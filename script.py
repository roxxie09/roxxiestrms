import os

# Define the old and new script tags (making sure to account for the closing </script> tag)
old_script = "<script type='text/javascript' src='//pl24903545.profitablecpmrate.com/a8/d0/0a/a8d00ade81b48f5b50f7935385047cd0.js'>"
new_script = "<script type='text/javascript' src='//dearesthydrogen.com/a8/d0/0a/a8d00ade81b48f5b50f7935385047cd0.js'></script>"

# Path to the current directory (same folder as the script)
folder_path = os.getcwd()

# Loop through each file in the current directory
for filename in os.listdir(folder_path):
    if filename.endswith(".html"):  # Only target .html files
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Replace the old script tag with the new one
        file_content = file_content.replace(old_script, new_script)

        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(file_content)

print("Replacement complete!")
