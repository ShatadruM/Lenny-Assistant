from sqlalchemy.ext.asyncio import AsyncSession
from app.services.retrieval import retrieve_context
from app.services.llm_factory import LLMFactory
from app.services.skills import format_ship30_essay, get_ship30_tool_schema
from app.schemas.chat import SourceNode
from app.core.logger import logger
import json

llm_factory = LLMFactory()

async def generate_essay(topic: str, context: str, provider: str, api_key: str, llm_factory: LLMFactory) -> str:
    essay_prompt = (
        f"You are an expert essayist using the Ship 30 for 30 framework.\n"
        f"Write a highly formatted, skimmable essay about '{topic}' based strictly on the following transcripts:\n\n"
        f"{context}\n\n"
        "Ensure you include:\n"
        "1. A strong Hook.\n"
        "2. The Core Philosophy.\n"
        "3. Key Principles.\n"
        "4. Evidence from the transcripts (using blockquotes and source links).\n"
        "5. A strong Takeaway.\n"
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

async def process_chat_message(message: str, provider: str, db: AsyncSession, generate_essay_flag: bool = False, api_key: str = None):
    # 1. Always ground the query first (RAG)
    context_nodes = await retrieve_context(message, db)
    
    if not context_nodes:
        return "I don't have any information about that in Lenny's transcripts.", []

    context_str = "\n\n".join([
        f"Source: {node.title} ({node.url})\nContent: {node.content_snippet}" 
        for node in context_nodes
    ])

    # 2. Short-circuit routing if the UI explicitly requested an essay
    if generate_essay_flag:
        essay_content = await generate_essay(message, context_str, provider, api_key, llm_factory)
        return essay_content, context_nodes

    # 3. Agent System Prompt
    system_prompt = (
        "You are 'The Lenny Growth Assistant'. You answer product and growth questions strictly using the provided transcripts. "
        "If the transcripts do not contain the answer, gracefully acknowledge that you lack the context. "
        "If the user asks for code, a UI component, or a layout, wrap your response in ```html ... ``` tags so the Artifact Viewer can render it. "
        "If the user asks for a flowchart, diagram, mindmap, or graph, strictly generate Mermaid.js code and wrap your response in ```mermaid ... ``` tags. "
        "Otherwise, respond in pure Markdown. NEVER output raw JSON unless the user specifically asks you to format the output as JSON. "
        "CRITICAL INSTRUCTION: ONLY use the `generate_ship30_essay` tool if the user EXPLICITLY asks you to write a 'Ship 30' or 'Ship 30 for 30' essay. Do NOT use this tool to answer general questions (like 'who is Lenny'). "
        "If you decide to use a tool, just call the tool directly. Do not explain your thought process or apologize."
        f"\n\nKNOWLEDGE BASE TRANSCRIPTS:\n{context_str}"
    )

    messages = [{"role": "user", "content": message}]
    tools = [get_ship30_tool_schema(provider)]

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
                        reply = await generate_essay(topic, context_str, provider, api_key, llm_factory)
                        return reply, context_nodes
                reply = next(block.text for block in response.content if block.type == "text")
            else:
                # OpenAI / Grok
                choice = response.choices[0]
                if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                    tool_call = choice.message.tool_calls[0]
                    if tool_call.function.name == "generate_ship30_essay":
                        try:
                            args = json.loads(tool_call.function.arguments)
                            topic = args.get("topic", message)
                        except:
                            topic = message
                        reply = await generate_essay(topic, context_str, provider, api_key, llm_factory)
                        return reply, context_nodes
                
                reply = choice.message.content

            # --- CLOUD SAFETY NET ---
            # If the cloud model hallucinated the tool call into the text response
            if "generate_ship30_essay" in reply and ("{" in reply or "```json" in reply):
                logger.info("Intercepted raw JSON tool hallucination from Cloud model.")
                return await generate_essay(message, context_str, provider, api_key, llm_factory), context_nodes

            return reply, context_nodes

        else:
            # Handle Local Ollama Execution
            response_msg = await llm_factory.call_local_agent(system_prompt, messages, tools)
            content = response_msg.get("content", "")
            
            # --- LOCAL SAFETY NET ---
            # If Ollama leaked the tool call into the raw text
            if "generate_ship30_essay" in content:
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
                    
                return await generate_essay(topic, context_str, provider, api_key, llm_factory), context_nodes
                
            if response_msg.get("tool_calls"):
                tool_call = response_msg["tool_calls"][0]["function"]
                if tool_call["name"] == "generate_ship30_essay":
                    try:
                        args = json.loads(tool_call["arguments"])
                        topic = args.get("topic", message)
                    except:
                        topic = message
                    return await generate_essay(topic, context_str, provider, api_key, llm_factory), context_nodes
            
            return content, context_nodes
            
            return content, context_nodes

    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        return f"An error occurred while communicating with the {provider} model: {str(e)}", context_nodes