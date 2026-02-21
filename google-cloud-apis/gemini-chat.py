import os
from pprint import pprint

from google import genai

project_id = os.getenv("GOOGLE_CLOUD_PROJCT")

client = genai.Client(vertexai=True, project=project_id, location="global")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in a few words",
)

print("Full Response:")
print("\n")
pprint(response)

print("\n" * 6)
print(response.text)
