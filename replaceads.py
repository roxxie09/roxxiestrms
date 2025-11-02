import os
import re

folder_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\RANDOM\roxxiestrms"

pattern = re.compile(
    r"""<script\s+type="text/javascript">\s*
    atOptions\s*=\s*\{\s*
    'key'\s*:\s*'003d52b3a131567a085c68d8775f52a2',\s*
    'format'\s*:\s*'iframe',\s*
    'height'\s*:\s*60,\s*
    'width'\s*:\s*468,\s*
    'params'\s*:\s*\{\s*\}\s*
    \};\s*
    </script>\s*
    <script\s+type="text/javascript"\s+src="//monthspathsmug.com/003d52b3a131567a085c68d8775f52a2/invoke.js"></script>\s*
    <script\s+type='text/javascript'\s+src='//monthspathsmug.com/39/5b/74/395b743c98df9f3269c808abb2b1d06a.js'></script>
    """, re.VERBOSE | re.DOTALL)

replacement_script_tag = '<script src="https://richinfo.co/richpartners/pops/js/richads-pu-ob.js" data-pubid="991686" data-siteid="376319" async data-cfasync="false"></script>'

head_close_pattern = re.compile(r"</head>", re.IGNORECASE)

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".html"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove the target old script block
        new_content, n = pattern.subn("", content)
        if n > 0:
            # Insert the replacement_script_tag just before </head>
            def insert_script(match):
                return replacement_script_tag + "\n" + match.group(0)
            new_content = head_close_pattern.sub(insert_script, new_content, count=1)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"Replaced script and moved to head in: {filename}")
