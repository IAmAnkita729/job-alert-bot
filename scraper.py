import requests
import json
import os

TOKEN   = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 🎯 Better skill targeting (balanced)
MY_SKILLS = [
    'data engineer', 'data', 'etl', 'pipeline',
    'azure', 'spark', 'databricks', 'sql', 'python'
]

SEEN_FILE = "jobs_seen.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return json.load(f)
    return []

def save_seen(seen_list):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen_list, f)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })
    print("Telegram response:", response.text)

def check_jobs():
    url = "https://jobicy.com/api/v2/remote-jobs?count=20"

    try:
        response = requests.get(url, timeout=10)
        jobs = response.json().get('jobs', [])
        print("Jobs fetched:", len(jobs))
    except Exception as e:
        print("API ERROR:", e)
        return

    seen = load_seen()
    new_seen = seen.copy()
    new_jobs_found = 0

    for job in jobs:
        job_id  = str(job.get('id', ''))
        title   = job.get('jobTitle', '').lower()
        company = job.get('companyName', '')
        link    = job.get('url', '')

        print("Checking:", title)

        if job_id in seen:
            continue

        # ✅ SMART FILTER (title based)
        if any(skill in title for skill in MY_SKILLS):
            message = (
                f"🚨 NEW JOB ALERT!\n\n"
                f"💼 {title.title()}\n"
                f"🏢 {company}\n"
                f"🔗 {link}"
            )

            send_telegram(message)
            new_jobs_found += 1
            new_seen.append(job_id)

    save_seen(new_seen[-200:])
    print(f"✅ Done. {new_jobs_found} jobs sent.")

check_jobs()
