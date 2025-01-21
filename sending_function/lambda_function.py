import json
import os
import yagmail
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def generate_email(goal: str) -> str:
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4-0125-preview",  # Using latest GPT-4 Turbo
        temperature=0.7
    )
    
    # Create the prompt template
    template = """You are a motivational coach helping people achieve their goals.
    Write a short, encouraging email to someone who has the following goal: {goal}
    
    The email should be:
    - Motivational and supportive
    - Brief (2-3 paragraphs)
    - Personal and friendly
    - Include one actionable tip
    
    Do not use any salutations or signatures - just the body text."""

    prompt = ChatPromptTemplate.from_template(template)
    
    # Generate the email content
    chain = prompt | llm
    response = chain.invoke({"goal": goal})
    
    return response.content

def send_email(recipient: str, content: str):
    # Initialize yagmail
    yag = yagmail.SMTP(
        user=os.environ["GMAIL_USER"],
        password=os.environ["GMAIL_PASSWORD"]
    )
    
    # Send the email
    yag.send(
        to=recipient,
        subject="Your Daily Motivation 💪",
        contents=content
    )

def lambda_handler(event, context):
    try:
        # Process SQS messages
        for record in event["Records"]:
            # Parse message body
            message = eval(record["body"])
            email = message["email"]
            goal = message["goal"]
            
            # Generate email content
            email_content = generate_email(goal)
            
            # Send email
            send_email(email, email_content)
            
        return {
            "statusCode": 200,
            "body": f"Successfully processed {len(event['Records'])} messages"
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e 