import os
from jira import JIRA
from slack_sdk.rtm_v2 import RTMClient

rtm = RTMClient(token=str(os.getenv("SLACK_TOKEN")))
jira = JIRA(server="https://linnworks.atlassian.net",
            basic_auth=("#", str(os.getenv("JIRA_TOKEN")))
            )  # Needs to be specific application token to the user.


@rtm.on("message")
def handle(client: RTMClient, event: dict):
    if "bot_id" in event and event["subtype"] == "bot_message":
        print(f"Captured Event: {event}\n")
    if event["subtype"] == "bot_message" and \
            event['username'] in ['#']: # Add more bot usernames.
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

            description_text = f"You can find the issue at the following\nSlack-Link: {slack_link}\n\n"
            # Format description for card.

            # Iterate through all elements in Slack response and fill out Jira card
            for added_text in event["blocks"][0]["elements"][0]["elements"]:
                if added_text['type'] == 'text':
                    description_text += str(added_text["text"])
                elif added_text['type'] == 'user':
                    description_text += str(added_text["user_id"])
                else:
                    continue

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
            update_this_issue.update(priority={"name": f"{priority_text}"})


rtm.start()  # Start listening on the API
