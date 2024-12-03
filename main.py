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
    # Temporarily disable backup functionality
    pass

def list_backups(path):
    backups = [d for d in os.listdir(path) if d.startswith("structure_backup_")]
    if not backups:
        print("No backups found.")
    else:
        print("Available backups:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup}")
    return backups

def restore_directory_structure(path, backup_name):
    backup_path = os.path.join(path, backup_name)
    if not os.path.exists(backup_path):
        print("Backup not found.")
        return

    # Clear the current directory except for the backup folder
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if item != backup_name:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    # Restore the directory structure from the backup
    for root, dirs, _ in os.walk(backup_path):
        relative_path = os.path.relpath(root, backup_path)
        restore_subdir = os.path.join(path, relative_path)
        for dir_name in dirs:
            os.makedirs(os.path.join(restore_subdir, dir_name), exist_ok=True)
    print(f"Restored directory structure from {backup_name}")

def delete_backup(path, backup_name):
    backup_path = os.path.join(path, backup_name)
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)
        print(f"Deleted backup {backup_name}")
    else:
        print("Backup not found.")

def organize_files_by_extension(path, files, exceptions):
    move_log = []  # List to store move operations for undo
    created_dirs = []  # List to store newly created directories

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
            move_log.append({'source': source, 'destination': destination})

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
        move_log = data.get('moves', [])
        created_dirs = data.get('created_dirs', [])

    for move in reversed(move_log):
        source = move['destination']
        destination = move['source']
        shutil.move(source, destination)
        print(f"Moved {os.path.basename(source)} back to original location.")

    # Remove directories that were created during the organization
    for dir_path in created_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Removed directory {dir_path}")

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
    
    # Check if the directory exists
    if not os.path.exists(full_path):
        print(f"Error: The directory '{full_path}' does not exist.")
    else:
        # Ask the user for the desired action
        action = input("Enter 'org' to organize files, 'undo' to undo the last organization, 'backup' to create a backup, 'restore' to restore from a backup, or 'delete' to delete a backup: ").strip().lower()
        
        if action == 'org':
            # Create a backup of the directory structure (currently disabled)
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
            # Create a backup of the directory structure (currently disabled)
            backup_directory_structure(full_path)
        elif action == 'restore':
            # List available backups
            backups = list_backups(full_path)
            if backups:
                # Ask the user to select a backup to restore
                choice = input("Enter the number of the backup to restore: ").strip()
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(backups):
                        restore_directory_structure(full_path, backups[choice_index])
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        elif action == 'delete':
            # List available backups
            backups = list_backups(full_path)
            if backups:
                # Ask the user to select a backup to delete
                choice = input("Enter the number of the backup to delete: ").strip()
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(backups):
                        delete_backup(full_path, backups[choice_index])
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        else:
            print("Invalid action. Please enter 'org', 'undo', 'backup', 'restore', or 'delete'.")
