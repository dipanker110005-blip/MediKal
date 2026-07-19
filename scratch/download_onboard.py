import urllib.request
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context

dest_dir = r"c:\Users\OM\OneDrive\Desktop\MediKal\frontend\assets\images"
os.makedirs(dest_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# HD healthcare images for onboarding slides + landing page
urls = {
    # Slide 1: Doctor consulting patient (AI/digital healthcare)
    "onboard1_hd.jpg": "https://images.pexels.com/photos/7089401/pexels-photo-7089401.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&dpr=1",
    # Slide 2: Heart rate / health monitoring technology
    "onboard2_hd.jpg": "https://images.pexels.com/photos/4386467/pexels-photo-4386467.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&dpr=1",
    # Slide 3: Medical team / collaboration
    "onboard3_hd.jpg": "https://images.pexels.com/photos/3825586/pexels-photo-3825586.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&dpr=1",
    # Landing page background: ultra HD stethoscope + digital
    "landing_bg_hd.jpg": "https://images.pexels.com/photos/4386464/pexels-photo-4386464.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&dpr=1",
}

print("Downloading images...")
for name, url in urls.items():
    dest_path = os.path.join(dest_dir, name)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            with open(dest_path, 'wb') as f:
                f.write(data)
        size_kb = os.path.getsize(dest_path) // 1024
        print(f"  OK: {name} ({size_kb} KB)")
    except Exception as e:
        print(f"  FAIL: {name} - {e}")

print("Done.")
