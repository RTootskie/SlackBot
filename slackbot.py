import os
from jira import JIRA
from slack_sdk.rtm_v2 import RTMClient

rtm = RTMClient(token=os.getenv("SLACK_TOKEN"))
jira = JIRA(server="#",
            basic_auth=("#", os.getenv("JIRA_TOKEN"))
            # Needs to be specify Jira server name, email and application token to the user.
            )


@rtm.on("message")
def handle(client: RTMClient, event: dict):
    print(event)
    if event['bot_id'] in ['#']:  # Add more workflow IDs here if you want.
        if 'thread_ts' in event:  # If it is a bot message inside a thread skip it
            pass
        else:
            channel_id = event["channel"]  # Get the Channel ID
            thread_ts = str(event["ts"])  # Get the thread TS
            thread_ts_link = thread_ts.replace(".", "")  # Remove the dot from TS for valid link.
            priority_text = str(event["blocks"][0]["elements"][0]["elements"][2]["name"]).upper()  # Find the correct
            # text for priority of the Slack message (This is specific to the Request Access one)
            summary_text = event["blocks"][0]["elements"][0]["elements"][9]["text"]  # Specific to request access
            # workflow again get the proper text.
            slack_link = f"#{channel_id}/p{thread_ts_link}"  # Create valid link according to your Slack workspace.

            description_text = f"You can find the issue at the following\nSlack-Link: {slack_link}"
            # Format description for card.

            new_issue_dict = {
                "project": "#",  # Specify project key
                "summary": f"SLACK-TICKET - {priority_text} - {summary_text}",
                "description": description_text,
                "issuetype": {"name": "Task"},
            }

            new_issue = jira.create_issue(
                fields=new_issue_dict
            )

            all_issue_fields = jira.fields()  # Give us all the fields.
            name_map = {field['name']: field['id'] for field in
                        all_issue_fields}  # Give the possibility to access the custom fields by field name.
            print(name_map)

            update_this_issue = jira.issue(str(new_issue))
            update_this_issue.update(fields={name_map["slack-thread-ts"]: f"{thread_ts}"})  # Add the thread ID
            update_this_issue.update(fields={name_map["slack-channel-id"]: f"{channel_id}"})  # Add the channel ID


rtm.start()  # Start listening on the API
