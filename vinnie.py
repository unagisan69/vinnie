#!/usr/bin/env python3

import os
import sys
import glob
from mutagen.flac import FLAC

def are_all_files_24_bit(flac_files):
    for file_path in flac_files:
        audio = FLAC(file_path)
        if audio.info.bits_per_sample != 24:
            print(f"{file_path} is not 24-bit. Exiting.")
            return False
    return True
    
def get_metadata_from_flac(file_path):
    try:
        audio = FLAC(file_path)
        artist = audio["artist"][0] if "artist" in audio else "Unknown Artist"
        album = audio["album"][0] if "album" in audio else "Unknown Album"
        date = audio["date"][0] if "date" in audio else "Unknown Year"
        
        return artist, album, date
    except Exception as e:
        print(f"Error reading FLAC metadata from {file_path}: {e}")
        return None, None, None

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

def main(folder_path):
    # Glob all FLAC files in the given folder
    flac_files = glob.glob(os.path.join(folder_path, "*.flac"))
    
    if not flac_files:
        print("No FLAC files found in the specified folder.")
        return
    
    # Check if all FLAC files are 24-bit
    if not are_all_files_24_bit(flac_files):
        return
        
    # Read metadata from the first FLAC file (assuming all files in the album have consistent metadata)
    artist, album, year = get_metadata_from_flac(flac_files[0])
    
    if not artist or not album or not year:
        print("Unable to retrieve all necessary metadata. Exiting.")
        return
    
    # Rename the folder
    folder_path = os.path.abspath(folder_path).rstrip(os.sep)
    parent_folder = os.path.dirname(folder_path)
    new_folder_name = f"{artist} - {album} - {year} [24-Bit FLAC]"
    new_folder_path = os.path.join(parent_folder, new_folder_name)

    # If the target folder is nested within the source, move it up one directory
    if new_folder_path.startswith(folder_path):
        new_folder_path = os.path.join(os.path.dirname(parent_folder), new_folder_name)


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
