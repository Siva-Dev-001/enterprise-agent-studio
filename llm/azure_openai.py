from openai import AzureOpenAI
import os

client=AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_KEY"),api_version="2024-02-15-preview",azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))

def call_llm(prompt):
    response=client.chat.completions.create(model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),messages=[{"role":"user","content":prompt}])
    return response.choices[0].message.content