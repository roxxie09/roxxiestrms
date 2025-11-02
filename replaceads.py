import os
import re

folder_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\RANDOM\roxxiestrms"

replacement_script_tag = '<script src="https://richinfo.co/richpartners/pops/js/richads-pu-ob.js" data-pubid="991686" data-siteid="376319" async data-cfasync="false"></script>'
additional_script_tag = '<script type="module" src="https://richinfo.co/richpartners/push/js/rp-cl-ob.js?pubid=991686&siteid=376330&niche=33" async data-cfasync="false"></script>'

# Regex to find the replacement script tag in head
replacement_script_pattern = re.compile(
    re.escape(replacement_script_tag), re.IGNORECASE)

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".html"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # If the additional script is already present, skip adding it
        if additional_script_tag in content:
            print(f"Additional script already present in {filename}, skipping")
            continue

        # Insert the additional script tag immediately after the replacement script tag
        def insert_after(match):
            return match.group(0) + "\n" + additional_script_tag

        new_content, count = replacement_script_pattern.subn(insert_after, content, count=1)

        if count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added additional script in {filename}")
        else:
            print(f"Replacement script tag not found in {filename}, skipping")
