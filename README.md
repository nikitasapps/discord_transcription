# Discord Recordings - Multitrack Auto-transcription
A program that utilizes the WhisperX library to automatically transcribe discord recordings created by bots such as "Craig-Bot"

This program can be utilized in two primary ways:
1. **Single Track / Mixed Audio**: Trancribes all spoken words into a .txt file.
2. **Multiple Tracks**: Takes several tracks from the same recording, each representing a different speaker. Transcribes all spoken words, with the speaker of each word indicated.

## Notes
In order to transcribe and tag speakers, I utilize both the "whisper" [https://github.com/openai/whisper] library from OpenAI, and the "whisperx" [https://github.com/m-bain/whisperX] library built on top of it.
- The "Single Mixed Track" transcription works best with the basic whisper library. It utilizes the "turbo" model for both speed and accuracy to get the compiled text.
- The "Multi Track" transcription works best with the whisperx library. It first performs a basic transcription on each speakers individual audio track, and then runs each speakers audio segment's through whisperx's alignment pipeline. Once the segments are better aligned (I.E., have more accurate timestamps), a compiled transcript is created.
- For "Diarization" (automatically recognizing and tagging speakers) in a single mixed audio file, check out whisperX!

## Usage
| arg    | Usage |
| -------- | ------- |
| -s, --single  | Completes a single track transcription. |
| -f, --compiledfilename | The filename a multi track transcription will be outputted to within the text directory. |
| -p, --preloaded | Lets the multi track transcription utilize preloaded transcription segments over generating them dynamically. |
| -w, --basewhisper    | Performs the transcription with the base whisper library over the whisperx/fast-whisper libraries. Required to be on to get a text transcription from --single transcriptions. |
| -n, --nopatch | Does not patch together the compiled transcript during a multi track transcription, instead only outputting several independant text and .json files. Allows you to run the patching separately with --preloaded.|
| -g, --gpu | Run the whisperx transcription on a GPU rather than on CPU. Only turn on if you have cuda accessible, and float16 computation is doable on your machine. |
| -m, --modelsize | Change the whisperx transcription model. Defaults to "small.en", a medium sized model. "base.en" or "tiny.en" perform faster at the cost of accuracy, while "medium.en" and "large-v2.en" perform slower but more accurately. |

### Running Multitrack
1. Given some multitrack file, export each track separately to their own .mp3 file. 
    - I primarily built this program to work with multitrack Audacity (.aup) files In Audacity (.aup files), go to File --> Export Audio. In the export dialog box, select .mp3 as the export type, and multiple files over "entire project". Then, store those files where you please.
2. Move those .mp3 files (those you want to be included in the transcription) into the "multitrack_audio" folder within this directory
3. Run the following command:
```
python3 main.py
```
This program will take some time to run, but will output the fully transcribed script to the text directory of multitrack_audio. The speakers will be tagged based on the names of the files of the tracks.

### Running Singletrack
1. Given some audio file, export the audio to an .mp3 file (single track mixed)
    - In Audacity (.aup), go to File --> Export Audio. In the export dialog box, select .mp3 as the export type, and then "Entire Project". Export and store that .mp3 file where you please.
2. Move that .mp3 file into the "singletrack_audio" folder within this directory.
3. Run the following command:
```
python3 main.py --single --basewhisper
```
Once this program is finished running, it will output the fully transcribed text to the text directory of singletrack_audio.

## Setup

### Python Version - PyEnv
This project was built on Python 3.9.20, and may not work on subsequent versions due to incompatabilities with numpy.

I'd recommend a python version manager to install the correct version of python. I utilize 'pyenv'[https://github.com/pyenv/pyenv] for this.

As an example with MacOS and Homebrew [https://brew.sh/]:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" # Install homebrew
brew install pyenv # install pyenv, remember to setup your shell!

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

Once you have this installed, you can create a virtual environment as so:

```
echo '3.9.20' > .python-version
pyenv virtual environment whisperx
```

Run the activate command, and deactivate commands whenever you need to install/utilize this code!
```
pyenv activate whisperx
<do what you need to do in terminal, run program>
pyenv deactivate
```

### Requirements
If you have python and pip, just run the following with the virtual environment activated

```
pip install -r requirements.txt
```

## TODO
* Handle files of type other than .mp3
* Allow user to specify which dir/file to get audio from. Should be an arguement that is passed to the singletrack/multitrack.
* Currently, the singletrack isn't utilizing whisper by default. The behavior should be altered to do so.
