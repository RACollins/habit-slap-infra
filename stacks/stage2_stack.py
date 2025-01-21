from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    Duration,
)
from constructs import Construct
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Stage2Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SQS Queue
        queue = sqs.Queue(
            self, 
            "HabitSlapQueue",
            queue_name="habit-slap-queue",
            visibility_timeout=Duration.minutes(5)  # Match Lambda timeout
        )

        # Create Lambda Layer
        layer = lambda_.LayerVersion(
            self,
            "HabitSlapLayer",
            code=lambda_.Code.from_asset("sending_function/lambda_layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_13],
            description="Layer containing OpenAI, Langchain, and email dependencies"
        )

        # Create Lambda function
        sending_function = lambda_.Function(
            self,
            "HabitSlapSendingFunction",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("sending_function"),
            timeout=Duration.minutes(5),
            layers=[layer],
            environment={
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
                "GMAIL_USER": os.getenv("GMAIL_USER", ""),
                "GMAIL_PASSWORD": os.getenv("GMAIL_PASSWORD", "")
            },
        )

        # Add SQS trigger to Lambda
        sending_function.add_event_source(
            lambda_event_sources.SqsEventSource(queue)
        ) 