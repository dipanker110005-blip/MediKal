import os
from pathlib import Path
import random
import json
import urllib.request
import urllib.parse
import urllib.error
import base64

class AIService:
    @staticmethod
    def get_system_prompt() -> str:
        """
        Loads the system prompt from the system_prompt.txt file.
        """
        try:
            prompt_path = Path(__file__).resolve().parent / 'system_prompt.txt'
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading system prompt file: {e}")
            return "You are MediKal, a high-trust medical AI assistant..."

    @staticmethod
    def call_gemini_api(prompt: str, history: list, system_instruction: str) -> str:
        """
        Calls Google Gemini API using standard urllib.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        contents = []
        for msg in history:
            role = "user" if msg.get("is_user") else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("text", "")}]
            })
            
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        data = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": system_instruction
                    }
                ]
            },
            "contents": contents
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                text = res_data['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                err_data = json.loads(err_body)
                err_msg = err_data.get('error', {}).get('message', err_body)
            except Exception:
                err_msg = e.reason
            msg = f"Gemini API Error {e.code}: {err_msg}"
            print(msg)
            raise Exception(msg)
        except Exception as e:
            msg = f"Gemini connection error: {str(e)}"
            print(msg)
            raise Exception(msg)

    @staticmethod
    def call_openai_api(prompt: str, history: list, system_instruction: str) -> str:
        """
        Calls OpenAI Chat Completions API using standard urllib.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        messages = [{"role": "system", "content": system_instruction}]
        for msg in history:
            role = "user" if msg.get("is_user") else "assistant"
            messages.append({"role": role, "content": msg.get("text", "")})
            
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": "gpt-4o-mini",
            "messages": messages
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                text = res_data['choices'][0]['message']['content']
                return text.strip()
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            return None

    @staticmethod
    def fallback_response(prompt: str) -> str:
        """
        Provides a structured rule-based fallback response meeting system prompt guidelines.
        """
        query = prompt.lower().strip()
        
        # 1. Mental Health Crisis check (Rule 1A)
        suicide_words = ["suicide", "suicidal", "kill myself", "end my life", "self harm", "want to die"]
        if any(word in query for word in suicide_words):
            return (
                "I hear that you are going through a very difficult time. Please know that you are not alone, and there is support available.\n\n"
                "I strongly encourage you to reach out to someone you trust, a healthcare professional, or contact a crisis line immediately:\n"
                "- In India: Call 9152987821 (KIRAN Mental Health Helpline) or 112.\n"
                "- If you are in immediate danger of hurting yourself, please go to the nearest emergency department.\n\n"
                "Please reach out to someone who can help you stay safe.\n\n"
                "MediKal provides general health information only and does not replace a licensed clinician. Always consult a qualified healthcare provider for diagnosis or treatment."
            )

        # 2. Emergency Warning Signs check (Rule 1 / Rule 9)
        emergency_words = [
            "chest pain", "pressure in chest", "difficulty breathing", "shortness of breath", "breathless",
            "stroke", "drooping", "slurred speech", "weakness in arm", "fainting", "passed out", "seizure",
            "confusion", "cyanosis", "blue lips", "blue fingers", "throat swelling", "hives with breathing difficulty",
            "uncontrolled bleeding", "severe dehydration", "stiff neck with fever", "paralysis", "abdominal pain"
        ]
        if any(word in query for word in emergency_words):
            return (
                "This could be serious. Seek emergency care now.\n\n"
                "If you are in India, please call 112 (National Emergency), 102 (Ambulance), or 104 (Health Helpline) immediately."
            )

        # 3. Default Symptom Triage Fallbacks
        summary = "You asked about symptoms/general health guidance."
        urgency = "Routine / Non-emergency"
        possible_conditions = "Mild viral infection, fatigue, or muscle strain."
        what_to_do = "Ensure adequate rest, monitor body temperature, and stay well hydrated."
        medicines_notes = "Paracetamol (Acetaminophen) can help reduce fever or mild pain. For children, pregnancy, kidney disease, or liver disease, please consult a licensed clinician or pharmacist directly. I cannot safely estimate this."
        when_seek_help = "Seek medical evaluation if symptoms worsen, a fever exceeds 103°F (39.4°C), or if you develop chest pain or breathing difficulties."
        questions = "1. What is the current body temperature?\n2. How long have these symptoms been present?\n3. Are there any other symptoms like a sore throat or body aches?"

        if "fever" in query:
            summary = "Discussion of fever symptoms."
            possible_conditions = "Viral fever (e.g. influenza, dengue, or common cold) or bacterial infection."
            what_to_do = "Stay hydrated, use cold compresses on the forehead, and rest."
        elif "cough" in query or "throat" in query:
            summary = "Discussion of cough or throat discomfort."
            possible_conditions = "Acute bronchitis, viral upper respiratory tract infection, or pharyngitis."
            what_to_do = "Drink warm fluids, consider steam inhalation, and avoid cold drinks."
        elif "stomach" in query:
            summary = "Discussion of stomach or gastrointestinal discomfort."
            possible_conditions = "Gastroenteritis, acid reflux (GERD), or mild food poisoning."
            what_to_do = "Eat bland foods, stay hydrated with ORS, and avoid spicy or oily foods."
        elif "headache" in query:
            summary = "Discussion of headache symptoms."
            possible_conditions = "Tension headache, migraine, or sinus pressure."
            what_to_do = "Rest in a quiet, dark room, stay hydrated, and manage stress."
        elif any(word in query for word in ["paracetamol", "ibuprofen", "medicine", "pill", "drug"]):
            summary = "Information request for common pain relief/fever medication."
            possible_conditions = "Mild pain or fever management."
            what_to_do = "Consult a pharmacist or physician before starting any new drug."
            medicines_notes = (
                "Paracetamol: Commonly used for mild pain/fever. Ibuprofen: An anti-inflammatory medication.\n"
                "Please consult a licensed clinician or pharmacist directly for dosing in children, pregnancy, kidney disease, or liver disease. I cannot safely estimate this."
            )

        # Format strictly adhering to Rule 8
        response = (
            f"1. Summary: {summary}\n\n"
            f"2. Urgency: {urgency}\n\n"
            f"3. Possible Conditions: {possible_conditions}\n\n"
            f"4. What You Can Do Now: {what_to_do}\n\n"
            f"5. Medicines or Care Notes: {medicines_notes}\n\n"
            f"6. When To Seek Help: {when_seek_help}\n\n"
            f"7. Follow-up Questions (Maximum 3):\n{questions}\n\n"
            f"8. Disclaimer: MediKal provides general health information only and does not replace a licensed clinician. Always consult a qualified healthcare provider for diagnosis or treatment."
        )
        return response

    @classmethod
    def generate_response(cls, prompt: str, history: list = None) -> str:
        """
        Generates a response using active LLM API if available, falling back to a structured script.
        """
        if history is None:
            history = []
        system_instruction = cls.get_system_prompt()
        
        # Try Gemini API
        if os.getenv("GEMINI_API_KEY"):
            try:
                gemini_res = cls.call_gemini_api(prompt, history, system_instruction)
                if gemini_res:
                    return gemini_res
            except Exception as e:
                return f"Error calling Gemini API: {str(e)}"
            
        # Try OpenAI API
        if os.getenv("OPENAI_API_KEY"):
            try:
                openai_res = cls.call_openai_api(prompt, history, system_instruction)
                if openai_res:
                    return openai_res
            except Exception as e:
                return f"Error calling OpenAI API: {str(e)}"
            
        # Fallback to local rule-based engine
        return cls.fallback_response(prompt)
