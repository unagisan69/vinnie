# vinnie
Vinnie helps you rip vinyl. My goal is to make processing vinyl rips as simple as possible.

# Installation

First install mutagen and mktorrent if you don't already have them:
For macOS:
```
pip install mutagen
brew install mktorrent
```
Next make vinnie executable:
```
chmod +x vinnie.py
```
Lastly, set your Discogs API key which you can obtain here: https://www.discogs.com/settings/developers

# Usage
```
vinnie.py foldername
```
Vinnie first asks for the Discogs release ID for your album. (ex. the URL is https://www.discogs.com/release/1032187-UNKLE-Burn-My-Shadow then the release ID is 1032187). 

Vinnie then pulls the metadata for the album from Discogs and uses it to set the folder name, filenames, and tags for each track. Vinnie will then confirm that all FLAC files are 24-Bit. 

Next, Vinnie prompts you for audio equipment information in order to create a lineage.txt file which it adds to the new folder. Defaults can be set for this file so you can just press enter for each prompt.

Finally, Vinnie creates a torrent file for the folder using the announce URL set in the script.
