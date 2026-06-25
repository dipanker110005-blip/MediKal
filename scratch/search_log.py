import os
import json

log_path = r"C:\Users\OM\.gemini\antigravity-ide\brain\8b79b7a0-c6fb-4c55-bb4e-44fd526be3a1\.system_generated\logs\transcript.jsonl"
keywords = ['Paracetamol', 'FIX 9', 'FIX 10', 'FIX 11', 'FIX 12', 'FIX 13', 'FIX 14', 'Fix 9', 'Fix 10', 'Fix 11', 'Fix 12', 'Fix 13', 'Fix 14', 'Login Page Images', 'Banner Text-Over-Image', 'timeline', 'care circle']

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        found = [kw for kw in keywords if kw in line]
        if found:
            try:
                data = json.loads(line)
                print(f"Line {idx+1} | Step {data.get('step_index')} | Type {data.get('type')} | Matches: {found} | Length: {len(line)}")
            except Exception as e:
                print(f"Line {idx+1} | Parse error: {e}")
