"""Script to add symlinks for all alignment files in the database."""
import os
import sqlite3

db_path = '/pycom1data/static/downloads/pycom.db'
source_path = '/pycom1data/data/aln_data'
target_path = '/pycom1data/data/aln'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT entryId, sequence FROM entry')
entries = cursor.fetchall()

# Map sequences to entries and vice versa
entry_to_sequence = {entry_id: sequence for entry_id, sequence in entries}
sequence_to_entries = {sequence: [] for _, sequence in entries}
for entry_id, sequence in entries:
    sequence_to_entries[sequence].append(entry_id)

if not os.path.exists(target_path):
    os.makedirs(target_path)

count = 0

# Process entries
for current_entry_id, sequence in entries:
    list_of_entries = sequence_to_entries[sequence]
    matched_entry = next(
        (entry for entry in list_of_entries if os.path.exists(os.path.join(source_path, f'{entry}.aln'))), None)

    if matched_entry is None:
        print(f'No match for {current_entry_id}, {sequence}')
        continue

    source_file = os.path.join(source_path, f'{matched_entry}.aln')
    target_file = os.path.join(target_path, f'{current_entry_id}.aln')

    # Create symlinks
    os.symlink(source_file, target_file)
    os.symlink(source_file, os.path.join(target_path, f'{current_entry_id}'))

    count += 1
    if count % 10000 == 0:
        print(count)
