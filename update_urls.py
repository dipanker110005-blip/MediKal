import re

with open('frontend/lib/core/data/medicines_data.dart', 'r') as f:
    data = f.read()

url_blister = 'https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=400&q=90'
url_bottle = 'https://images.unsplash.com/photo-1584362917165-526a968579e8?w=400&q=90'
url_bottle_white = 'https://images.unsplash.com/photo-1550572017-edd951b55104?w=400&q=90'
url_capsules = 'https://images.unsplash.com/photo-1563213126-a4273aed2016?w=400&q=90'
url_inhaler = 'https://images.unsplash.com/photo-1583324113626-70df0f4deaab?w=400&q=90'
url_cream = 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&q=90'
url_effervescent = 'https://images.unsplash.com/photo-1559181567-c3190e08af72?w=400&q=90'
url_liquid = 'https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=400&q=90'

def replace_url(match):
    name = match.group(1).lower()
    if 'inhaler' in name: url = url_inhaler
    elif 'cream' in name: url = url_cream
    elif 'effervescent' in name: url = url_effervescent
    elif 'capsule' in name: url = url_capsules
    elif 'syrup' in name or 'liquid' in name: url = url_liquid
    elif 'vitamin' in name or 'supplement' in name or 'omega' in name or 'calcium' in name or 'coq10' in name or 'biotin' in name: url = url_bottle_white
    else: url = url_blister
    
    return f'name: "{match.group(1)}"{match.group(2)}imageUrl: "{url}"'

new_data = re.sub(r'name:\s*"([^"]+)"(.*?)imageUrl:\s*"[^"]+"', replace_url, data, flags=re.DOTALL)

with open('frontend/lib/core/data/medicines_data.dart', 'w') as f:
    f.write(new_data)
print("Updated successfully")
