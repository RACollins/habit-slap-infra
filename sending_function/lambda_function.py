import boto3  # type: ignore
import os
from datetime import datetime, timedelta
from generate_email import generate_email, send_email

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    print(f"Event: {event}")
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    try:
        for record in event["Records"]:
            message = eval(record["body"])
            email = message["email"]
            goal = message["goal"]
            print(f"Processing message for email: {email} with goal: {goal}")

            # Generate and send email
            email_content = generate_email(goal)
            send_email(email, email_content.parsed)

            # Get current record to find next_email_date
            current_record = table.get_item(Key={"email": email})
            current_next_date = current_record["Item"]["next_email_date"]

            # Calculate next email date (1 week from current next_email_date)
            next_date = (
                datetime.fromisoformat(current_next_date) + timedelta(days=7)
            ).isoformat()

            # Update DynamoDB record
            table.update_item(
                Key={"email": email},
                UpdateExpression="SET next_email_date = :next_date",
                ExpressionAttributeValues={":next_date": next_date},
            )
            print(f"Updated next_email_date for {email} to {next_date}")

        return {
            "statusCode": 200,
            "body": f"Successfully processed {len(event['Records'])} messages",
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
