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
    You are a motivational coach who writes emails that motivate people to achieve their goals.
    
    The emails should be:
    - Motivational and supportive
    - Brief (2-3 paragraphs)
    - Don't sugar coat your advice
    - Include at leastone actionable tip
    
    Do not use any salutations or signatures - just the body text."""


### Define email format
class EmailBody(BaseModel):
    subject: str = Field(description="The subject of the email")
    previous_summary: str = Field(
        description="A summary of the previous emails if they exist, otherwise return an empty string"
    )
    body: str = Field(description="The body of the email")


@ell.complex(
    model="gpt-4o-mini",
    client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    temperature=1.1,
    max_tokens=2000,
    response_format=EmailBody,
)
def generate_email(goal: str, message_history: List[Message]) -> EmailBody:
    user_prompt = f"Summarise the emails in a few sentences. Then, write a motivational email to someone who has the following goal: {goal}"
    response = (
        [ell.system(GENERAL_SYSTEM_PROMPT)] + message_history + [ell.user(user_prompt)]
    )
    return response


def send_email(recipient: str, content: str):
    yag = yagmail.SMTP(
        user=os.getenv("GMAIL_USER"), password=os.getenv("GMAIL_PASSWORD")
    )
    if content.previous_summary == "":
        main_text = (
            f"This is the first email on your Habit Slap journey!\n\n{content.body}"
        )
    else:
        main_text = f"{content.previous_summary}\n\nHere is the next email I've written to you. I hope it helps you achieve your goal!\n\n{content.body}"
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
