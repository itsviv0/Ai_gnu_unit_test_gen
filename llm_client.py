import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Model setup
endpoint = "https://models.github.ai/inference"
model = "xai/grok-3"
token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise EnvironmentError("GITHUB_TOKEN environment variable is not set")

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def llm_call(prompt: str) -> str:
    messages = [
        SystemMessage("You are a helpful assistant."),
        UserMessage(prompt)
    ]
    try:
        response = client.complete(
            messages=messages,
            temperature=0.7,
            top_p=0.95,
            model=model
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error calling LLM:", e)
        return ""

def refactor_main_code(code: str) -> str:
    prompt = f"""
    Refactor this main function for clarity and maintainability without changing its logic or behavior.
    Return a complete C++ file. Do not modify global structure unless absolutely necessary.

    ```cpp
    {code}
    ```
    """
    return llm_call(prompt)

def generate_tests_for_main(refactored_code: str) -> str:
    prompt = f"""
    Generate Google Test unit tests for the following C++ main function code.
    Include appropriate headers. Avoid test duplication and follow best practices.
    {refactored_code}
    """
    return llm_call(prompt)