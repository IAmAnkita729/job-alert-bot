import requests
import json
import os

# ── Load secrets from GitHub ──────────────────────────────
TOKEN   = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ── Your skills to match ──────────────────────────────────
MY_SKILLS = [
    'pyspark', 'azure', 'databricks', 'sql',
    'data engineer', 'python', 'spark',
    'azure data factory', 'adf'
]

# ── File that remembers jobs already sent ─────────────────
SEEN_FILE = "jobs_seen.json"

# ── Load already-seen jobs ────────────────────────────────
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return json.load(f)
    return []

# ── Save seen jobs ────────────────────────────────────────
def save_seen(seen_list):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen_list, f)

# ── Send Telegram message (FIXED + DEBUG) ─────────────────
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    response = requests.post(url, data=payload)

    print("Telegram response:", response.text)  # 🔥 DEBUG

    if response.status_code == 200:
        print(f"✅ Sent: {message[:60]}")
    else:
        print("❌ Failed to send message")

# ── Main job checking logic ───────────────────────────────
def check_jobs():

    # 🔥 TEST MESSAGE (keep this for now)
    send_telegram("🔥 TEST MESSAGE FROM GITHUB")

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
        desc    = job.get('jobDescription', '').lower()

        if job_id in seen:
            continue

        # Skill match
        if any(skill in desc or skill in title.lower() for skill in MY_SKILLS):
            message = (
                f"🚨 NEW JOB ALERT!\n\n"
                f"💼 {title}\n"
                f"🏢 {company}\n"
                f"🔗 {link}"
            )
            send_telegram(message)
            new_jobs_found += 1
            new_seen.append(job_id)  # ✅ only save if sent

    save_seen(new_seen[-200:])
    print(f"✅ Done. {new_jobs_found} new jobs sent.")

# ── Run ───────────────────────────────────────────────────
check_jobs()
