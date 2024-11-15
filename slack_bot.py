import os
from flask import Flask, request, jsonify
import json
from slack_sdk import WebClient # type: ignore
from slack_sdk.errors import SlackApiError # type: ignore
from time import sleep, perf_counter
from threading import Thread

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

#create leaderboard
leaderboard: dict[str, int] = {}    

app = Flask(__name__)

@app.route('/api/slack/snipe', methods=['POST'])
def slack_events():
    data = request.json

    if data.get("type") == "url_verification":
        # Respond with the challenge parameter
        return jsonify({"challenge": data["challenge"]}), 200

    # Ensure message contains the expected fields
    if 'event' in data and 'text' in data['event']:
        text = data['event']['text']
        user_id = data['event']['user']
        
        # Look for @mention in the text
        if '@' in text:
            mentioned_user = text.split('@')[1].split(' ')[0]
            
            # Confirm snipe in channel
            channel_id = data['event']['channel']
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f":dart: Snipe confirmed on <@{mentioned_user}> by <@{user_id}>!"
                )
                
                # Update leaderboard
                if mentioned_user in leaderboard:
                    leaderboard[user_id] += 1
                else:
                    leaderboard[user_id] = 1

            except SlackApiError as e:
                print(f"Error posting message: {e.response['error']}")

    return jsonify({'status': 'success'}), 200

def checkAndPostToChannel(text, user_id, channel_id):
    # Look for @mention in the text
    if '@' in text:
        mentioned_user = text.split('@')[1].split(' ')[0]
        
        # Confirm snipe in channel
        try:
            client.chat_postMessage(
                channel=channel_id,
                text=f":dart: Snipe confirmed on <@{mentioned_user}> by <@{user_id}>!"
            )
            
            # Update leaderboard
            if mentioned_user in leaderboard:
                leaderboard[mentioned_user] += 1
            else:
                leaderboard[mentioned_user] = 1

        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")

def get_display_name_from_user_id(user_id):
    try:
        userResponse = client.users_info(user=user_id)
        return userResponse["user"]["profile"]["display_name"]
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return None


def populate_leaderboard():
    response = client.conversations_history(
        channel=os.environ['SNIPE_PROJECT_ID'],
        limit=100000000000000000,
    )
    leaderboard.clear()
    messages = response["messages"]
    for message in messages:
        text = message["text"]
        if message["type"]=="message" and "snipe" in text and "@" in text:
            if message["user"] in leaderboard:
                leaderboard[message["user"]] += 1
            else:
                leaderboard[message["user"]] = 1


@app.route('/api/slack/leaderboard', methods=['GET'])
def get_leaderboard():
    # Convert leaderboard dictionary to JSON for easy display
    populate_leaderboard()
    dict = {}
    for user_id,score in leaderboard.items():
        displayName = get_display_name_from_user_id(user_id)
        if (displayName is not None):
            dict[displayName] = score
        else:
            dict[user_id] = 0
    return jsonify(dict), 200

@app.route('/api/slack/leaderboard/<user_id>/', methods=['GET'])
def get_leaderboard_with_user_id(user_id):
    populate_leaderboard()
    dict = {}
    if user_id not in leaderboard:
        dict[user_id] = 0
        return jsonify(dict), 200
    displayName = get_display_name_from_user_id(user_id)
    if (displayName is not None):
        dict[displayName] = leaderboard[user_id]
    else:
        dict[user_id] = 0
    return jsonify(dict), 200

@app.route('/api/slack/leaderboard_publish/', methods=['GET'])
def post_leaderboard():
    populate_leaderboard()
    dict = {}
    for user_id in sorted(leaderboard,key=lambda x: -leaderboard.get(x)):
        displayName = get_display_name_from_user_id(user_id)
        if (displayName is not None):
            dict[displayName] = leaderboard[user_id]
        else:
            dict[user_id] = 0
    client.chat_postMessage(
                    channel=os.environ['SNIPE_PROJECT_ID'],
                    text=":dart: Leaderboard Rankings: " + str(dict)
                )
    return jsonify({}), 200


if __name__ == "__main__":
    app.run(port=3000, debug=True)
