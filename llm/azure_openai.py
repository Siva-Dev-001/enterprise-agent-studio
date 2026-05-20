from openai import AzureOpenAI, OpenAI
import os
from dotenv import load_dotenv
# client=AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_KEY"),api_version="2024-02-15-preview",azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))

# def call_llm(prompt):
#     response=client.chat.completions.create(model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),messages=[{"role":"user","content":prompt}])
#     return response.choices[0].message.content
load_dotenv()


def call_llm(prompt: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-5.3-chat-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# if __name__ == "__main__":
#     print(call_llm("What is a transformer model?"))