import os

# Get the current directory
directory = os.getcwd()

# The iframe tag to be removed
iframe_tag = '<iframe data-aa="2358765" src="//acceptable.a-ads.com/2358765" style="border:0px; padding:0; width:100%; height:100%; overflow:hidden; background-color: transparent;"></iframe>'

# Iterate through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.html'):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Remove the existing iframe tag if present
        content = content.replace(iframe_tag, '')

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

print("Specified iframe tag removed from all HTML files.")
