import os
import yagmail # type: ignore
from openai import OpenAI # type: ignore
from pydantic import BaseModel # type: ignore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

### Define email format
class Email(BaseModel):
    subject: str
    body: str


def generate_email(goal: str) -> Email:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""
    Write a short, encouraging email to someone who has the following goal: {goal}
    
    The email should be:
    - Motivational and supportive
    - Brief (2-3 paragraphs)
    - Don't sugar coat your advice
    - Include one actionable tip
    
    Do not use any salutations or signatures - just the body text."""

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a tough motivational coach who helps people achieve their goals no matter what."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000,
        response_format=Email
    )
    
    return response.choices[0].message.parsed

def send_email(recipient: str, content: str):
    yag = yagmail.SMTP(
        user=os.getenv("GMAIL_USER"),
        password=os.getenv("GMAIL_PASSWORD")
    )
    yag.send(
        to=recipient,
        subject=f"{content.subject} 💪",
        contents=content.body
    )

# Test the function if running this file directly
if __name__ == "__main__":
    goal = "I just want to lose weight, fast, I'm so fat. Help me please!"
    email_object = generate_email(goal)
    email_address = "habitslaptest+user1@gmail.com"
    send_email(email_address, email_object)