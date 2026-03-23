import requests
import os
import json
import feedparser

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEEN_FILE = "jobs_seen.json"

# 🎯 STRONG FILTER (no random jobs now)
KEYWORDS = [
    "azure data engineer",
    "data engineer azure",
    "azure engineer data",
    "etl azure",
    "databricks engineer",
    "azure databricks",
    "data engineer spark"
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

# ✅ GOOGLE JOBS VIA RSS (IMPORTANT 🔥)
def google_jobs():
    feed = feedparser.parse(
        "https://news.google.com/rss/search?q=azure+data+engineer+jobs&hl=en-IN&gl=IN&ceid=IN:en"
    )
    jobs = []
    for entry in feed.entries:
        jobs.append({
            "id": entry.link,
            "title": entry.title,
            "company": "Google Jobs",
            "link": entry.link
        })
    return jobs

def main():
    seen = load_seen()
    new_seen = seen.copy()
    sent = 0

    jobs = jobicy() + remoteok() + google_jobs()

    for job in jobs:
        if not job["title"]:
            continue

        jid = job["id"]

        if jid in seen:
            continue

        if match(job["title"]):
            msg = f"""🚨 Azure Data Engineer Job

💼 {job['title']}
🏢 {job['company']}
🔗 {job['link']}"""

            send(msg)
            new_seen.append(jid)
            sent += 1

    save_seen(new_seen[-400:])
    print("Jobs sent:", sent)

main()
