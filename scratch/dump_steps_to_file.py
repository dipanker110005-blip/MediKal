import json

log_path = r"C:\Users\OM\.gemini\antigravity-ide\brain\8b79b7a0-c6fb-4c55-bb4e-44fd526be3a1\.system_generated\logs\transcript.jsonl"
target_steps = [32, 48, 60, 259, 273, 289, 563, 583, 586, 589, 591, 593]

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f, open('scratch/steps_dump.txt', 'w', encoding='utf-8') as out:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
            step = data.get('step_index')
            if step in target_steps or idx == 0: # include step 0 too!
                out.write(f"=== LINE {idx+1} | STEP {step} | TYPE {data.get('type')} | SOURCE {data.get('source')} ===\n")
                content = data.get('content', '')
                if content:
                    out.write(content)
                else:
                    out.write("(No content)")
                out.write("\n\n" + "="*80 + "\n\n")
        except Exception as e:
            out.write(f"Error parsing line {idx+1}: {e}\n")
