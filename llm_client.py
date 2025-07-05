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


def generate_tests_with_yaml(code: str, yaml_rules: str) -> str:
    prompt = f"""
        You are a C++ unit test generator.

        Strictly follow the rules below defined in YAML format. Use Google Test framework unless specified otherwise.
        Do not include duplicate tests or unnecessary includes. Generate Google Test unit tests for the following C++ main function code.
        Include appropriate headers. Avoid test duplication and follow best practices.
        {code}

        YAML Rules:
        ```yaml
        {yaml_rules}
        ```

        C++ Code to test:
        {code}
        Generate the complete test file.
        """
    return llm_call(prompt)