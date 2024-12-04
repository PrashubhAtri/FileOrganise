import os
import json
import shutil

def undo_last_organization(path):
    log_file_path = os.path.join(path, 'move_log.json')
    
    if not os.path.exists(log_file_path):
        print("No move log found. Nothing to undo.")
        return

    with open(log_file_path, 'r') as log_file:
        data = json.load(log_file)
        move_log = data.get('moves', {})
        created_dirs_log = data.get('created_dirs', {})

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
    if latest_timestamp in created_dirs_log:
        for dir_path in created_dirs_log[latest_timestamp]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"Removed directory {dir_path}")

        # Remove the entry for the created directories
        del created_dirs_log[latest_timestamp]

    # Update the log file or delete it if empty
    if move_log or created_dirs_log:
        with open(log_file_path, 'w') as log_file:
            json.dump({'moves': move_log, 'created_dirs': created_dirs_log}, log_file)
    else:
        os.remove(log_file_path)
