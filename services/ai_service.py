import os
import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def analyze_resume(resume_text, job_description):

    prompt = f"""
You are an expert AI Hiring Manager.

Analyze the resume against the job description.

Return ONLY valid JSON.

Format:
{{
    "match_score": 0,
    "reasoning": ""
}}

Job Description:
{job_description}

Resume:
{resume_text[:3000]}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        print("RAW AI RESPONSE:")
        print(content)

        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        return json.loads(content)

    except Exception as e:

        print("AI ERROR:", str(e))

        return {
            "match_score": 0,
            "reasoning": f"AI Error: {str(e)}"
        }
    print("API KEY FOUND:", os.getenv("GROQ_API_KEY") is not None)