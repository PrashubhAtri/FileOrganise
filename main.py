import os
import shutil
import json
from datetime import datetime

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

def backup_directory_structure(path):
    # Generate a timestamp for the current backup session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_log = {}

    # Traverse the directory structure
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            # Store the same path for both old and new paths
            backup_log[file] = [file_path, file_path]

    # Load existing move log or create a new one
    log_file_path = os.path.join(path, 'move_log.json')
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            data = json.load(log_file)
    else:
        data = {'moves': {}, 'created_dirs': []}

    # Add the backup log to the move log
    data['moves'][timestamp] = backup_log

    # Save the updated move log
    with open(log_file_path, 'w') as log_file:
        json.dump(data, log_file)

    print(f"Backup of directory structure created with timestamp {timestamp}")

def list_backups(path):
    log_file_path = os.path.join(path, 'move_log.json')
    if not os.path.exists(log_file_path):
        print("No backups found.")
        return

    with open(log_file_path, 'r') as log_file:
        data = json.load(log_file)
        move_log = data.get('moves', {})

    if not move_log:
        print("No backups found.")
    else:
        print("Available backups:")
        for i, timestamp in enumerate(move_log.keys(), 1):
            print(f"{i}. Backup from {timestamp}")

def restore_directory_structure(path, timestamp):
    log_file_path = os.path.join(path, 'move_log.json')
    if not os.path.exists(log_file_path):
        print("No move log found. Cannot restore.")
        return

    with open(log_file_path, 'r') as log_file:
        data = json.load(log_file)
        move_log = data.get('moves', {})

    if timestamp not in move_log:
        print(f"No backup found for timestamp {timestamp}.")
        return

    # Restore the directory structure
    backup_log = move_log[timestamp]
    for file, paths in backup_log.items():
        original_path = paths[0]
        if not os.path.exists(original_path):
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            # Restore the file (in this case, just touch the file)
            with open(original_path, 'w') as f:
                pass
            print(f"Restored {original_path}")

def delete_backup(path, timestamp):
    log_file_path = os.path.join(path, 'move_log.json')
    if not os.path.exists(log_file_path):
        print("No move log found. Cannot delete backup.")
        return

    with open(log_file_path, 'r') as log_file:
        data = json.load(log_file)
        move_log = data.get('moves', {})

    if timestamp not in move_log:
        print(f"No backup found for timestamp {timestamp}.")
        return

    # Delete the backup entry
    del move_log[timestamp]
    print(f"Deleted backup from {timestamp}")

    # Update the log file or delete it if empty
    if move_log:
        with open(log_file_path, 'w') as log_file:
            json.dump({'moves': move_log, 'created_dirs': data.get('created_dirs', [])}, log_file)
    else:
        os.remove(log_file_path)

def organize_files_by_extension(path, files, exceptions):
    move_log = {}  # Dictionary to store move operations for undo
    created_dirs = []  # List to store newly created directories

    # Generate a timestamp for the current organization session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    move_log[timestamp] = {}

    for file in files:
        # Skip directories and files in the exceptions list
        if os.path.isdir(os.path.join(path, file)) or file in exceptions:
            continue
        
        # Get file extension
        _, extension = os.path.splitext(file)
        extension = extension.lstrip('.').lower()  # Remove the dot and convert to lowercase
        
        if extension:  # Only proceed if there's an extension
            # Create a directory for the extension if it doesn't exist
            extension_dir = os.path.join(path, extension)
            if not os.path.exists(extension_dir):
                os.makedirs(extension_dir, exist_ok=True)
                created_dirs.append(extension_dir)  # Track newly created directories
            
            # Move the file into the respective directory
            source = os.path.join(path, file)
            destination = os.path.join(extension_dir, file)
            shutil.move(source, destination)
            print(f"Moved {file} to {extension}/")

            # Log the move operation
            move_log[timestamp][file] = [source, destination]

    # Save the move log and created directories to a file
    with open(os.path.join(path, 'move_log.json'), 'w') as log_file:
        json.dump({'moves': move_log, 'created_dirs': created_dirs}, log_file)

def undo_last_organization(path):
    log_file_path = os.path.join(path, 'move_log.json')
    
    if not os.path.exists(log_file_path):
        print("No move log found. Nothing to undo.")
        return

    with open(log_file_path, 'r') as log_file:
        data = json.load(log_file)
        move_log = data.get('moves', {})
        created_dirs = data.get('created_dirs', [])

    # Get the most recent timestamp
    if move_log:
        latest_timestamp = max(move_log.keys())
        latest_moves = move_log[latest_timestamp]

        for file, paths in latest_moves.items():
            source = paths[1]  # New path
            destination = paths[0]  # Original path
            shutil.move(source, destination)
            print(f"Moved {os.path.basename(source)} back to original location.")

        # Remove the entry for the undone session
        del move_log[latest_timestamp]

    # Remove directories that were created during the organization
    for dir_path in created_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Removed directory {dir_path}")

    # Update the log file or delete it if empty
    if move_log:
        with open(log_file_path, 'w') as log_file:
            json.dump({'moves': move_log, 'created_dirs': created_dirs}, log_file)
    else:
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
    
    # Check if the directory exists
    if not os.path.exists(full_path):
        print(f"Error: The directory '{full_path}' does not exist.")
    else:
        # Ask the user for the desired action
        action = input("Enter 'org' to organize files, 'undo' to undo the last organization, 'backup' to create a backup, 'list' to list backups, 'restore' to restore from a backup, or 'delete' to delete a backup: ").strip().lower()
        
        if action == 'org':
            # Create a backup of the directory structure
            backup_directory_structure(full_path)
            
            # Define exceptions
            exceptions = ['move_log.json']
            
            # List files in the directory
            files = list_files_in_directory(full_path)
            
            # Organize files by their extensions
            organize_files_by_extension(full_path, files, exceptions)
        elif action == 'undo':
            # Undo the last organization
            undo_last_organization(full_path)
        elif action == 'backup':
            # Create a backup of the directory structure
            backup_directory_structure(full_path)
        elif action == 'list':
            # List available backups
            list_backups(full_path)
        elif action == 'restore':
            # List available backups
            list_backups(full_path)
            # Ask the user to select a backup to restore
            choice = input("Enter the number of the backup to restore: ").strip()
            try:
                choice_index = int(choice) - 1
                timestamps = list(data['moves'].keys())
                if 0 <= choice_index < len(timestamps):
                    restore_directory_structure(full_path, timestamps[choice_index])
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif action == 'delete':
            # List available backups
            list_backups(full_path)
            # Ask the user to select a backup to delete
            choice = input("Enter the number of the backup to delete: ").strip()
            try:
                choice_index = int(choice) - 1
                timestamps = list(data['moves'].keys())
                if 0 <= choice_index < len(timestamps):
                    delete_backup(full_path, timestamps[choice_index])
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            print("Invalid action. Please enter 'org', 'undo', 'backup', 'list', 'restore', or 'delete'.")
