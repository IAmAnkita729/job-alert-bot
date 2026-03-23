import requests
import os
import json

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEEN_FILE = "jobs_seen.json"

# 🎯 STRONG FILTER (Azure-focused)
KEYWORDS = [
    "azure data engineer",
    "data engineer azure",
    "azure databricks",
    "databricks engineer",
    "etl engineer",
    "data pipeline engineer",
    "azure etl"
]

# ❌ REMOVE JUNK CONTENT
BLOCK_WORDS = [
    "course", "blog", "roadmap", "interview",
    "questions", "tutorial", "learn", "guide"
]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def load_seen():
    if os.path.exists(SEEN_FILE):
        return json.load(open(SEEN_FILE))
    return []

def save_seen(data):
    json.dump(data, open(SEEN_FILE, "w"))

def match(title):
    t = title.lower()
    return any(k in t for k in KEYWORDS)

def is_valid(title):
    t = title.lower()
    return not any(b in t for b in BLOCK_WORDS)

# ✅ JOBICY
def jobicy():
    try:
        data = requests.get("https://jobicy.com/api/v2/remote-jobs").json()
        return [{
            "id": str(j["id"]),
            "title": j["jobTitle"],
            "company": j["companyName"],
            "link": j["url"]
        } for j in data.get("jobs", [])]
    except:
        return []

# ✅ REMOTEOK
def remoteok():
    try:
        data = requests.get("https://remoteok.com/api").json()[1:]
        return [{
            "id": str(j.get("id")),
            "title": j.get("position"),
            "company": j.get("company"),
            "link": j.get("url")
        } for j in data]
    except:
        return []

def main():
    seen = load_seen()
    new_seen = seen.copy()
    sent = 0

    jobs = jobicy() + remoteok()

    for job in jobs:
        if not job["title"]:
            continue

        title = job["title"]
        jid = job["id"]

        if jid in seen:
            continue

        # 🎯 APPLY FILTERS
        if match(title) and is_valid(title):
            msg = f"""🚨 Azure Data Engineer Job

💼 {title}
🏢 {job['company']}
🔗 {job['link']}"""

            send(msg)
            new_seen.append(jid)
            sent += 1

    save_seen(new_seen[-300:])
    print("Jobs sent:", sent)

main()
