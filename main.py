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

def backup_directory(path):
    # Create a backup directory with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{path}_backup_{timestamp}"
    
    try:
        shutil.copytree(path, backup_path)
        print(f"Backup created at {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Failed to create backup: {e}")
        return None

def list_backups(path):
    backups = [d for d in os.listdir(path) if d.startswith(os.path.basename(path) + "_backup_")]
    if not backups:
        print("No backups found.")
    else:
        print("Available backups:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup}")
    return backups

def restore_backup(path, backup_name):
    backup_path = os.path.join(path, backup_name)
    if not os.path.exists(backup_path):
        print("Backup not found.")
        return

    # Clear the current directory
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

    # Copy the backup to the original location
    for item in os.listdir(backup_path):
        s = os.path.join(backup_path, item)
        d = os.path.join(path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    print(f"Restored backup from {backup_name}")

def delete_backup(path, backup_name):
    backup_path = os.path.join(path, backup_name)
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)
        print(f"Deleted backup {backup_name}")
    else:
        print("Backup not found.")

def organize_files_by_extension(path, files, exceptions):
    move_log = []  # List to store move operations for undo

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
    
    # Ask the user for the desired action
    action = input("Enter 'org' to organize files, 'undo' to undo the last organization, 'backup' to create a backup, 'restore' to restore from a backup, or 'delete' to delete a backup: ").strip().lower()
    
    if action == 'org':
        # Create a backup of the directory
        backup_path = backup_directory(full_path)
        
        # Define exceptions
        exceptions = ['move_log.json']
        if backup_path:
            exceptions.append(os.path.basename(backup_path))
        
        # List files in the directory
        files = list_files_in_directory(full_path)
        
        # Organize files by their extensions
        organize_files_by_extension(full_path, files, exceptions)
    elif action == 'undo':
        # Undo the last organization
        undo_last_organization(full_path)
    elif action == 'backup':
        # Create a backup of the directory
        backup_directory(full_path)
    elif action == 'restore':
        # List available backups
        backups = list_backups(os.path.dirname(full_path))
        if backups:
            # Ask the user to select a backup to restore
            choice = input("Enter the number of the backup to restore: ").strip()
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(backups):
                    restore_backup(full_path, backups[choice_index])
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    elif action == 'delete':
        # List available backups
        backups = list_backups(os.path.dirname(full_path))
        if backups:
            # Ask the user to select a backup to delete
            choice = input("Enter the number of the backup to delete: ").strip()
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(backups):
                    delete_backup(os.path.dirname(full_path), backups[choice_index])
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print("Invalid action. Please enter 'org', 'undo', 'backup', 'restore', or 'delete'.")
