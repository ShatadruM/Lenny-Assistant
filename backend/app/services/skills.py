def format_ship30_essay(topic: str, grounded_context: str) -> str:
    """
    Transforms grounded context into a formatted Ship 30 for 30 essay.
    """
    return (
        f"# Ship 30 for 30: {topic}\n\n"
        f"**The Hook:** Finding the right path in product growth is rarely intuitive. But the data reveals a pattern.\n\n"
        f"## The Core Philosophy\n"
        f"Based on Lenny's insights, the fundamental shift happens when you focus on user retention over raw acquisition.\n\n"
        f"### Key Principles\n"
        f"* **Focus on the micro-interactions.**\n"
        f"* **Listen to the silent churn.**\n"
        f"* **Iterate on the onboarding.**\n\n"
        f"## The Evidence\n"
        f"The transcripts highlight this clearly:\n"
        f"> {grounded_context[:500]}...\n\n"
        f"**The Takeaway:** Stop optimizing for the top of the funnel if your bucket is leaking. Fix the retention first."
    )

def get_ship30_tool_schema(provider: str):
    if provider == "cloud":
        return {
            "name": "generate_ship30_essay",
            "description": "Generates a highly formatted, skimmable 1,250-word essay using the Ship 30 for 30 framework.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The main topic of the essay"}
                },
                "required": ["topic"]
            }
        }
    else:
        return {
            "type": "function",
            "function": {
                "name": "generate_ship30_essay",
                "description": "Generates a highly formatted essay using the Ship 30 for 30 framework.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"}
                    },
                    "required": ["topic"]
                }
            }
        }