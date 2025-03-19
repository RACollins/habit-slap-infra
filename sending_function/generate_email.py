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
    action_plan: str,
    obstacles: str,
) -> Email:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    GENERAL_SYSTEM_PROMPT = PromptManager.get_prompt(
        "general_system_template",
    )
    user_prompt = PromptManager.get_prompt(
        "email_template",
        user_name=user_name,
        user_bio=user_bio,
        habit_details=habit_details,
        action_plan=action_plan,
        obstacles=obstacles,
    )
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.9,
        max_tokens=2000,
        response_format=Email,
    )

    return response.choices[0].message


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
    user_name = "John Doe"
    user_bio = "I'm a 30-year-old software engineer who loves to code and play guitar. I'm also a bit of a foodie and love to cook."
    habit_details = "I just want to lose weight, fast, I'm so fat. Help me please!"
    action_plan = "I'm going to eat less and exercise more."
    obstacles = "I'm too busy to exercise."

    email_address = "habitslaptest+user1@gmail.com"
    email_object = generate_email(
        user_name,
        user_bio,
        habit_details,
        action_plan,
        obstacles,
    )
    send_email(email_address, email_object.parsed)
    print(email_object.parsed)
