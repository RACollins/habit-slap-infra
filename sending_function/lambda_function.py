from generate_email import generate_email, send_email

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
            "body": f"Successfully processed {len(event['Records'])} messages",
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
