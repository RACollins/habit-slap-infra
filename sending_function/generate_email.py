import os
import yagmail  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from pydantic_ai import Agent  # type: ignore
from pydantic_ai.models.openai import OpenAIModel  # type: ignore
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool  # type: ignore
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
    model = OpenAIModel("gpt-4o-mini")
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
    agent = Agent(
        model=model,
        result_type=Email,
        system_prompt=(GENERAL_SYSTEM_PROMPT),
        tools=[duckduckgo_search_tool()],
    )
    response = agent.run_sync(
        user_prompt,
        model_settings={"temperature": 1.1, "max_tokens": 2000},
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


### Test the function if running this file directly
if __name__ == "__main__":
    user_name = "Kana Collins"
    user_bio = "I'm a 30-year-old recruiter who loves to sew. I'm also a huge fan of the TV show Stranger Things."
    habit_details = "I hate my job and want to quit."
    action_plan = "I'm going to apply for a new job next week."
    obstacles = "Most jobs I've applied to have been: low pay, no benefits, and no remote work."

    email_address = "habitslaptest+user1@gmail.com"
    email_object = generate_email(
        user_name,
        user_bio,
        habit_details,
        action_plan,
        obstacles,
    )
    send_email(email_address, email_object.data)
    print(email_object)
