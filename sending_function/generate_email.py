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


def get_formality_level(formality: int) -> str:
    if formality < 25:
        return "very friendly and casual"
    elif formality < 50:
        return "somewhat friendly"
    elif formality < 75:
        return "professional but approachable"
    else:
        return "formal and professional"


def get_assertiveness_level(assertiveness: int) -> str:
    if assertiveness < 25:
        return "gentle and encouraging"
    elif assertiveness < 50:
        return "moderately assertive"
    elif assertiveness < 75:
        return "firm and direct"
    else:
        return "very assertive and challenging"


def get_intensity_level(intensity: int) -> str:
    if intensity < 25:
        return "calm and measured"
    elif intensity < 50:
        return "moderately energetic"
    elif intensity < 75:
        return "highly energetic and passionate"
    else:
        return "extremely intense and powerful"


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
    # Convert string inputs to integers if they aren't already
    formality = int(formality)
    assertiveness = int(assertiveness)
    intensity = int(intensity)
    
    formality_level = get_formality_level(formality)
    assertiveness_level = get_assertiveness_level(assertiveness)
    intensity_level = get_intensity_level(intensity)
    GENERAL_SYSTEM_PROMPT = PromptManager.get_prompt(
        "general_system_template",
    )
    user_prompt = PromptManager.get_prompt(
        "email_template",
        user_name=user_name,
        user_bio=user_bio,
        habit_details=habit_details,
        time_frame=time_frame,
        formality_level=formality_level,
        assertiveness_level=assertiveness_level,
        intensity_level=intensity_level,
    )
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
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
    time_frame = "1 month"
    formality = 90
    assertiveness = 10
    intensity = 10

    email_address = "habitslaptest+user1@gmail.com"
    email_object = generate_email(
        user_name,
        user_bio,
        habit_details,
        time_frame,
        formality,
        assertiveness,
        intensity,
    )
    send_email(email_address, email_object.parsed)
    print(email_object.parsed)
