import requests
import json
import time

def test_ask_guruji():
    url = "http://127.0.0.1:8000/ask-guruji"
    payload = {
        "question": "श्याम यंत्र के क्या लाभ हैं और इसे कहाँ रखें?"
    }
    
    print("Sending question to Guruji...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("\n--- GURUJI RESPONSE ---")
            print(f"Text: {data['answer_text']}")
            print(f"Audio URL: {data['audio_url']}")
            print(f"Avatar: {data['avatar']}")
            print("------------------------")
            print("\n✓ System logic is working perfectly.")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection Error: {e}")
        print("Make sure your FastAPI server is running (uvicorn main:app --reload)")

if __name__ == "__main__":
    test_ask_guruji()
