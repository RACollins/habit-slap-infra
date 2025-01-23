import os
import yagmail # type: ignore
from openai import OpenAI # type: ignore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_email(goal: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are a tough motivational coach helping people achieve their goals no matter what.
    Write a short, encouraging email to someone who has the following goal: {goal}
    
    The email should be:
    - Motivational and supportive
    - Brief (2-3 paragraphs)
    - Don't sugar coat your advice
    - Include one actionable tip
    
    Do not use any salutations or signatures - just the body text."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a motivational coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def send_email(recipient: str, content: str):
    yag = yagmail.SMTP(
        user=os.getenv("GMAIL_USER"),
        password=os.getenv("GMAIL_PASSWORD")
    )
    yag.send(
        to=recipient,
        subject="Your Daily Motivation 💪",
        contents=content
    )

# Test the function if running this file directly
if __name__ == "__main__":
    goal = "I just want to lose weight, fast, I'm so fat. Help me please!"
    body = generate_email(goal)
    email = "habitslaptest+user1@gmail.com"
    send_email(email, body)