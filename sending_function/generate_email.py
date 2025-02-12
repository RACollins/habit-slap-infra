import os
import yagmail  # type: ignore
import ell  # type: ignore
from ell import Message  # type: ignore
from openai import OpenAI  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GENERAL_SYSTEM_PROMPT = """
    You are a motivational coach who helps people achieve their goals no matter what.
    You write emails that motivate people to achieve their goals.
    
    The emails should be:
    - Motivational and supportive
    - Brief (2-3 paragraphs)
    - Don't sugar coat your advice
    - Include one actionable tip
    
    Do not use any salutations or signatures - just the body text."""


### Define email format
class EmailBody(BaseModel):
    subject: str = Field(description="The subject of the email")
    previous_summary: str = Field(description="A summary of the previous emails")
    body: str = Field(description="The body of the email")


@ell.complex(
    model="gpt-4o-mini",
    client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    temperature=1.1,
    max_tokens=2000,
    response_format=EmailBody,
)
def generate_email(goal: str, message_history: List[Message]) -> EmailBody:
    response = [
        ell.system(GENERAL_SYSTEM_PROMPT),
        ell.user(
            f"Write a motivational email to someone who has the following goal: {goal}"
        ),
    ] + message_history
    return response


def send_email(recipient: str, content: str):
    yag = yagmail.SMTP(
        user=os.getenv("GMAIL_USER"), password=os.getenv("GMAIL_PASSWORD")
    )
    if content.previous_summary:
        main_text = f"{content.previous_summary}\n\n{content.body}"
    else:
        main_text = content.body
    yag.send(
        to=recipient,
        subject=f"{content.subject} 💪",
        contents=main_text,
    )


# Test the function if running this file directly
if __name__ == "__main__":
    goal = "I just want to lose weight, fast, I'm so fat. Help me please!"
    email_address = "habitslaptest+user1@gmail.com"
    message_history = []
    first_email_object = generate_email(goal, message_history)
    send_email(email_address, first_email_object.parsed)
    message_history.append(first_email_object)
    second_email_object = generate_email(goal, message_history)
    send_email(email_address, second_email_object.parsed)

    print(first_email_object.parsed)
    print("--------------------------------")
    print(second_email_object.parsed)
