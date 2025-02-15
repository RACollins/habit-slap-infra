import os
import yagmail  # type: ignore
import ell  # type: ignore
from ell import Message  # type: ignore
from openai import OpenAI  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from typing import List
from dotenv import load_dotenv
from prompts.prompt_manager import PromptManager

# Load environment variables from .env file
load_dotenv()


### Define email format
class Email(BaseModel):
    subject: str = Field(description="The subject of the email")
    body: str = Field(description="The body of the email")


@ell.complex(
    model="gpt-4o-mini",
    client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    temperature=1.0,
    max_tokens=2000,
    response_format=Email,
)
def generate_email(goal: str, message_history: List[Message]) -> Email:
    GENERAL_SYSTEM_PROMPT = PromptManager.get_prompt(
        "general_system_template",
        min_actionable_tips=1,
        previous_email_exists=bool(message_history),
    )
    user_prompt = PromptManager.get_prompt(
        "goal_template", goal=goal, previous_email_exists=bool(message_history)
    )
    response = (
        [ell.system(GENERAL_SYSTEM_PROMPT)] + message_history + [ell.user(user_prompt)]
    )
    return response


def send_email(recipient: str, content: str):
    yag = yagmail.SMTP(
        user=os.getenv("GMAIL_USER"), password=os.getenv("GMAIL_PASSWORD")
    )
    yag.send(
        to=recipient,
        subject=f"{content.subject} 💪",
        contents=content.body,
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
