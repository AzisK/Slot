import os
import time
import re

import slack

os.environ['REQUESTS_CA_BUNDLE'] = 'DigiCertGlobalRootCA.crt'  # Requests
os.environ['SSL_CERT_FILE'] = 'DigiCertGlobalRootCA.crt'  # OpenSSL
os.environ['SSL_CERT_DIR'] = os.getcwd()

# instantiate Slack client
slack_client = slack.RTMClient(token=os.environ.get('SLACK_BOT_TOKEN'))

# constants
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(([A-Z]|[0-9])+)>(.*)"

def parse_bot_commands(data, starterbot_id):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    user_id, message = parse_direct_mention(data["text"])
    print(f'user_id: {user_id}')
    print(f'starterbot_id: {starterbot_id}')
    if user_id == starterbot_id:
        return message, data["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(3).strip()) if matches else (None, None)

def handle_command(command, channel, web_client):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # Sends the response back to the channel
    web_client.chat_postMessage(
        channel=channel,
        text=response or default_response
    )

def talk(data, **payload):
    web_client = payload['web_client']

    print(f'data: {data}')

    if not 'text' in data: 
        return

    starterbot_id = web_client.api_call("auth.test")['user_id']
    print(f'starterbot_id: {starterbot_id}')

    command, channel = parse_bot_commands(data, starterbot_id)

    print(command, channel)

    if command:
        handle_command(command, channel, web_client)

if __name__ == "__main__":
    slack_client.on(event='message', callback=talk)
    slack_client.start()
