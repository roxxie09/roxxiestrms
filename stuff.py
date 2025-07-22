import os
import re

def replace_afronifty_urls(directory):
    pattern = r"https://lol\.afronifty\.com/([^\s\"']+\.m3u8)"
    replacement_template = r"https://snake.ncvtmisgov.com/\1"

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Use regex to find and replace all matching URLs
                updated_content, count = re.subn(pattern, replacement_template, content)

                if count > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    print(f"Updated {count} URL(s) in: {file_path}")
                else:
                    print(f"No change: {file_path}")

# Replace '.' with your target directory if needed
replace_afronifty_urls('.')
