import os

# Define the new script tags that you want to append at the bottom
new_scripts = [
    "<script type='text/javascript' src='//dearesthydrogen.com/c1/82/80/c18280deffd705ae435b128cb42c35c5.js'></script>",
    """<script type="text/javascript"> 
        atOptions = {
            'key' : '2dd3949da5b04dc4b008c10d433a08d1',
            'format' : 'iframe',
            'height' : 60,
            'width' : 468,
            'params' : {}
        };
    </script>
    <script type="text/javascript" src="//dearesthydrogen.com/2dd3949da5b04dc4b008c10d433a08d1/invoke.js"></script>""",
    """<script async="async" data-cfasync="false" src="//dearesthydrogen.com/c3639d5c75ac6152f14bdf3fc73a02cd/invoke.js"></script>
    <div id="container-c3639d5c75ac6152f14bdf3fc73a02cd"></div>"""
]

# Path to the current directory (same folder as the script)
folder_path = os.getcwd()

# Loop through each file in the current directory
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):  # Only target .txt files
        file_path = os.path.join(folder_path, filename)
        
        # Open the .txt file and read the content
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Initialize new_content with the original file content
        new_content = file_content
        
        # Check if the file contains the closing </body> tag
        if "</body>" in file_content:
            # Append the new scripts just before the closing </body> tag
            new_content = file_content.replace("</body>", f"{new_scripts[0]}\n{new_scripts[1]}\n{new_scripts[2]}\n</body>")
        else:
            # If no </body> tag is found, append the new scripts at the very end of the file
            new_content = file_content + f"\n{new_scripts[0]}\n{new_scripts[1]}\n{new_scripts[2]}\n</body>"
        
        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(new_content)

print("Script tags added to the bottom of all .txt files!")
