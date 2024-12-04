import os
import json
import shutil
from datetime import datetime

def backup_directory_structure(path):
    # Generate a timestamp for the current backup session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_log = {}
    created_dirs = []

    # Traverse the directory structure
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            # Store the same path for both old and new paths
            backup_log[file] = [file_path, file_path]

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            created_dirs.append(dir_path)

    # Load existing move log or create a new one
    log_file_path = os.path.join(path, 'move_log.json')
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            data = json.load(log_file)
    else:
        data = {'moves': {}, 'created_dirs': {}}

    # Add the backup log and created directories to the move log
    data['moves'][timestamp] = backup_log
    data['created_dirs'][timestamp] = created_dirs

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
        created_dirs_log = data.get('created_dirs', {})

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

    # Remove any extra created directories
    if timestamp in created_dirs_log:
        for dir_path in created_dirs_log[timestamp]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"Removed directory {dir_path}")

    # Remove the entry for the restored session
    del move_log[timestamp]
    del created_dirs_log[timestamp]

    # Update the log file or delete it if empty
    if move_log or created_dirs_log:
        with open(log_file_path, 'w') as log_file:
            json.dump({'moves': move_log, 'created_dirs': created_dirs_log}, log_file)
    else:
        os.remove(log_file_path)

def delete_backup(path, timestamp):
    log_file_path = os.path.join(path, 'move_log.json')
    if not os.path.exists(log_file_path):
        print("No move log found. Cannot delete backup.")
        return

    with open(log_file_path, 'r') as log_file:
        data = json.load(log_file)
        move_log = data.get('moves', {})
        created_dirs_log = data.get('created_dirs', {})

    if timestamp not in move_log:
        print(f"No backup found for timestamp {timestamp}.")
        return

    # Delete the backup entry
    del move_log[timestamp]
    del created_dirs_log[timestamp]
    print(f"Deleted backup from {timestamp}")

    # Update the log file or delete it if empty
    if move_log or created_dirs_log:
        with open(log_file_path, 'w') as log_file:
            json.dump({'moves': move_log, 'created_dirs': created_dirs_log}, log_file)
    else:
        os.remove(log_file_path)
