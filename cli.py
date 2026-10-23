import sys
import requests

def run_sloth_cli(file_path: str, user_name: str = "Me"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            chat_text = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        print("💡 Tip: Make sure 'sample_chat.txt' is in the same directory.")
        return

    print(f"\n🦥 Inbox Sloth is digesting '{file_path}' via local Gemma 2 & FastAPI...")
    
    try:
        response = requests.post(
            "http://localhost:8000/sloth-briefing/",
            json={"chat_text": chat_text, "user_name": user_name},
            timeout=120
        )

        if response.status_code == 200:
            result_data = response.json()
            data = result_data.get("sloth_briefing", {})
            
            print("\n" + "="*55)
            print(f"🚨 URGENCY LEVEL : {data.get('urgency_level', 'UNKNOWN')}")
            print("="*55)
            print(f"📖 MORNING BRIEFING:\n{data.get('morning_briefing', '')}")
            print("\n💬 LAZY COPY-PASTE REPLIES:")
            for idx, reply in enumerate(data.get("suggested_replies", []), 1):
                print(f"  {idx}. \"{reply}\"")
            print("="*55)
            print(f"✨ Traced and monitored by: {result_data.get('traced_by', 'Sentry')}\n")
        else:
            print(f"❌ Error from server (Status {response.status_code}):", response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to FastAPI server.")
        print("💡 Tip: Make sure your backend is running in another terminal window by typing: python main.py")
    except requests.exceptions.Timeout:
        print("\n❌ Error: The request timed out. Local LLM inference on Gemma 2 is taking longer than expected.")

if __name__ == "__main__":
    # Allows passing custom file path and username as arguments: python cli.py custom_chat.txt John
    file_target = sys.argv[1] if len(sys.argv) > 1 else "sample_chat.txt"
    user_name = sys.argv[2] if len(sys.argv) > 2 else "Me"
    run_sloth_cli(file_target, user_name)