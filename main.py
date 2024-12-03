import os
import shutil
import json

def print_welcome_message():
    print("Welcome to File Organizer")

def list_files_in_directory(path):
    try:
        return os.listdir(path)
    except FileNotFoundError:
        print(f"The directory {path} was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def organize_files_by_extension(path, files):
    move_log = []  # List to store move operations for undo

    for file in files:
        # Skip directories and the move_log.json file
        if os.path.isdir(os.path.join(path, file)) or file == 'move_log.json':
            continue
        
        # Get file extension
        _, extension = os.path.splitext(file)
        extension = extension.lstrip('.').lower()  # Remove the dot and convert to lowercase
        
        if extension:  # Only proceed if there's an extension
            # Create a directory for the extension if it doesn't exist
            extension_dir = os.path.join(path, extension)
            os.makedirs(extension_dir, exist_ok=True)
            
            # Move the file into the respective directory
            source = os.path.join(path, file)
            destination = os.path.join(extension_dir, file)
            shutil.move(source, destination)
            print(f"Moved {file} to {extension}/")

            # Log the move operation
            move_log.append({'source': source, 'destination': destination})

    # Save the move log to a file
    with open(os.path.join(path, 'move_log.json'), 'w') as log_file:
        json.dump(move_log, log_file)

def undo_last_organization(path):
    log_file_path = os.path.join(path, 'move_log.json')
    
    if not os.path.exists(log_file_path):
        print("No move log found. Nothing to undo.")
        return

    with open(log_file_path, 'r') as log_file:
        move_log = json.load(log_file)

    for move in reversed(move_log):
        source = move['destination']
        destination = move['source']
        shutil.move(source, destination)
        print(f"Moved {os.path.basename(source)} back to original location.")

    # Remove the log file after undoing
    os.remove(log_file_path)

if __name__ == "__main__":
    print_welcome_message()
    
    # Prompt the user for a directory path
    user_input = input("Enter the directory path to list files (default is Desktop, '~/Desktop'): ").strip()
    
    # Use the Desktop path as default if no input is provided
    if not user_input:
        user_input = "Desktop"
    
    # Append '~/'
    full_path = os.path.expanduser(f"~/{user_input}")
    
    # Ask the user if they want to organize or undo
    action = input("Enter 'org' to organize files or 'undo' to undo the last organization: ").strip().lower()
    
    if action == 'org':
        # List files in the directory
        files = list_files_in_directory(full_path)
        
        # Organize files by their extensions
        organize_files_by_extension(full_path, files)
    elif action == 'undo':
        # Undo the last organization
        undo_last_organization(full_path)
    else:
        print("Invalid action. Please enter 'org' or 'undo'.")
