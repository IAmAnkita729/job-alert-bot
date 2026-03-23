import requests
import json
import os

TOKEN   = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })
    print("Telegram response:", response.text)

def check_jobs():
    url = "https://jobicy.com/api/v2/remote-jobs?count=5"

    try:
        response = requests.get(url)
        data = response.json()
        jobs = data.get("jobs", [])
        print("Total jobs fetched:", len(jobs))
    except Exception as e:
        print("API ERROR:", e)
        send_telegram("❌ API FAILED")
        return

    # 🚨 FORCE SEND FIRST JOB
    if jobs:
        job = jobs[0]

        title = job.get("jobTitle", "No Title")
        company = job.get("companyName", "No Company")
        link = job.get("url", "")

        message = f"🔥 TEST JOB\n\n💼 {title}\n🏢 {company}\n🔗 {link}"
        send_telegram(message)
    else:
        send_telegram("❌ NO JOBS FOUND FROM API")

check_jobs()
