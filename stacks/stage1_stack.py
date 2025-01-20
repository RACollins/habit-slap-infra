from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_sqs as sqs,
    aws_iam as iam,
    Duration,
)
from constructs import Construct


class Stage1Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SQS Queue
        queue = sqs.Queue(self, "HabitSlapQueue", queue_name="habit-slap-queue")

        # Create Lambda function
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
                    f"arn:aws:dynamodb:*:*:table/habit-slap-users-dev/index/*"
                ],
            )
        )

        # Grant SQS permissions
        queue.grant_send_messages(checking_function)

        # Create EventBridge rule
        rule = events.Rule(
            self,
            "HabitSlapScheduleRule",
            # Run at minute 0, 5, ... , 55 of every hour
            schedule=events.Schedule.cron(minute="0/5"),
        )
        rule.add_target(targets.LambdaFunction(checking_function))
