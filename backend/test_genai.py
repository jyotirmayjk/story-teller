from google import genai

client = genai.Client(
    vertexai=True,
    location="us-central1",
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain what a tiger is to a 3 year old."
)

print(response.text)
