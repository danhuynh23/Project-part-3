import openai

import os 

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable is not set!")

completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)