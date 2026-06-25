import urllib.request
import urllib.error
import json

url = 'https://medikal-backend-production-d7ad.up.railway.app/api/auth/login/'

def test_login(email, password):
    data = {
        'email': email,
        'password': password
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print(f"Success for {email}:")
            print(f"  Name: {res_data.get('full_name')}")
            print(f"  Role: {res_data.get('role')}")
            print(f"  Access Token length: {len(res_data.get('access'))}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {email}:")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Connection Error for {email}: {e}")

print("Testing Admin Login:")
test_login('admin@medikal.local', 'Password123')

print("\nTesting Doctor Login:")
test_login('doctor1@medikal.local', 'Password123')

print("\nTesting Patient Login:")
test_login('patient1@medikal.local', 'Password123')
