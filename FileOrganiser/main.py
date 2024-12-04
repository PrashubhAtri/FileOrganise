import os
import json
from . import (
    undo_last_organization,
    organize_files_by_extension,
    backup_directory_structure,
    list_backups,
    restore_directory_structure,
    delete_backup
)

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

def load_move_log(path):
    log_file_path = os.path.join(path, 'move_log.json')
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            return json.load(log_file)
    return {'moves': {}, 'created_dirs': []}

def run_organiser():
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
        # Load the move log data
        data = load_move_log(full_path)
        
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
