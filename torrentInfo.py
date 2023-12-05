# Description: This script parses a torrent file and extracts relevant information from it.

import os               # Operating system-specific functions (e.g., working with file paths)
import json             # JSON encoding and decoding
import csv              # CSV file reading and writing
import bencodepy        # Bencoding (serialization format used in BitTorrent)

def parse_torrent_file(file_path):
    try:
        with open(file_path, 'rb') as torrent_file:
            # Parse the torrent file using the bencode library
            torrent_data = bencodepy.decode(torrent_file.read())

        # Extract relevant information from the parsed data
        if b'length' in torrent_data[b'info']:
            # Single-file torrent
            torrent_info = {
                "file_name": torrent_data[b'info'][b'name'].decode('utf-8'),
                "file_size": torrent_data[b'info'][b'length'],
                "total_size": torrent_data[b'info'][b'length'],
                "total_no_pieces": calculate_number_of_pieces(torrent_data[b'info'][b'length'], torrent_data[b'info'][b'piece length']),
                "piece_length": torrent_data[b'info'][b'piece length'],
                "pieces": torrent_data[b'info'][b'pieces'].hex(),
                "trackers": [tracker.decode('utf-8') for tracker in torrent_data.get(b'announce-list', [torrent_data[b'announce']])[0]]
            }
        else:
            # Multi-file torrent
            total_size = 0
            files = []
            for file_info in torrent_data[b'info'][b'files']:
                # Join the file path parts and decode from bytes to UTF-8
                file_path = os.path.join(*[part.decode('utf-8') for part in file_info[b'path']])
                files.append({
                    "file_path": file_path,
                    "file_size": file_info[b'length']
                })
                total_size += file_info[b'length']

            number_of_pieces = calculate_number_of_pieces(total_size, torrent_data[b'info'][b'piece length'])

            torrent_info = {
                "files": files,
                "piece_length": torrent_data[b'info'][b'piece length'],
                "total_size": total_size,
                "number_of_pieces": number_of_pieces,
                "pieces": torrent_data[b'info'][b'pieces'].hex(),
                "trackers": [tracker.decode('utf-8') for tracker in torrent_data.get(b'announce-list', [torrent_data[b'announce']])[0]]
            }

        return torrent_info
    except Exception as e:
        print(f"Error parsing the torrent file: {e}")
        return None

def save_to_json(data, json_file):
    try:
        with open(json_file, 'w') as outfile:
            # Save the extracted information to a JSON file
            json.dump(data, outfile, indent=4)
        print(f"Torrent information saved to {json_file}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")

def save_to_csv(data, csv_file):
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            # Determine the field names from the data (dictionary or list of dictionaries)
            fieldnames = data.keys() if isinstance(data, dict) else data[0].keys()
            
            # Create a CSV writer with the specified field names
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header to the CSV file
            writer.writeheader()
            
            # Write data to the CSV file
            if isinstance(data, dict):
                writer.writerow(data)
            else:
                writer.writerows(data)
            
        print(f"Torrent information saved to {csv_file}")
    except Exception as e:
        print(f"Error saving to CSV file: {e}")

def calculate_number_of_pieces(file_size, piece_length):
    return (file_size + piece_length - 1) // piece_length

def main():
    # Specify the path to the torrent file in the Downloads folder
    downloads_folder = os.path.expanduser('~') + '/Downloads'
    torrent_file_name = input("Enter torrent file name: ") + ".torrent"
    torrent_file_path = os.path.join(downloads_folder, torrent_file_name)

    if os.path.exists(torrent_file_path):
        # Parse the torrent file
        torrent_info = parse_torrent_file(torrent_file_path)

        if torrent_info:
            # Specify the paths for the JSON and CSV output files
            json_output_file = input("Enter JSON output file name: ") + ".json"
            csv_output_file = input("Enter CSV output file name: ") + ".csv"

            # Save the extracted information to a JSON file
            save_to_json(torrent_info, json_output_file)

            # Save the extracted information to a CSV file
            save_to_csv(torrent_info, csv_output_file)
    else:
        print(f"Torrent file not found at {torrent_file_path}")

if __name__ == "__main__":
    main()

