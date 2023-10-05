# vinnie
Vinnie helps you rip vinyl. My goal is to make processing vinyl rips as simple as possible.

# Installation

First install mutagen if you don't already have it:
```
pip install mutagen
```
Next make vinnie executable:
```
chmod +x vinnie.py
```
Lastly, set you discogs API key https://www.discogs.com/settings/developers

# Usage
```
vinnie.py foldername
```

Vinnie relies on mutagen to first check the given folder for FLAC files, then confirm all FLAC files are 24-bit, next the metadata of the files is ready to set the folder name to:

"Artist Name - Album Name - Release Year - [24-Bit FLAC]"

Finally, Vinnie prompts you for audio equipment information in order to create a lineage.txt file which it adds to the new folder. Defaults can be set for this file so you can just press enter for each prompt.
