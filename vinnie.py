#!/usr/bin/env python3
import os
import sys
import glob
from mutagen.flac import FLAC
import requests
import subprocess

ANNOUNCE_URL = "http://your.tracker.url/announce"  # Replace with your tracker's announce URL
DISCOGS_API_KEY = "xxxx" # Replace with your API key
TORRENT_OUTPUT_FOLDER = "/Users/unagi/Desktop"  # Optional. Change this to a path like "/path/to/torrents/" if desired

def check_and_convert_files(folder_path):
    wav_files = glob.glob(os.path.join(folder_path, "*.wav"))
    flac_files = glob.glob(os.path.join(folder_path, "*.flac"))

    if wav_files:  # Convert WAV files to 24-bit FLAC
        for wav_file in wav_files:
            output_flac_file = os.path.splitext(wav_file)[0] + ".flac"
            subprocess.run([
                "ffmpeg", "-i", wav_file, "-sample_fmt", "s32", "-ar", "96000", output_flac_file
            ], check=True)
            os.remove(wav_file)  # Remove the original WAV file after conversion

    if flac_files:  # Confirm FLAC files are 24-bit
        for flac_file in flac_files:
            audio = FLAC(flac_file)
            if audio.info.bits_per_sample != 24:
                raise ValueError(f"{flac_file} is not 24-bit. Please ensure all FLAC files are 24-bit.")

def create_torrent(folder_path):
    output_path_option = []
    if TORRENT_SAVE_PATH:
        torrent_file_path = os.path.join(TORRENT_SAVE_PATH, f"{os.path.basename(folder_path)}.torrent")
        output_path_option = ["-o", torrent_file_path]
    try:
        result = subprocess.run(["mktorrent", "-p", "-a", ANNOUNCE_URL] + output_path_option + [folder_path], check=True, text=True, capture_output=True)
        if result.returncode == 0:
            print(f"Successfully created torrent for {folder_path}.")
        else:
            print("Error creating torrent:", result.stderr)
    except Exception as e:
        print(f"Error executing mktorrent: {e}")
        
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
    
def determine_track_format(tracks):
    """
    Determine if tracks from Discogs use numbers or letters.
    Returns: "number" or "letter"
    """
    first_track = tracks[0]['position']
    if first_track.isdigit():
        return "number"
    elif len(first_track) == 1:  # Assuming single letter (e.g., A, B, C)
        return "letter"
    else:
        print(f"Unexpected track format: {first_track}. Defaulting to 'number'.")
        return "number"

def letter_to_number(letter):
    """Convert A to 1, B to 2, etc."""
    return ord(letter) - ord('A') + 1
    
def set_flac_metadata_from_discogs(flac_file, artist, album, year, genre, tracks, idx):
    audio = FLAC(flac_file)
    
    if idx >= len(tracks):
        print(f"Warning: No matching track title found in Discogs data for track index {idx}")
        return

    track = tracks[idx]

    if track['position'].isdigit():
        track_num = track['position']
    else:
        # Check if the track position is of format like A1, B2, etc.
        if len(track['position']) > 1 and track['position'][1:].isdigit():
            track_num = track['position'][1:]
        else:
            track_num = str(ord(track['position'][0]) - 64)  # Convert first letter to number

    audio["title"] = track['title']
    audio["tracknumber"] = track_num
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
    # Check if files are 24-bit FLAC or convert WAV to 24-bit FLAC
    check_and_convert_files(folder_path)

    # Fetch Discogs data
    discogs_data = fetch_discogs_data(discogs_id)
    if not discogs_data:
        print("Error fetching data from Discogs. Exiting.")
        return

    artist, album, year, genre, tracks = extract_discogs_info(discogs_data)

    # Glob all FLAC files in the given folder
    flac_files = glob.glob(os.path.join(folder_path, "*.flac"))
    if not flac_files:
        print("No FLAC files found in the specified folder.")
        return

    # Update FLAC metadata and rename file
    for idx, flac_file in enumerate(sorted(flac_files)):
        set_flac_metadata_from_discogs(flac_file, artist, album, year, genre, tracks, idx)
    
        track = tracks[idx]
        if track['position'].isdigit():
            track_num = track['position']
        else:
            # Check if the track position is of format like A1, B2, etc.
            if len(track['position']) > 1 and track['position'][1:].isdigit():
                track_num = track['position'][1:]
            else:
                track_num = str(ord(track['position'][0]) - 64)  # Convert first letter to number

        new_filename = f"{track_num} - {track['title']}.flac"
        new_file_path = os.path.join(os.path.dirname(flac_file), new_filename)
        os.rename(flac_file, new_file_path)

    # Rename the folder
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

    # Create torrent
    mktorrent_cmd = f"mktorrent -l 18 -a {ANNOUNCE_URL} -p -o \"{TORRENT_OUTPUT_FOLDER if TORRENT_OUTPUT_FOLDER else '.'}/{new_folder_name}.torrent\" \"{new_folder_path}\""
    os.system(mktorrent_cmd)
    print(f"Torrent created for {new_folder_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: vinnie.py <folder_path>")
        sys.exit(1)
    main(sys.argv[1])
