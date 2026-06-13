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
You are an AI Hiring Manager.

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
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        return json.loads(content)

    except:

        return {
            "match_score": 0,
            "reasoning": "AI failed"
        }