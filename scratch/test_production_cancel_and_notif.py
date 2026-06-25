import urllib.request
import urllib.parse
import json

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

def get_request(path, token):
    url = f"{base_url}{path}"
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode('utf-8'))
    except Exception as e:
        if hasattr(e, 'read'):
            err = e.read().decode('utf-8')
            return e.code, err
        return None, str(e)

def patch_request(path, data, token):
    url = f"{base_url}{path}"
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, method='PATCH')
    req.add_header('Content-Type', 'application/json')
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
status, res = post_request('/api/auth/login/', {'email': 'patient1@medikal.local', 'password': 'Password123'})
token = res.get('access')

# 2. Get Doctors to find an ID
status, doctors = get_request('/api/doctors/', token)
doc_id = doctors[0]['id']

# 3. Book appointment
print("Booking a test appointment...")
status, apt = post_request('/api/appointments/', {
    'doctor': doc_id,
    'date': '2026-06-20',
    'time': '10:00 AM',
    'consultation_type': 'ONLINE'
}, token)
apt_id = apt.get('id')
print(f"Booked ID: {apt_id}, Status: {apt.get('status')}")

# 4. Cancel appointment
print(f"Cancelling appointment ID {apt_id}...")
status, cancel_res = patch_request(f'/api/appointments/{apt_id}/', {'status': 'CANCELLED'}, token)
print(f"Cancel Response: {cancel_res}")

# 5. Fetch notifications
print("Fetching notifications...")
status, notifications = get_request('/api/notifications/', token)
print("Latest 5 notifications:")
for n in notifications[:5]:
    print(f"  Notif ID {n.get('id')}: {n.get('title')} - {n.get('body')} (Created: {n.get('created_at')})")
