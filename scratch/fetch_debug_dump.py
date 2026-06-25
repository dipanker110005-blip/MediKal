import urllib.request
import json
import time

url = 'https://medikal-backend-production-d7ad.up.railway.app/api/appointments/config/'

print("Querying production debug dump...")
for i in range(5):
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            print("Successfully retrieved debug dump!")
            print("\n--- Live Production Appointments (Latest 15) ---")
            for a in data.get('debug_appointments', [])[:15]:
                print(f"  ID {a['id']}: Patient {a['patient']}, Doctor {a['doctor']}, Date {a['date']} {a['time']}, Status: {a['status']}")
            
            print("\n--- Live Production Notifications (Latest 15) ---")
            for n in data.get('debug_notifications', [])[:15]:
                print(f"  ID {n['id']}: User {n['user']}, Title: {n['title']}, Body: {n['body']}")
            break
    except Exception as e:
        print(f"Attempt {i+1} failed (waiting for rebuild...): {e}")
        time.sleep(10)
