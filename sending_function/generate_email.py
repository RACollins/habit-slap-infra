import os
import yagmail  # type: ignore
from openai import OpenAI  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from dotenv import load_dotenv
from prompts.prompt_manager import PromptManager

# Load environment variables from .env file
load_dotenv()


### Define email format
class Email(BaseModel):
    subject: str = Field(description="The subject of the email")
    body: str = Field(description="The body of the email")


def generate_email(
    user_name: str,
    user_bio: str,
    habit_details: str,
    time_frame: str,
    formality: int,
    assertiveness: int,
    intensity: int,
) -> Email:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    message_history = []
    GENERAL_SYSTEM_PROMPT = PromptManager.get_prompt(
        "general_system_template",
        min_actionable_tips=1,
        previous_email_exists=bool(message_history),
    )
    user_prompt = PromptManager.get_prompt(
        "goal_template", goal=goal, previous_email_exists=bool(message_history)
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content


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
