import os
import re

folder_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\RANDOM\roxxiestrms"

replacement_script_tag = '<script src="https://richinfo.co/richpartners/pops/js/richads-pu-ob.js" data-pubid="991686" data-siteid="376319" async data-cfasync="false"></script>'
new_script_tag = '<script src="https://richinfo.co/richpartners/in-page/js/richads-ob.js?pubid=991686&siteid=376376" async></script>'

head_pattern = re.compile(r"(</head>)", re.IGNORECASE)

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".html"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if the replacement script exists in the content
        if replacement_script_tag in content:
            # Check if the new script already exists to avoid duplicates
            if new_script_tag not in content:
                # Insert the new script immediately after replacement_script_tag
                updated_content = content.replace(
                    replacement_script_tag,
                    replacement_script_tag + "\n" + new_script_tag
                )

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                print(f"Added new script to: {filename}")
