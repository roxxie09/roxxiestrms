import os

# Get the current directory
directory = os.getcwd()

# The script to be added
script_tag = "<script type='text/javascript' src='//pl24903545.profitablecpmrate.com/a8/d0/0a/a8d00ade81b48f5b50f7935385047cd0.js'></script>"

# Iterate through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.html'):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Insert the script tag before the closing </head> tag
        content = content.replace('</head>', f'  {script_tag}\n</head>')

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

print("Script added to all HTML files.")
