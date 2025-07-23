import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from utils.utils import clean_llm_cpp_output

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
    messages = [SystemMessage("You are a helpful assistant."), UserMessage(prompt)]
    try:
        response = client.complete(
            messages=messages, temperature=0.7, top_p=0.95, model=model
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
    response = llm_call(prompt)
    return clean_llm_cpp_output(response)


def generate_tests_with_yaml(code: str, yaml_rules: str) -> str:
    prompt = f"""
        You are a C++ unit test generator using Google Test.

        Strictly follow the rules below defined in YAML format. Use Google Test framework unless specified otherwise.
        Do not include duplicate tests or unnecessary includes. Generate Google Test unit tests for the following C++ main function code.
        - No optimization flags.
        - Compatible with `-fprofile-arcs -ftest-coverage`.
        - Avoid dynamic code generation or runtime hacks.
        - Use Google Test framework.
        - Include appropriate headers. 
        - Avoid test duplication and follow best practices.

        YAML Rules:
        ```yaml
        {yaml_rules}
        ```

        C++ Code to test:
        {code}
        Generate the complete test file.
        """
    response = llm_call(prompt)
    return clean_llm_cpp_output(response)


def refine_generated_tests(test_code: str, yaml_rules: str) -> str:
    prompt = f"""
    You are a C++ test assistant. Your job is to improve existing unit tests.
    Follow these STRICT rules in YAML format:
    
    ```yaml
    {yaml_rules}
    ```
    Here is the existing test file. Improve it by:
    - Removing any duplicated or redundant test cases
    - Adding any missing includes or relevant libraries
    - Ensuring all tests are clear and concise
    - Fixing bad naming or formatting
    - Keeping the test framework and logic intacT

    ```
    {test_code}
    ```
    Return the improved test file as clean C++ code.
    """
    response = llm_call(prompt)
    return clean_llm_cpp_output(response)
