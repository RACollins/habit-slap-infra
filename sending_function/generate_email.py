import os
import yagmail  # type: ignore
from langchain.chat_models import init_chat_model  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


### Define email format
class Email(BaseModel):
    subject: str = Field(description="The subject of the email")
    body: str = Field(description="The body of the email")


def setup_chain():
    system_prompt = f"""
    You are a motivational coach who helps people achieve their goals no matter what.
    You write emails that motivate people to achieve their goals.
    
    The emails should be:
    - Motivational and supportive
    - Brief (2-3 paragraphs)
    - Don't sugar coat your advice
    - Include one actionable tip
    
    Do not use any salutations or signatures - just the body text."""

    user_prompt_template = f"""
    Write a motivational email to someone who has the following goal: {goal}
    """
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", user_prompt_template)]
    )

    llm = init_chat_model(
        "gpt-4o-mini",
        model_provider="openai",
        configurable_fields=["api_key"],
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=1000,
    ).with_structured_output(Email)

    chain = prompt | llm
    return chain


def generate_email(goal: str) -> Email:
    chain = setup_chain()
    response = chain.invoke({"goal": goal})
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
    email_object = generate_email(goal)
    email_address = "habitslaptest+user1@gmail.com"
    send_email(email_address, email_object)
