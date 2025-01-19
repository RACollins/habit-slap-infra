---
date created: 2025-01-19 10:46:29
date modified: 2025-01-19 11:12:19
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
Will update when satisfied with [[#Stage 1]].

## Important
- Please contain all code of [[#Stage 1]] in the checking_function directory, and all of [[## Stage 2]] in the sending_directory
- The language to be used is Python
- .venv is the virtual environment
# References
 