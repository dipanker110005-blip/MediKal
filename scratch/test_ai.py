import urllib.request
import urllib.error
import json

base_url = 'https://medikal-backend-production-d7ad.up.railway.app'

def test_ai():
    # 1. Login
    login_url = f"{base_url}/api/auth/login/"
    login_data = {
        'email': 'patient1@medikal.local',
        'password': 'Password123'
    }
    
    req = urllib.request.Request(
        login_url,
        data=json.dumps(login_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            access_token = res_data['access']
            print("Logged in successfully. Access token obtained.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Call Chatbot
    chat_url = f"{base_url}/api/ai-assistant/chat/"
    chat_data = {
        'prompt': 'What is typhoid?'
    }
    
    req = urllib.request.Request(
        chat_url,
        data=json.dumps(chat_data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        },
        method='POST'
    )
    
    print("Calling AI Chat endpoint with prompt: 'What is typhoid?'...")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("\nResponse from AI:")
            print(res_data.get('response'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}:")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == '__main__':
    test_ai()
