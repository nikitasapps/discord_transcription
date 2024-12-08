# Discord Recordings - Multi track Auto-transcription
A python program that utilizes WhisperX in order to transcribe Multitrack Discord recordings created by bots such as "Craig-Bot".

The goal was to allow users to get transcripts from recordings of discord voice chats. This code can be utilized in two primary ways:
1. Take a single track, and transcribe all the spoken words.
2. Take several tracks from the same recording representing different speakers, and transcribe the full recording with the speakers tagged.

In order to transcribe and tag the speakers, I utilize both the "whisper" [https://github.com/openai/whisper] library from openAI, and the "whisperx" [https://github.com/m-bain/whisperX] library built on top of it.
- The single track transcription works best with the basic whisper library which can load the turbo model and then spits out the transcribed text directly.
- The multi track transcription works best with the whisperx library which allows better alignment of the individual audio tracks with their timestamps, allowing for the compiled transcript to be more accurate and reflect who is speaking.
- For an auto diarization, or tagging speakers automatically, from a single track mixed file, check out whisperx!


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
<do what you need to do in terminal!>
pyenv deactivate
```

### Requirements
If you have python and pip, just run the following with the virtual environment activated

```
pip install -r requirements.txt
```

## Usage

| arg    | Usage |
| -------- | ------- |
| -s, --single  | Completes a single track transcription over a multi track transcription |
| -f, --compiledfilename | The filename a multi track transcription will be outputted to within the text directory. |
| -p, --preloaded | Lets the multi track transcription utilize preloaded transcription segments over generating them dynamically. |
| -w, --basewhisper    | Performs the transcription with the base whisper library over the whisperx/fast-whisper libraries. Required to be on to get a text transcription from --single transcriptions. |
| -n, --nopatch | Does not patch together the compiled transcript during a multi track transcription, instead only outputting several independant text and .json files. Allows you to run the patching separately with --preloaded.|
| -g, --gpu | Run the whisperx transcription on a GPU rather than on CPU. Only turn on if you have cuda accessible, and float16 computation is doable on your machine. |
| -m, --modelsize | Change the whisperx transcription model. Defaults to "small.en", a medium sized model. "base.en" or "tiny.en" perform faster at the cost of accuracy, while "medium.en" and "large-v2.en" perform slower but more accurately. |

There is currently a TODO to handle files of type other than .mp3.

## Running Multitrack

- Given some multitrack file, export each track separately to their own .mp3 file. 
    - I primarily built this program to work with multitrack Audacity (.aup) files In Audacity (.aup files), go to File --> Export Audio. In the export dialog box, select .mp3 as the export type, and multiple files over "entire project". Then, store those files where you please.
- Move those .mp3 files (those you want to be included in the transcription) into the "multitrack_audio" folder within this directory
- Run the following command:

```
python3 main.py
```

This program will take some time to run, but will output the fully transcribed script to the text directory of multitrack_audio. The speakers will be tagged based on the names of the files of the tracks.

## Running Singletrack
- Given some audio file, export the audio to an .mp3 file (single track mixed)
    - In Audacity (.aup), go to File --> Export Audio. In the export dialog box, select .mp3 as the export type, and then "Entire Project". Export and store that .mp3 file where you please.
- Move that .mp3 file into the "singletrack_audio" folder within this directory.

- Run the following command:
```
python3 main.py --single --basewhisper
```

Once this program is finished running, it will output the fully transcribed text to the text directory of singletrack_audio.

NOTE: Include the --basewhisper tag to get this text output! otherwise, it will output only a .json file of the individual segments for a single track. This is a TODO to fix in a later iteration!