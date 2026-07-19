import os
import struct

def get_image_info(filepath):
    """Parses image header to get size and format."""
    size = os.path.getsize(filepath)
    with open(filepath, 'rb') as f:
        head = f.read(24)
        if len(head) < 24:
            return "Too short", 0, 0
        
        # Check if PNG
        if head.startswith(b'\x89PNG\r\n\x1a\n'):
            w, h = struct.unpack('>II', head[16:24])
            return "PNG", w, h
        
        # Check if JPEG
        elif head.startswith(b'\xff\xd8'):
            f.seek(0)
            try:
                data = f.read()
                i = 2
                while i < len(data):
                    marker = data[i:i+2]
                    if len(marker) < 2:
                        break
                    if marker[0] == 0xff:
                        m_byte = marker[1]
                        if m_byte in [0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]:
                            h, w = struct.unpack('>HH', data[i+5:i+9])
                            return "JPEG", w, h
                        else:
                            block_len = struct.unpack('>H', data[i+2:i+4])[0]
                            i += 2 + block_len
                    else:
                        i += 1
            except Exception as e:
                return f"JPEG (Error: {e})", 0, 0
            return "JPEG (SOF not found)", 0, 0
            
    return "Unknown", 0, 0

dest_dir = r"c:\Users\OM\OneDrive\Desktop\MediKal\frontend\assets\images"
for f in ["doctor_kit_hd.jpg", "ai_hands_hd.jpg"]:
    path = os.path.join(dest_dir, f)
    if os.path.exists(path):
        fmt, w, h = get_image_info(path)
        size = os.path.getsize(path)
        print(f"{f}: {fmt} {w}x{h} ({size} bytes)")
    else:
        print(f"{f}: Not found")
