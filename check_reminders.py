import json
import urllib.request
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo


def load_env_file(filename=".env"):
    env = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()

    return env


def send_telegram_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")

    with urllib.request.urlopen(req) as response:
        body = response.read().decode("utf-8")
        print("Telegram response:", body)


env = load_env_file()
BOT_TOKEN = env["BOT_TOKEN"]
CHAT_ID = env["CHAT_ID"]

with open("reminders.json", "r", encoding="utf-8") as f:
    reminders = json.load(f)

now = datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y-%m-%d %H:%M")
print("Current time in Europe/Rome:", now)
print("Loaded reminders:", reminders)

matched = False

for reminder in reminders:
    print("Checking reminder:", reminder["datetime"], "-", reminder["message"])

    if reminder["datetime"] == now:
        matched = True
        print("Reminder matched. Sending message...")
        send_telegram_message(BOT_TOKEN, CHAT_ID, reminder["message"])
    else:
        print("Not matched.")

if not matched:
    print("No reminders matched the current time.")