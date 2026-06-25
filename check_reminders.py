import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Europe/Rome")
TOLERANCE_MINUTES = 15


def load_env_file(filename=".env"):
    env = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
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


def load_reminders(filename="reminders.txt"):
    reminders = []
    with open(filename, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if " | " not in line:
                print(f"Skipped invalid line: {line}")
                continue
            dt_str, message = line.split(" | ", 1)
            reminders.append((dt_str.strip(), message.strip()))
    return reminders


def load_sent(filename="sent_reminders.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_sent(sent_set, filename="sent_reminders.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for item in sorted(sent_set):
            f.write(item + "\n")


def parse_reminder_datetime(dt_string):
    return datetime.strptime(dt_string, "%Y-%m-%d %H:%M").replace(tzinfo=TIMEZONE)


env = load_env_file()
BOT_TOKEN = env["BOT_TOKEN"]
CHAT_ID = env["CHAT_ID"]

now = datetime.now(TIMEZONE)
window_start = now - timedelta(minutes=TOLERANCE_MINUTES)

print("Current time in Europe/Rome:", now.strftime("%Y-%m-%d %H:%M"))
print("Checking reminders due between:",
      window_start.strftime("%Y-%m-%d %H:%M"),
      "and",
      now.strftime("%Y-%m-%d %H:%M"))

reminders = load_reminders()
sent_reminders = load_sent()

changed = False
sent_count = 0

for dt_str, message in reminders:
    reminder_id = f"{dt_str} | {message}"
    print("\n---")
    print("Reminder:", reminder_id)

    if reminder_id in sent_reminders:
        print("Skipped: already sent.")
        continue

    try:
        reminder_time = parse_reminder_datetime(dt_str)
    except Exception as e:
        print(f"Skipped invalid datetime: {dt_str} | Error: {e}")
        continue

    if window_start <= reminder_time <= now:
        print("Matched: sending Telegram message...")
        send_telegram_message(BOT_TOKEN, CHAT_ID, message)
        sent_reminders.add(reminder_id)
        changed = True
        sent_count += 1
        print("Marked as sent.")
    else:
        print("Not due yet (or too old for the tolerance window).")

if changed:
    save_sent(sent_reminders)
    print(f"\nSaved sent_reminders.txt. Sent {sent_count} reminder(s).")
else:
    print("\nNo reminders were sent. sent_reminders.txt not changed.")
