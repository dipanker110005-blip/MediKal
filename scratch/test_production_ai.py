import urllib.request
import urllib.parse
import json
import time

base_url = 'https://medikal-backend-production-d7ad.up.railway.app'

def post_request(path, data, token=None):
    url = f"{base_url}{path}"
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, method='POST')
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode('utf-8'))
    except Exception as e:
        if hasattr(e, 'read'):
            err = e.read().decode('utf-8')
            return e.code, err
        return None, str(e)

# 1. Login
print("1. Logging in to get access token...")
status, res = post_request('/api/auth/login/', {'email': 'patient1@medikal.local', 'password': 'Password123'})
print(f"Login Status: {status}")
if status != 200:
    print(f"Login failed: {res}")
    exit(1)

token = res.get('access')
print("Login successful.")

# 2. First query
prompt1 = "What are the common side effects of Paracetamol?"
print(f"\n2. Sending first prompt: '{prompt1}'")
status, chat_res1 = post_request('/api/ai-assistant/chat/', {'prompt': prompt1, 'history': []}, token)
print(f"Response Status: {status}")
if status != 200:
    print(f"Chat failed: {chat_res1}")
    exit(1)

response_text1 = chat_res1.get('response', '')
print("\n--- AI Response 1 ---")
print(response_text1)
print("---------------------\n")

# Wait a second
time.sleep(1)

# 3. Second query with history
prompt2 = "Can pregnant women take it?"
history = [
    {
        "is_user": True,
        "text": prompt1
    },
    {
        "is_user": False,
        "text": response_text1
    }
]

print(f"3. Sending second prompt: '{prompt2}' with conversation history...")
status, chat_res2 = post_request('/api/ai-assistant/chat/', {'prompt': prompt2, 'history': history}, token)
print(f"Response Status: {status}")
if status != 200:
    print(f"Chat failed: {chat_res2}")
    exit(1)

response_text2 = chat_res2.get('response', '')
print("\n--- AI Response 2 ---")
print(response_text2)
print("---------------------\n")
