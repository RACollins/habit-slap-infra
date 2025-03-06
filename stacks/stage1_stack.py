from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_lambda_event_sources as lambda_event_sources,
    Duration,
)
from constructs import Construct
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Stage1Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SQS Queue
        queue = sqs.Queue(
            self,
            "HabitSlapQueue",
            queue_name="habit-slap-queue",
            visibility_timeout=Duration.minutes(5),  # Match Lambda timeout
        )

        # Create Checking Lambda function
        checking_function = lambda_.Function(
            self,
            "HabitSlapCheckingFunction",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("checking_function"),
            timeout=Duration.minutes(1),
            environment={
                "QUEUE_URL": queue.queue_url,
                "TABLE_NAME": "habit-slap-users-dev",
            },
        )

        # Grant DynamoDB permissions
        checking_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query", "dynamodb:Scan", "dynamodb:GetItem"],
                resources=[
                    f"arn:aws:dynamodb:*:*:table/habit-slap-users-dev",
                    f"arn:aws:dynamodb:*:*:table/habit-slap-users-dev/index/*",
                ],
            )
        )

        # Grant SQS permissions
        queue.grant_send_messages(checking_function)

        # Create EventBridge rule
        rule = events.Rule(
            self,
            "HabitSlapScheduleRule",
            # Run every minute
            schedule=events.Schedule.cron(minute="*"),
        )
        rule.add_target(targets.LambdaFunction(checking_function))

        # Create Lambda Layer for sending function
        layer = lambda_.LayerVersion(
            self,
            "HabitSlapLayer",
            code=lambda_.Code.from_asset("lambda_layer/lambda_layer.zip"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_13],
            description="Layer containing OpenAI and email dependencies",
        )

        # Create Sending Lambda function
        sending_function = lambda_.Function(
            self,
            "HabitSlapSendingFunction",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("sending_function"),
            timeout=Duration.minutes(1),
            memory_size=128,  # <- Increase memory if necessary
            layers=[layer],
            environment={
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
                "GMAIL_USER": os.getenv("GMAIL_USER", ""),
                "GMAIL_PASSWORD": os.getenv("GMAIL_PASSWORD", ""),
                "TABLE_NAME": "habit-slap-users-dev",
            },
        )

        # Add DynamoDB update permissions to sending function
        sending_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:UpdateItem", "dynamodb:GetItem"],
                resources=[f"arn:aws:dynamodb:*:*:table/habit-slap-users-dev"],
            )
        )

        # Add SQS trigger to Sending Lambda with batch size 1
        sending_function.add_event_source(
            lambda_event_sources.SqsEventSource(
                queue,
                batch_size=1,  # Process one message at a time
                max_batching_window=Duration.seconds(0),  # Don't wait to batch messages
            )
        )
