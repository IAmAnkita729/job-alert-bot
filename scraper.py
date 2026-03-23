import requests
import json
import os

# ── Load secrets ─────────────────────────────────────────
TOKEN   = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ── Skills (IMPROVED FILTER) ─────────────────────────────
MY_SKILLS = [
    'data', 'engineer', 'python', 'sql',
    'azure', 'spark', 'etl', 'pipeline'
]

# ── Seen jobs file ───────────────────────────────────────
SEEN_FILE = "jobs_seen.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return json.load(f)
    return []

def save_seen(seen_list):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen_list, f)

# ── Telegram sender (FIXED) ──────────────────────────────
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    response = requests.post(url, data=payload)

    print("Telegram response:", response.text)

    if response.status_code == 200:
        print(f"✅ Sent: {message[:60]}")
    else:
        print("❌ Failed to send message")

# ── Main function ────────────────────────────────────────
def check_jobs():

    url = "https://jobicy.com/api/v2/remote-jobs?count=20&tag=data-engineer"

    try:
        response = requests.get(url, timeout=10)
        jobs = response.json().get('jobs', [])
    except Exception as e:
        print(f"❌ API error: {e}")
        return

    seen = load_seen()
    new_seen = seen.copy()
    new_jobs_found = 0

    for job in jobs:
        job_id  = str(job.get('id', ''))
        title   = job.get('jobTitle', '')
        company = job.get('companyName', '')
        link    = job.get('url', '')

        print("Checking job:", title)  # 🔍 DEBUG

        # Skip already seen
        if job_id in seen:
            continue

        # ✅ Match ONLY title (better)
        if any(skill in title.lower() for skill in MY_SKILLS):
            message = (
                f"🚨 NEW JOB ALERT!\n\n"
                f"💼 {title}\n"
                f"🏢 {company}\n"
                f"🔗 {link}"
            )

            send_telegram(message)
            new_jobs_found += 1
            new_seen.append(job_id)   # ✅ only save when sent

    save_seen(new_seen[-200:])
    print(f"✅ Done. {new_jobs_found} new jobs sent.")

# ── Run ─────────────────────────────────────────────────
check_jobs()
