import json

log_path = r"C:\Users\OM\.gemini\antigravity-ide\brain\8b79b7a0-c6fb-4c55-bb4e-44fd526be3a1\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT':
                print(f"Line {idx+1} | Step {data.get('step_index')} | Content: {data.get('content')}")
                print("="*40)
        except Exception as e:
            pass
