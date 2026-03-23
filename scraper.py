import requests
import os
import json

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEEN_FILE = "jobs_seen.json"

KEYWORDS = [
    "azure data engineer",
    "data engineer",
    "azure",
    "databricks",
    "etl",
    "data pipeline"
]

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

# 🎯 SCORING SYSTEM (VERY IMPORTANT)
def score_job(title):
    t = title.lower()
    score = 0

    if "azure data engineer" in t:
        score += 10
    if "data engineer" in t:
        score += 6
    if "azure" in t:
        score += 4
    if "databricks" in t:
        score += 3
    if "etl" in t:
        score += 2

    return score

def is_valid(title):
    t = title.lower()
    if any(b in t for b in BLOCK_WORDS):
        return False
    return True

# APIs
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

    jobs = jobicy() + remoteok()

    scored_jobs = []

    for job in jobs:
        if not job["title"]:
            continue

        jid = job["id"]
        title = job["title"]

        if jid in seen:
            continue

        if not is_valid(title):
            continue

        score = score_job(title)

        if score > 0:
            job["score"] = score
            scored_jobs.append(job)

    # 🎯 SORT BEST FIRST
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)

    # 🔥 TAKE TOP 10 ONLY
    top_jobs = scored_jobs[:10]

    for job in top_jobs:
        msg = f"""🚨 Top Azure/Data Job

💼 {job['title']}
🏢 {job['company']}
🔗 {job['link']}"""

        send(msg)
        new_seen.append(job["id"])

    save_seen(new_seen[-300:])
    print("Sent:", len(top_jobs))

main()
