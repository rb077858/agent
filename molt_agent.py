import os
import requests
import schedule
import time
import threading

# ====== הגדרות ======
API_KEY = os.environ.get("MOLTBOOK_API_KEY")
if not API_KEY:
    raise ValueError("MOLTBOOK_API_KEY לא מוגדר בסביבת Render!")

BASE_URL = "https://www.moltbook.com/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

AGENT_NAME = "rb07785"  # שם ה-agent שלך ב-Moltbook

# ====== פונקציות ======
def post_message(title, content, submolt="general"):
    data = {"submolt": submolt, "title": title, "content": content}
    r = requests.post(f"{BASE_URL}/posts", json=data, headers=HEADERS)
    return r.json()

def reply_post(post_id, content, parent_id=None):
    data = {"content": content}
    if parent_id:
        data["parent_id"] = parent_id
    r = requests.post(f"{BASE_URL}/posts/{post_id}/comments", json=data, headers=HEADERS)
    return r.json()

def upvote_post(post_id):
    r = requests.post(f"{BASE_URL}/posts/{post_id}/upvote", headers=HEADERS)
    return r.json()

def get_feed(limit=5):
    r = requests.get(f"{BASE_URL}/feed?sort=new&limit={limit}", headers=HEADERS)
    return r.json().get("data", [])

# ====== Heartbeat אוטומטי ======
def heartbeat():
    print("🔄 Heartbeat: בודק פוסטים חדשים...")
    feed = get_feed(limit=5)
    for post in feed:
        pid = post.get("id")
        author = post.get("author", {}).get("name")
        title = post.get("title", "")
        print(f"Post: {title} מאת {author}")
        if author != AGENT_NAME:  # אל תגיב על עצמך
            reply_post(pid, "תגובה אוטומטית מבוט 🦞")
            upvote_post(pid)
    
    # דוגמה: פרסום פוסט אוטומטי כל שעה
    post_message("פוסט אוטומטי 🦞", "זה פוסט שנשלח אוטומטית על ידי הבוט שלי.")

# ====== הפעלה ב-Render ======
def run_schedule():
    schedule.every(1).hours.do(heartbeat)
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    print("✅ Agent Moltbook רץ! בוט פעיל 24/7 🦞")
    threading.Thread(target=run_schedule, daemon=True).start()

    # אפשרות לראות feed דרך הלוגים של Render
    while True:
        print("בדיקת feed אחרונים...")
        feed = get_feed(limit=3)
        for f in feed:
            print(f"{f['id']}: {f.get('title')} מאת {f.get('author', {}).get('name')}")
        time.sleep(3600)  # כל שעה
