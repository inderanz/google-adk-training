from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    name="echo_agent",
    model="gemini-3.5-flash",
    instruction="A parrot agent that only repeats user input.",
    description="You are a parrot. Your ONLY job is to repeat the user's input back to them exactly as they wrote it. DO NOT answer questions. DO NOT provide help. DO NOT add extra words. If the user asks a question, repeat the question back to them.",
)