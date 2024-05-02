import subprocess
import json
from datetime import datetime

def parse_linux_updates(output):
    updates = []
    lines = output.splitlines()
    for line in lines[1:]:  # Skip the header line
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            severity = parts[1]
            updates.append({'name': name, 'severity': severity})
    return updates

def parse_macos_updates(output):
    updates = []
    lines = output.splitlines()
    for line in lines:
        parts = line.split(None, 1)
        if len(parts) == 2:
            name = parts[0]
            date_str = parts[1].strip()
            if date_str:
                released_date = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                released_date = None
            updates.append({'name': name, 'released_date': released_date})
    return updates

def parse_windows_updates(output):
    updates = []
    lines = output.splitlines()
    for line in lines:
        parts = line.split(',')
        if len(parts) >= 3:
            name = parts[0]
            severity = parts[1]
            released_date_str = parts[2]
            if released_date_str.lower() != 'n/a':
                released_date = datetime.strptime(released_date_str, '%m/%d/%Y')
            else:
                released_date = None
            updates.append({'name': name, 'severity': severity, 'released_date': released_date})
    return updates

def check_linux_updates():
    updates = []
    try:
        result = subprocess.run(['apt', 'update'], capture_output=True, text=True)
        subprocess.run(['apt', 'list', '--upgradable'])
        updates_output = subprocess.run(['apt', 'list', '--upgradable'], capture_output=True, text=True).stdout
        updates = parse_linux_updates(updates_output)
    except FileNotFoundError:
        pass
    try:
        result = subprocess.run(['yum', 'check-update'], capture_output=True, text=True)
        updates = parse_linux_updates(result.stdout)
    except FileNotFoundError:
        pass
    return updates

def check_windows_updates():
    updates = []
    try:
        result = subprocess.run(['powershell', 'Get-WindowsUpdate'], capture_output=True, text=True)
        updates = parse_windows_updates(result.stdout)
    except FileNotFoundError:
        pass
    return updates

def check_macos_updates():
    updates = []
    try:
        result = subprocess.run(['softwareupdate', '-l'], capture_output=True, text=True)
        updates = parse_macos_updates(result.stdout)
    except FileNotFoundError:
        pass
    return updates

def main():
    updates = []
    try:
        updates = check_linux_updates()
    except Exception:
        try:
            updates = check_windows_updates()
        except Exception:
            try:
                updates = check_macos_updates()
            except Exception:
                print("Unsupported operating system")
                return

    if updates:
        print(json.dumps(updates, indent=4))
    else:
        print("No updates found")

if __name__ == "__main__":
    main()
