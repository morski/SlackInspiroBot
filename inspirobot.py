import os
import time
import re
import requests
import random
import time
import json
from collections import namedtuple
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def post_inspiration():
    print("HERE")
    starttime=time.time()
    while True:
        print("POST THAT IMAGE!")
        image = get_inspiro_picture()
        print(image)
        channel = "GBG77K8RH"
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            attachments=[{'title':'Get inspired!','image_url': image}]
        )
        print("MESSAGE SENT!")
        time.sleep(10.0 - ((time.time() - starttime) % 10.0))

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def get_inspiro_picture():
    picture_number = random.randint(0,9999)
    random_folder_number = random.randint(1,100) 
    folder_number = str(random_folder_number).zfill(3)
    generated_url = "http://generated.inspirobot.me/" + str(folder_number) + "/aXm" + str(picture_number) + "xjU.jpg"
    print(generated_url)

    try:
        r = requests.head(generated_url)
        if r.status_code != 200:
            print(r.status_code)
            return get_inspiro_picture()
        else:
            return generated_url
        # prints the int of the status code. Find more at httpstatusrappers.com :)
    except requests.ConnectionError:
        print("failed to connect")

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = "Get inspired!"
    image_link = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    if command.startswith("lol"):
        try:
            image_link = get_inspiro_picture
            print(image_link)
            # prints the int of the status code. Find more at httpstatusrappers.com :)
        except requests.ConnectionError:
            print("failed to connect")

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        attachments=[{'title':response,'image_url': image_link}]
    )

    print("Message sent!")

if __name__ == "__main__":
    post_inspiration()

    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
