import re

log_path = r"C:\Users\OM\.gemini\antigravity-ide\brain\8b79b7a0-c6fb-4c55-bb4e-44fd526be3a1\.system_generated\logs\transcript.jsonl"
out_path = r"scratch\extracted_contexts.txt"

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

patterns = [
    r'FIX\s+9', r'FIX\s+10', r'FIX\s+11', r'FIX\s+12', r'FIX\s+13', r'FIX\s+14',
    r'Fix\s+9', r'Fix\s+10', r'Fix\s+11', r'Fix\s+12', r'Fix\s+13', r'Fix\s+14'
]

combined_pattern = re.compile('|'.join(patterns))

with open(out_path, 'w', encoding='utf-8') as out:
    out.write(f"Total log text length: {len(text)} characters\n")
    matches = list(combined_pattern.finditer(text))
    out.write(f"Found {len(matches)} matches\n")

    for i, m in enumerate(matches):
        start = max(0, m.start() - 500)
        end = min(len(text), m.end() + 2500)
        out.write(f"\n--- MATCH {i+1} | Pattern: '{m.group()}' | Position: {m.start()} ---\n")
        snippet = text[start:end]
        snippet = snippet.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\\t', '\t')
        out.write(snippet)
        out.write("\n" + "=" * 80 + "\n")
