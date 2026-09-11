from google.adk import Agent

root_agent = Agent(
    name="echo_agent",
    model="gemini-3.5-flash",
    description="A parrot agent that only repeats user input.",
    instruction="You are a parrot agent that only repeats user input. Do not provide any additional information or context. Only repeat what the user says.",
)