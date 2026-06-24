import urllib.request
import urllib.parse


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


print("1. Script started")

env = load_env_file()
print("2. .env loaded")

print("3. Keys found in .env:", list(env.keys()))

BOT_TOKEN = env["BOT_TOKEN"]
CHAT_ID = env["CHAT_ID"]

print("4. BOT_TOKEN length:", len(BOT_TOKEN))
print("5. CHAT_ID:", CHAT_ID)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
print("6. URL created")

data = urllib.parse.urlencode({
    "chat_id": CHAT_ID,
    "text": "Hello! This is my test message read from the .env file."
}).encode("utf-8")

print("7. Data encoded")

req = urllib.request.Request(url, data=data, method="POST")
print("8. Request created")

with urllib.request.urlopen(req) as response:
    print("9. Request sent")
    body = response.read().decode("utf-8")
    print("10. Response received")
    print("Response:", body)