"""
Check current indexing status from log file
"""
import re
from datetime import datetime, timedelta
from pathlib import Path

log_file = Path("logs/full_qdrant_indexing.log")

if not log_file.exists():
    print("[ERROR] Log file not found:", log_file)
    exit(1)

print("[INFO] Reading log file:", log_file)
print()

# Read last 100 lines
with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    last_lines = lines[-100:]

# Extract latest progress info
progress_pattern = r'(\d+)/(\d+)'
success_pattern = r'�������: (\d+)'
failed_pattern = r'������: (\d+)'
eta_pattern = r'~(\d+) ���'

latest_progress = None
latest_success = None
latest_failed = None
latest_eta = None

for line in reversed(last_lines):
    if progress_pattern in line or '/' in line:
        match = re.search(progress_pattern, line)
        if match and not latest_progress:
            latest_progress = (int(match.group(1)), int(match.group(2)))

    if 'SUCCESS' in line or '�������' in line:
        match = re.search(r'(\d+)', line)
        if match and not latest_success:
            latest_success = int(match.group(1))

    if 'ETA' in line or '��������' in line:
        match = re.search(eta_pattern, line)
        if match and not latest_eta:
            latest_eta = int(match.group(1))

print("=" * 60)
print("CURRENT INDEXING STATUS")
print("=" * 60)

if latest_progress:
    current, total = latest_progress
    percent = (current / total * 100) if total > 0 else 0
    print(f"Progress:    {current}/{total} files ({percent:.1f}%)")
    print(f"Remaining:   {total - current} files")
else:
    print("Progress:    Unable to parse")

if latest_success is not None:
    print(f"Successful:  {latest_success} files")

if latest_failed is not None:
    print(f"Failed:      {latest_failed} files")

if latest_eta:
    eta_hours = latest_eta / 3600
    eta_time = datetime.now() + timedelta(seconds=latest_eta)
    print(f"ETA:         ~{eta_hours:.1f} hours (~{latest_eta} seconds)")
    print(f"Complete at: {eta_time.strftime('%Y-%m-%d %H:%M:%S')}")

print()

# Determine if process is still running
last_timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
last_timestamp = None

for line in reversed(last_lines):
    match = re.search(last_timestamp_pattern, line)
    if match:
        last_timestamp_str = match.group(1)
        last_timestamp = datetime.strptime(last_timestamp_str, '%Y-%m-%d %H:%M:%S')
        break

if last_timestamp:
    time_since_update = datetime.now() - last_timestamp
    print(f"Last update: {last_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time since:  {time_since_update.total_seconds():.0f} seconds ago")

    if time_since_update.total_seconds() > 300:
        print()
        print("[WARNING] No updates in 5+ minutes - process may be stuck!")
    elif time_since_update.total_seconds() > 120:
        print()
        print("[INFO] Process is slow but appears to be running")
    else:
        print()
        print("[OK] Process is actively running")

print()
print("=" * 60)
