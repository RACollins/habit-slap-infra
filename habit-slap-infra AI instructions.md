---
date created: 2025-01-19 10:46:29
date modified: 2025-01-21 16:55:34
parents:
  - "[[Side Projects]]"
tags:
  - AI
  - SaaS
  - AWS
complete: 0.5
---
OK, let's do this. I want to launch multiple AWS resources using the CDK in python. The infrastructure looks like the attached image. I would like the infrastructure to be launched in two stages.

## Stage 1
The checking Lambda function should query a DynamoBD (habit-slap-users-dev) which already exists, so no need to create this resource. The function should trigger according to an EventBridge rule which is set to trigger the Lambda function every 5 minutes. The expected behaviour of the checking Lambda function is as follows:
- The DynamoBD habit-slap-users-dev should be queried
- The query is to find every record where the "next_email_date" column is equal to the current time
- Return all record that meet this query condition
- Create a list of dictionaries, where each dictionary is the record returned in the step above, for example:
	- [{"email": "example1@email.com", "goal": "lose weight"}, {"email": "example2@email.com", "goal": "quit smoking"}, ...]
- Send each dictionary in this list to an SQS (not created yet)

## Stage 2
The sending Lambda function handles the generation of emails and the sending of emails. It should be triggered by the SQS (now created after stage 1) which feeds the message to the lambda function. The "goal" key of the json string should be used as the prompt of the email generation. Once the email has been generated, it should be sent to the recipient, which is the "email" key of the json.

### Generating the email
Key points of the email generating code
- The code should be simple and clean. I only want a basic prompt input and output structure
- Use a popular framework like Langchain to manage system prompts, user prompts etc
- Use OpenAI's gpt-4o-mini model for the LLM, but allow for other models to be swapped out in future
- OPENAI_API_KEY should be stored as environment variables of the Lambda function, which will be stored locally in the .env file so they can be passed to the stack class via the dotenv python library
### Lambda function
Key points about the Lambda function
- Create a Lambda Layer to contain all necessary libraries needed to run the code
	- It may be useful to create a separate directory to handle this layer creation with the Dockerfile, a stand alone generate_base_layer.sh script, requirements.txt etc.
- The Lambda will be triggered from the SQS whenever a message appears in the queue
	- No batching of messages is necessary. One message, one lambda execution

### Sending emails
Key points about sending emails
- Use the yagmail Python library for handling the sending of emails
- GMAIL_USER and GMAIL_PASSWORD should be stored as environment variables of the Lambda function, which will be stored locally in the .env file so they can be passed to the stack class via the dotenv python library


## Important
- Please contain all code of [[#Stage 1]] in the checking_function directory, and all of [[## Stage 2]] in the sending_directory
- The language to be used is Python
- .venv is the local virtual environment
# References
 