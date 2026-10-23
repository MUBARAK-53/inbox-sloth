import os, sys, sqlite3, datetime, sentry_sdk

sentry_sdk.init(
    dsn="https://88429cf795513cefa27646afd2a586ff@o4512305399398400.ingest.us.sentry.io/4512305423581184",
    traces_sample_rate=1.0,
    environment="hacktoberfest-pure-local"
)

DB_FILE = "sloth_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS triage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            filename TEXT,
            urgency_level TEXT,
            line_count INTEGER,
            question_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_triage(filename, urgency, lines_count, questions_count):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO triage_logs (timestamp, filename, urgency_level, line_count, question_count)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.datetime.now().isoformat(), filename, urgency, lines_count, questions_count))
    conn.commit()
    conn.close()

def triage_chat(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    tl = text.lower()
    if any(w in tl for w in ["bug", "fix", "error", "down", "broken", "asap", "production"]):
        u, r = "URGENT - ACTION REQUIRED", ["I can look into this right away."]
    elif any(w in tl for w in ["tomorrow", "today", "when", "who", "meet", "time", "still on"]):
        u, r = "MODERATE", ["Sounds good, see you then!", "Works for me!"]
    else:
        u, r = "CHILL - IGNORE", ["Got it, thanks!", "Love that."]
    qs = [l for l in lines if "?" in l]
    return {"urgency_level": u, "morning_briefing": f"Processed {len(lines)} message lines. Found {len(qs)} question(s).", "suggested_replies": r, "lines": len(lines), "questions": len(qs)}

def run(fp):
    if not os.path.exists(fp): return print("File not found")
    with open(fp, "r", encoding="utf-8") as f: data = f.read()
    print(f"\n🦥 Inbox Sloth digesting '{fp}'...")
    with sentry_sdk.start_transaction(op="agent.execution", name="local_triage_with_db"):
        res = triage_chat(data)
        log_triage(fp, res["urgency_level"], res["lines"], res["questions"])
        print("\n" + "="*40 + "\n 📋 INBOX SLOTH MORNING BRIEFING (Logged) \n" + "="*40)
        print(f"🚨 Urgency Level  : {res['urgency_level']}")
        print(f"📝 Summary        : {res['morning_briefing']}")
        print(f"💡 Suggested Reply: {res['suggested_replies'][0]}")
        print("="*40 + "\n")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "sample_chat.txt")