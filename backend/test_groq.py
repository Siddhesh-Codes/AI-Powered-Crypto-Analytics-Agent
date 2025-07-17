import os
os.environ['GROQ_API_KEY'] = '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'

try:
    from groq import Groq
    client = Groq(api_key=os.environ['GROQ_API_KEY'])
    
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful crypto expert."},
            {"role": "user", "content": "What is Bitcoin?"}
        ],
        temperature=0.7,
        max_tokens=200
    )
    
    print("✅ Groq API is working!")
    print("Response:", response.choices[0].message.content)
    
except Exception as e:
    print(f"❌ Groq API Error: {e}")
