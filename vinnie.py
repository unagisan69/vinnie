#!/usr/bin/env python3
import os
import sys
import glob
from mutagen.flac import FLAC
import requests

DISCOGS_API_KEY = "xxxx"
discogs_id = input("Enter Discogs release ID: ")

def fetch_discogs_data(discogs_id):
    url = f"https://api.discogs.com/releases/{discogs_id}"
    headers = {
        "User-Agent": "VinnieScript/1.0 vinnieboy",
        "Authorization": f"Discogs key={DISCOGS_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from Discogs: {response.status_code}")
        return None

def extract_discogs_info(data):
    artist = data['artists'][0]['name']
    album = data['title']
    year = data['year']
    genre = ', '.join(data['genres'])

    tracklist = data['tracklist']
    tracks = [{'title': track['title'], 'position': track['position']} for track in tracklist]

    return artist, album, year, genre, tracks

def set_flac_metadata_from_discogs(flac_file, artist, album, year, genre, tracks):
    audio = FLAC(flac_file)
    track_num = os.path.basename(flac_file).split(' - ')[0]
    for track in tracks:
        if track['position'] == track_num:
            audio["title"] = track['title']
            break
    audio["artist"] = artist
    audio["album"] = album
    audio["date"] = str(year)
    audio["genre"] = genre
    audio.save()

def are_all_files_24_bit(flac_files):
    for file_path in flac_files:
        audio = FLAC(file_path)
        if audio.info.bits_per_sample != 24:
            print(f"{file_path} is not 24-bit. Exiting.")
            return False
    return True

def get_lineage():
    # Define default values
    default_vinyl = "VG+"
    default_turntable = "LP120xUSB"
    default_cartridge = "VM540ML"
    default_adc = "Yamaha RX-V3000"
    default_interface = "Scarlet Focusrite 2i2"
    default_clean = "Boundless"
    default_soft = "Audition > Izotope RX 10"
    default_ripped = "Ripped by unagi"

    # Prompt user for inputs
    print("~~ Lineage Generator ~~")
    vinyl = input(f"Vinyl [{default_vinyl}]: ") or default_vinyl
    turntable = input(f"Turntable [{default_turntable}]: ") or default_turntable
    cartridge = input(f"Cartridge [{default_cartridge}]: ") or default_cartridge
    adc = input(f"ADC [{default_adc}]: ") or default_adc
    interface = input(f"Interface [{default_interface}]: ") or default_interface
    clean = input(f"Clean [{default_clean}]: ") or default_clean
    soft = input(f"Soft [{default_soft}]: ") or default_soft
    ripped = input(f"Ripped by [{default_ripped}]: ") or default_ripped

    lineage_data = f"""-------
LINEAGE
-------
Vinyl: {vinyl}
Turntable: {turntable}
Cartridge: {cartridge}
Preamp / ADC: {adc}
Interface: {interface}
Clean: {clean}
Soft: {soft}
{ripped}
"""

    return lineage_data

def track_num_to_letter(track_num):
    return chr(64 + int(track_num))

def main(folder_path):
    discogs_data = fetch_discogs_data(discogs_id)
    if not discogs_data:
        print("Error fetching data from Discogs. Exiting.")
        return

    artist, album, year, genre, tracks = extract_discogs_info(discogs_data)
    flac_files = glob.glob(os.path.join(folder_path, "*.flac"))
    if not flac_files:
        print("No FLAC files found in the specified folder.")
        return

    if not are_all_files_24_bit(flac_files):
        return

    for idx, flac_file in enumerate(sorted(flac_files), 1):
        set_flac_metadata_from_discogs(flac_file, artist, album, year, genre, tracks)
        track_letter = track_num_to_letter(idx)
        for track in tracks:
            if track['position'] == track_letter:
                new_filename = f"{track_letter} - {track['title']}.flac"
                new_file_path = os.path.join(os.path.dirname(flac_file), new_filename)
                os.rename(flac_file, new_file_path)
                break

    folder_path = os.path.abspath(folder_path).rstrip(os.sep)
    parent_folder = os.path.dirname(folder_path)
    new_folder_name = f"{artist} - {album} - {year} [24-Bit FLAC]"
    new_folder_path = os.path.join(parent_folder, new_folder_name)
    os.rename(folder_path, new_folder_path)
    print(f"Folder renamed to: {new_folder_name}")

    lineage = get_lineage()
    with open(os.path.join(new_folder_path, "lineage.txt"), "w") as f:
        f.write(lineage)

    print(f"Saved lineage details to {new_folder_path}/lineage.txt")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: vinnie.py <folder_path>")
        sys.exit(1)
    main(sys.argv[1])
