import os

# Define the directory containing your HTML files
directory = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\RANDOM\roxxiestrms"

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".html"):
        file_path = os.path.join(directory, filename)
        
        # Open the file for reading
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace '.pro' with '.cc'
        content = content.replace(".pro", ".cc")
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

print("Replacement complete!")
