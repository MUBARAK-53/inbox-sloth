import os
import sys
import json
import sentry_sdk

# Initialize Sentry SDK for Agent Tracing & Error Monitoring
sentry_sdk.init(
    dsn="https://88429cf795513cefa27646afd2a586ff@o4512305399398400.ingest.us.sentry.io/4512305423581184",
    traces_sample_rate=1.0,
    environment="hacktoberfest-pure-local"
)

def triage_chat(chat_text: str) -> dict:
    """
    Local heuristic triage engine simulating an AI agent,
    fully tracked and traced via Sentry.
    """
    lines = [line.strip() for line in chat_text.splitlines() if line.strip()]
    text_lower = chat_text.lower()
    
    # Check for actual high-priority operational issues
    if any(word in text_lower for word in ["bug", "fix", "error", "down", "broken", "urgent", "asap", "production"]):
        urgency = "URGENT - ACTION REQUIRED"
        suggested_replies = ["I can look into this right away.", "Checking on this now!"]
    # Check for coordination/planning
    elif any(word in text_lower for word in ["tomorrow", "today", "when", "who", "meet", "time", "still on"]):
        urgency = "MODERATE"
        suggested_replies = ["Sounds good, see you then!", "Works for me!", "Count me in!"]
    else:
        urgency = "CHILL - IGNORE"
        suggested_replies = ["Got it, thanks!", "Haha nice.", "Love that."]

    questions = [line for line in lines if "?" in line]
    briefing = f"Processed {len(lines)} message lines. Detected {len(questions)} open question(s) requiring coordination."

    return {
        "urgency_level": urgency,
        "morning_briefing": briefing,
        "suggested_replies": suggested_replies,
        "detected_questions": questions
    }

def run_sloth(file_path: str):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        chat_text = f.read()

    print(f"\n🦥 Inbox Sloth is digesting '{file_path}' locally...")

    # Trace execution in Sentry
    with sentry_sdk.start_transaction(op="agent.execution", name="pure_local_chat_triage"):
        try:
            sentry_sdk.set_tag("agent_version", "3.0")
            sentry_sdk.set_context("chat_metrics", {"character_length": len(chat_text)})

            result = triage_chat(chat_text)

            print("\n" + "="*40)
            print(" 📋 INBOX SLOTH MORNING BRIEFING ")
            print("="*40)
            print(f"🚨 Urgency Level  : {result['urgency_level']}")
            print(f"📝 Summary        : {result['morning_briefing']}")
            print(f"💡 Suggested Reply: {result['suggested_replies'][0]}")
            print("="*40 + "\n")

        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"❌ Error during triage: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sloth.py sample_chat.txt")
        sys.exit(1)
    
    run_sloth(sys.argv[1])