import os
import re

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements
    # MediKal -> Ouch
    # Medikal -> Ouch
    # medikal -> ouch
    # MEDIKAL -> OUCH

    new_content = re.sub(r'MediKal', 'Ouch', content)
    new_content = re.sub(r'Medikal', 'Ouch', new_content)
    new_content = re.sub(r'medikal', 'ouch', new_content)
    new_content = re.sub(r'MEDIKAL', 'OUCH', new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

def main():
    root_dirs = [
        r'c:\Users\OM\OneDrive\Desktop\MediKal\frontend\lib',
        r'c:\Users\OM\OneDrive\Desktop\MediKal\backend',
    ]

    for root_dir in root_dirs:
        for subdir, _, files in os.walk(root_dir):
            # Skip python envs and build folders
            if 'venv' in subdir or 'build' in subdir or '.dart_tool' in subdir:
                continue
            for file in files:
                if file.endswith('.dart') or file.endswith('.py') or file.endswith('.yaml'):
                    replace_in_file(os.path.join(subdir, file))

if __name__ == '__main__':
    main()
