import os
import json
import requests
from datetime import datetime

class AILeadProcessor:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "YOUR_MOCK_OR_REAL_KEY")
        self.api_url = "https://openrouter.ai"

    def process_incoming_lead(self, raw_message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Received unstructured payload...")
        
        system_prompt = (
            "You are an elite business data extraction engine. Analyze the incoming text and "
            "extract the parameters into a strict JSON format with these exact keys: "
            "'name', 'email', 'estimated_budget', 'project_scope'."
        )

        if self.api_key == "YOUR_MOCK_OR_REAL_KEY":
            print("[!] API Key mock state active. Simulating AI token generation...")
            return {
                "name": "Alex Mercer",
                "email": "alex@mercertech.io",
                "estimated_budget": 4500,
                "project_scope": "Needs a custom n8n workflow and multi-agent customer support chatbot setup."
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_message}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"AI error: {str(e)}")
            return None

    def qualify_and_route_lead(self, structured_lead):
        if not structured_lead: return
        budget = structured_lead.get("estimated_budget", 0)
        name = structured_lead.get("name", "Unknown Contact")
        
        print("\n" + "="*50)
        print(f"📊 EVALUATING LEAD: {name}")
        print(f"Budget: ${budget}")
        
        if budget >= 1500:
            print(f"🟢 QUALIFIED: Budget exceeds threshold.")
            print("Action: Syncing to Google Sheets CRM & alerting rep via Telegram...")
        else:
            print(f" Lazarus Pipeline: Budget falls below threshold.")
            print("Action: Routing to email nurture campaign.")
        print("="*50 + "\n")

if __name__ == "__main__":
    processor = AILeadProcessor()
    messy_lead = (
        "Hey! Im Alex Mercer from mercertech.io. My contact mail is alex@mercertech.io. "
        "We are looking to overhaul our sales pipeline with a custom n8n workflow setup. "
        "We have allocated around 4500 dollars. Let me know if you are free."
    )
    parsed = processor.process_incoming_lead(messy_lead)
    processor.qualify_and_route_lead(parsed)
