import urllib.request
import ssl

# Disable SSL verification for download if there are cert errors
ssl._create_default_https_context = ssl._create_unverified_context

urls = {
    "doctor_kit_hd.jpg": "https://blog.ipleaders.in/wp-content/uploads/2020/01/Health-Insurance.jpg",
    "ai_hands_hd.jpg": "https://www.grantthornton.in/cdn-cgi/image/format=auto/globalassets/1.-member-firms/india/assets/images/hero-banner/1440x658-ai-healthcare.jpg"
}

dest_dir = r"c:\Users\OM\OneDrive\Desktop\MediKal\frontend\assets\images"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for name, url in urls.items():
    dest_path = f"{dest_dir}\\{name}"
    print(f"Downloading {url} to {dest_path}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(dest_path, 'wb') as f:
                f.write(response.read())
        print(f"Successfully downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
