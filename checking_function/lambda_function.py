import boto3  # type: ignore
import os
from boto3.dynamodb.conditions import Key  # type: ignore

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")


def lambda_handler(event, context):
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    queue_url = os.environ["QUEUE_URL"]

    # Get time from EventBridge event and convert format
    current_time = event["time"].replace("Z", "+00:00")
    print("Current time:", current_time)

    # Query DynamoDB using the GSI
    response = table.query(
        IndexName="NextEmailDateIndex",
        KeyConditionExpression=Key("next_email_date").eq(current_time)
    )

    # Process matching records
    records = response.get("Items", [])
    for record in records:
        message = {"email": record.get("email"), "goal": record.get("goal")}
        sqs.send_message(QueueUrl=queue_url, MessageBody=str(message))

    return {"statusCode": 200, "body": f"Processed {len(records)} records"}
