from sqlalchemy.ext.asyncio import AsyncSession
from app.services.retrieval import retrieve_context
from app.services.llm_factory import LLMFactory
from app.services.skills import format_ship30_essay, get_ship30_tool_schema
from app.schemas.chat import SourceNode
from app.core.logger import logger
import json
import httpx
from bs4 import BeautifulSoup

llm_factory = LLMFactory()

async def fetch_url_content(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text and collapse whitespace
            text = ' '.join(soup.stripped_strings)
            return text[:10000] # Limit to avoid context window explosion
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ""

async def generate_essay(topic: str, context: str, provider: str, api_key: str, llm_factory: LLMFactory, principles_source_url: str = None) -> str:
    principles_text = ""
    if principles_source_url:
        scraped_text = await fetch_url_content(principles_source_url)
        if scraped_text:
            principles_text = (
                f"I have scraped the following source for writing principles: {principles_source_url}\n"
                f"Source Content: {scraped_text}\n"
                "Please analyze this source content, identify the key writing principles, and apply them closely while writing this essay.\n"
            )

    if not principles_text:
        principles_text = (
            "Ensure you include:\n"
            "1. A strong Hook.\n"
            "2. The Core Philosophy.\n"
            "3. Key Principles.\n"
            "4. Evidence from the transcripts (using blockquotes and source links).\n"
            "5. A strong Takeaway.\n"
        )

    essay_prompt = (
        f"You are an expert essayist using the Ship 30 for 30 framework.\n"
        f"Write a highly formatted, skimmable essay about '{topic}' based strictly on the following transcripts:\n\n"
        f"{context}\n\n"
        f"{principles_text}"
        f"Format it in Markdown, starting with `# Ship 30 for 30: {topic}`."
    )
    
    messages = [{"role": "user", "content": f"Please write the essay on {topic}."}]
    
    try:
        if provider in ["anthropic", "openai", "groq"]:
            response = await llm_factory.call_cloud_agent(essay_prompt, messages, [], provider=provider, api_key=api_key)
            if provider == "anthropic":
                reply = next(block.text for block in response.content if block.type == "text")
            else:
                reply = response.choices[0].message.content
            return reply
        else:
            response_msg = await llm_factory.call_local_agent(essay_prompt, messages, [])
            return response_msg.get("content", "")
    except Exception as e:
        logger.error(f"Failed to generate essay dynamically: {e}")
        return f"# Error generating essay\n\nThere was a problem generating the dynamic essay: {e}"

async def process_chat_message(message: str, provider: str, db: AsyncSession, generate_essay_flag: bool = False, api_key: str = None, chat_history: list = None):
    # 1. Always ground the query first (RAG)
    rag_failed = False
    try:
        context_nodes = await retrieve_context(message, db)
    except httpx.ConnectError:
        logger.warning("Ollama connection failed. Skipping RAG.")
        context_nodes = []
        rag_failed = True
        
    def append_warning(text: str) -> str:
        if rag_failed:
            return text + "\n\n> ⚠️ **RAG Disabled:** The local Ollama instance is unreachable. If you are using the deployed version, RAG will not work unless you set it up locally! The AI answered using its general knowledge."
        return text
    
    # We do NOT short-circuit here if context_nodes is empty.
    # This allows the agent to respond to greetings ("Hi") or follow-up questions
    # that rely on conversational memory instead of direct database hits.
    context_str = ""
    if context_nodes:
        context_str = "\n\n".join([
            f"Source: {node.title} ({node.url})\nContent: {node.content_snippet}" 
            for node in context_nodes
        ])

    # 2. Agent System Prompt
    system_prompt = (
        "You are 'The Lenny Growth Assistant'. You answer product and growth questions strictly using the provided transcripts and conversation history. "
        "If you do not know the answer, gracefully acknowledge it. Be conversational and polite (e.g. say hello back if greeted). "
        "If the user asks for code, a UI component, or a layout, wrap your response in ```html ... ``` tags so the Artifact Viewer can render it. "
        "If the user asks for a flowchart, diagram, mindmap, or graph, strictly generate Mermaid.js code and wrap your response in ```mermaid ... ``` tags. "
        "Otherwise, respond in pure Markdown. NEVER output raw JSON unless the user specifically asks you to format the output as JSON."
    )

    tools = []
    if generate_essay_flag:
        tools = [get_ship30_tool_schema(provider)]
        system_prompt += "\n\nCRITICAL INSTRUCTION: The user has requested an essay. You MUST use the `generate_ship30_essay` tool to fulfill this request. If the user provided a URL in their prompt, pass it to the tool."

    messages = chat_history or []
    # Note: user's latest message is already appended to the chat_history in api/chat.py!
    if not chat_history:
        messages = [{"role": "user", "content": message}]

    # 3. Inject context directly into the final user message to ensure all models respect it
    if context_str:
        # Find the last user message and append the context
        for i in range(len(messages) - 1, -1, -1):
            if messages[i]["role"] == "user":
                messages[i]["content"] = f"{messages[i]['content']}\n\n--- KNOWLEDGE BASE TRANSCRIPTS ---\n{context_str}\n----------------------------------\nPlease use the above transcripts to answer the question."
                break

    try:
        # 4. Execute LLM Call
        if provider in ["anthropic", "openai", "groq"]:
            response = await llm_factory.call_cloud_agent(system_prompt, messages, tools, provider=provider, api_key=api_key)
            
            # Since OpenAI and Anthropic tool use structures differ, we handle them based on provider
            if provider == "anthropic":
                if hasattr(response, 'stop_reason') and response.stop_reason == "tool_use":
                    tool_call = next(block for block in response.content if block.type == "tool_use")
                    if tool_call.name == "generate_ship30_essay":
                        topic = tool_call.input.get("topic", message)
                        principles_url = tool_call.input.get("principles_source_url")
                        reply = await generate_essay(topic, context_str, provider, api_key, llm_factory, principles_source_url=principles_url)
                        return append_warning(reply), context_nodes
                reply = next(block.text for block in response.content if block.type == "text")
            else:
                # OpenAI / Grok
                choice = response.choices[0]
                if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                    tool_call = choice.message.tool_calls[0]
                    if tool_call.function.name == "generate_ship30_essay":
                        principles_url = None
                        try:
                            args = json.loads(tool_call.function.arguments)
                            topic = args.get("topic", message)
                            principles_url = args.get("principles_source_url")
                        except:
                            topic = message
                        reply = await generate_essay(topic, context_str, provider, api_key, llm_factory, principles_source_url=principles_url)
                        return append_warning(reply), context_nodes
                
                reply = choice.message.content

            # --- CLOUD SAFETY NET ---
            # If the cloud model hallucinated the tool call into the text response
            if generate_essay_flag and "generate_ship30_essay" in reply and ("{" in reply or "```json" in reply):
                logger.info("Intercepted raw JSON tool hallucination from Cloud model.")
                fallback_reply = await generate_essay(message, context_str, provider, api_key, llm_factory)
                return append_warning(fallback_reply), context_nodes

            # If the user wanted an essay but the model ignored the tool instruction
            if generate_essay_flag and "generate_ship30_essay" not in reply:
                logger.info("Model ignored tool instruction, falling back to direct generation.")
                fallback_reply = await generate_essay(message, context_str, provider, api_key, llm_factory)
                return append_warning(fallback_reply), context_nodes

            return append_warning(reply), context_nodes

        else:
            # Handle Local Ollama Execution
            response_msg = await llm_factory.call_local_agent(system_prompt, messages, tools)
            content = response_msg.get("content", "")
            
            # --- LOCAL SAFETY NET ---
            # If Ollama leaked the tool call into the raw text
            if generate_essay_flag and "generate_ship30_essay" in content:
                logger.info("Intercepted raw JSON tool hallucination from Ollama.")
                
                # Attempt to extract the topic from the hallucinated JSON if possible
                topic = message
                try:
                    # Find the first JSON-like structure
                    if "{" in content and "}" in content:
                        json_str = content[content.find("{"):content.rfind("}")+1]
                        parsed = json.loads(json_str)
                        if "parameters" in parsed and "topic" in parsed["parameters"]:
                            topic = parsed["parameters"]["topic"]
                        elif "topic" in parsed:
                            topic = parsed["topic"]
                except:
                    pass
                    
                fallback_reply = await generate_essay(topic, context_str, provider, api_key, llm_factory)
                return append_warning(fallback_reply), context_nodes
                
            if response_msg.get("tool_calls"):
                tool_call = response_msg["tool_calls"][0]["function"]
                if tool_call["name"] == "generate_ship30_essay":
                    try:
                        args = json.loads(tool_call["arguments"])
                        topic = args.get("topic", message)
                    except:
                        topic = message
                    fallback_reply = await generate_essay(topic, context_str, provider, api_key, llm_factory)
                    return append_warning(fallback_reply), context_nodes
            
            # If the user wanted an essay but the local model ignored the tool instruction
            if generate_essay_flag:
                logger.info("Local model ignored tool instruction, falling back to direct generation.")
                fallback_reply = await generate_essay(message, context_str, provider, api_key, llm_factory)
                return append_warning(fallback_reply), context_nodes
                
            return append_warning(content), context_nodes

    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        return f"An error occurred while communicating with the {provider} model: {str(e)}", context_nodes