import urllib.request
import urllib.error
import json

url = 'https://medikal-backend-production-d7ad.up.railway.app/api/auth/register/send-otp/'
data = {
    'type': 'email',
    'value': 'dipanker.110005@gmail.com'
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Connection Error: {e}")
