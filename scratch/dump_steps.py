import json

log_path = r"C:\Users\OM\.gemini\antigravity-ide\brain\8b79b7a0-c6fb-4c55-bb4e-44fd526be3a1\.system_generated\logs\transcript.jsonl"
target_steps = [32, 48, 60, 259, 273, 289, 583, 586, 589, 591, 593]

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        try:
            data = json.loads(line)
            step = data.get('step_index')
            if step in target_steps:
                print(f"=== STEP {step} (Type: {data.get('type')}, Source: {data.get('source')}) ===")
                content = data.get('content', '')
                if content:
                    print(content[:3000]) # print first 3000 chars of content
                else:
                    print("(No content field)")
                print("\n" + "="*40 + "\n")
        except Exception as e:
            print(f"Error parsing line: {e}")
