import boto3
import os
import datetime
from boto3.dynamodb.conditions import Key
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")


def lambda_handler(event, context):
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    queue_url = os.environ["QUEUE_URL"]

    # Get time from EventBridge event
    event_time = event["time"]
    # EventBridge sends time in ISO format, convert to our format
    current_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ").strftime(
        "%Y-%m-%d %H:%M"
    )

    # Query DynamoDB using the GSI
    response = table.query(
        IndexName="NextEmailDateIndex",
        KeyConditionExpression=Key("next_email_date").eq(current_time),
    )

    # Process matching records
    records = response.get("Items", [])
    for record in records:
        message = {"email": record.get("email"), "goal": record.get("goal")}
        sqs.send_message(QueueUrl=queue_url, MessageBody=str(message))

    return {"statusCode": 200, "body": f"Processed {len(records)} records"}
