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
            print(
                f"Processing message for email: {message["email"]} with habit_details: {message["habit_details"]}"
            )

            # Generate and send email
            email_object = generate_email(
                user_name=message["name"],
                user_bio=message["bio"],
                habit_details=message["habit_details"],
                action_plan=message["action_plan"],
                obstacles=message["obstacles"],
            )
            send_email(message["email"], email_object.data)

            # Get current record to find next_email_date
            current_record = table.get_item(Key={"email": message["email"]})
            current_next_date = current_record["Item"]["next_email_date"]

            # Calculate next email date (1 day from current next_email_date)
            next_date = (
                datetime.fromisoformat(current_next_date) + timedelta(days=1)
            ).isoformat()

            # Update DynamoDB record
            table.update_item(
                Key={"email": message["email"]},
                UpdateExpression="SET next_email_date = :next_date",
                ExpressionAttributeValues={":next_date": next_date},
            )
            print(f"Updated next_email_date for {message["email"]} to {next_date}")

        return {
            "statusCode": 200,
            "body": f"Successfully processed {len(event['Records'])} messages",
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
