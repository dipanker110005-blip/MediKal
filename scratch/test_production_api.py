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

# Test login
print("1. Logging in as patient1@medikal.local...")
status, res = post_request('/api/auth/login/', {'email': 'patient1@medikal.local', 'password': 'Password123'})
print(f"Login Response Status: {status}")
if status != 200:
    print(f"Login failed: {res}")
    exit(1)

token = res.get('access')
print("Login successful! Access token obtained.")

# Test appointments
print("\n2. Fetching appointments...")
status, appointments = get_request('/api/appointments/', token)
print(f"Appointments Status: {status}")
print(f"Appointments Count: {len(appointments) if isinstance(appointments, list) else 'N/A'}")
if isinstance(appointments, list):
    for a in appointments[:3]:
        print(f"  Apt ID {a.get('id')}: Doctor {a.get('doctor_name')}, Date {a.get('date')}, Status {a.get('status')}")
else:
    print(f"Error fetching appointments: {appointments}")

# Test notifications
print("\n3. Fetching notifications...")
status, notifications = get_request('/api/notifications/', token)
print(f"Notifications Status: {status}")
print(f"Notifications Count: {len(notifications) if isinstance(notifications, list) else 'N/A'}")
if isinstance(notifications, list):
    for n in notifications[:3]:
        print(f"  Notif ID {n.get('id')}: {n.get('title')} - {n.get('body')}")
else:
    print(f"Error fetching notifications: {notifications}")

# Try to find a confirmed/pending appointment and cancel it
if isinstance(appointments, list) and len(appointments) > 0:
    upcoming = [a for a in appointments if a.get('status') in ['CONFIRMED', 'PENDING']]
    if upcoming:
        target_apt = upcoming[0]
        apt_id = target_apt.get('id')
        print(f"\n4. Attempting to cancel appointment ID {apt_id} (current status: {target_apt.get('status')})...")
        status, cancel_res = patch_request(f'/api/appointments/{apt_id}/', {'status': 'CANCELLED'}, token)
        print(f"Cancel Response Status: {status}")
        print(f"Cancel Response: {cancel_res}")
        
        # Fetch again to verify
        status, updated_appointments = get_request('/api/appointments/', token)
        for a in updated_appointments:
            if a.get('id') == apt_id:
                print(f"Verified status after cancellation: {a.get('status')}")
    else:
        print("\n4. No active PENDING or CONFIRMED appointments to test cancellation.")
else:
    print("\n4. No appointments found.")
