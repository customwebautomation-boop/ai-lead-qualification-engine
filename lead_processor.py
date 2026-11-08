import os
import json
import requests
from datetime import datetime

class AILeadProcessor:
    def __init__(self):
        # Read the secure token from the active terminal session variables
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    def _parse_json_response(self, content):
        if content is None:
            raise ValueError("AI response was empty.")

        if isinstance(content, dict):
            return content

        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict):
                    if "text" in item:
                        text_parts.append(str(item["text"]))
                    elif "content" in item:
                        text_parts.append(str(item["content"]))
            content = "".join(text_parts)

        content_string = str(content).strip()
        if not content_string:
            raise ValueError("AI response was empty.")

        if content_string.startswith("```"):
            content_string = content_string.strip("`")
            if content_string.lower().startswith("json"):
                content_string = content_string[4:].strip()
            content_string = content_string.strip()

        if "{" in content_string and "}" in content_string:
            start = content_string.find("{")
            end = content_string.rfind("}")
            candidate = content_string[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        return json.loads(content_string)

    def process_incoming_lead(self, raw_message):
        """Processes the unorganized text string using either local simulation or a live OpenRouter API request."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Received unstructured payload...")

        system_prompt = (
            "You are an elite business data extraction engine. Analyze the incoming text and "
            "extract the parameters into a strict JSON format with these exact keys: "
            "\"name\", \"email\", \"estimated_budget\", \"project_scope\". "
            "Return ONLY the raw JSON object. Do not include markdown code blocks like ```json."
        )

        # Secure Fallback / Mock loop for local testing
        if not self.api_key or self.api_key == "YOUR_MOCK_OR_REAL_KEY":
            print("[!] API Key not configured. Simulating AI token generation...")
            return {
                "name": "Alex Mercer",
                "email": "alex@mercertech.io",
                "estimated_budget": 4500,
                "project_scope": "Needs a custom n8n workflow and multi-agent customer support chatbot setup."
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
            "X-Title": "AI Lead Processor Pipeline"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_message}
            ]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                print(f"\n[!] API Server Error (Status {response.status_code}): {response.text}")
                return None

            try:
                response_data = response.json()
            except ValueError:
                print(f"\n[!] Provider returned a non-JSON response: {response.text[:500]}")
                return None

            if 'error' in response_data:
                print(f"\n[!] Provider returned an error: {response_data['error']}")
                return None

            if 'choices' in response_data and isinstance(response_data['choices'], list) and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]
                if 'message' in choice:
                    content = choice['message'].get('content')
                    if content is not None:
                        parsed = self._parse_json_response(content)
                        if isinstance(parsed, dict):
                            return parsed

            print(f"\n[!] Unexpected JSON structure from provider: {response_data}")
            return None

        except requests.RequestException as e:
            print(f"AI network exception: {str(e)}")
            return None
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            print(f"AI error parsing exception: {str(e)}")
            return None

    def qualify_and_route_lead(self, structured_lead):
        if not structured_lead: 
            return
            
        budget = structured_lead.get("estimated_budget", 0)
        name = structured_lead.get("name", "Unknown Contact")
        
        print("\n" + "="*50)
        print(f"📊 EVALUATING LEAD: {name}")
        print(f"Budget: ${budget}")
        
        if budget >= 1500:
            print(f"🟢 QUALIFIED: Budget exceeds threshold.")
            print("Action: Syncing to Google Sheets CRM & alerting rep via Telegram...")
        else:
            print(f"🟡 LOW-PRIORITY LEAD: Budget falls below threshold.")
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
    
    # Halt data evaluating tree safely if API execution failed to return content
    if parsed:
        processor.qualify_and_route_lead(parsed)
    else:
        print("[X] Pipeline halted because the AI parsing module failed.")
