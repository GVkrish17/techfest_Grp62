import openai

# ✅ Set your OpenAI key here:
openai.api_key = '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'

# ✅ Test OpenAI API by sending a prompt
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how can you help me?"}
    ],
    max_tokens=50
)

# ✅ Print the response from OpenAI
print(response.choices[0].message['content'])