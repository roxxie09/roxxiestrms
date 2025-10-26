import os

# Get the current working directory
folder = os.path.dirname(os.path.abspath(__file__))

# Loop through files in the current directory
for filename in os.listdir(folder):
    if filename.endswith(".html"):
        filepath = os.path.join(folder, filename)

        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace all instances of "slux.zaynic.my.id" with "saz.blitzen.store"
        updated_content = content.replace("slux.zaynic.my.id", "saz.blitzen.store")

        # Write the changes back to the file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        print(f"✅ Updated: {filename}")
