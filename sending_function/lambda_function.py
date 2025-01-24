from generate_email import generate_email, send_email


def lambda_handler(event, context):
    print(f"Event: {event}")
    try:
        for record in event["Records"]:
            message = eval(record["body"])
            email = message["email"]
            goal = message["goal"]
            print(f"Processing message for email: {email} with goal: {goal}")

            email_content = generate_email(goal)
            send_email(email, email_content)

        return {
            "statusCode": 200,
            "body": f"Successfully processed {len(event['Records'])} messages",
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
