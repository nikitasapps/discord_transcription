from .utils import *
import whisper
import whisperx
import json
"""
    Model helper function
"""
WHISPERX_MODEL_SIZE =  "small.en" # "base.en"
WHISPERX_DEVICE = "cpu" # "cuda"
WHISPERX_COMPUTE_TYPE = "float32" # change to "int8" if low on GPU mem (may reduce accuracy) # "float16"
WHISPERX_BATCH_SIZE = 16 # reduce if low on GPU mem
WHISPERX_MODEL = "whisperx_model"

def init_whisperx(gpu = True, model_size = "small.en"):
    if(gpu):
        WHISPERX_DEVICE = "cuda"
        WHISPERX_COMPUTE_TYPE = "float16"
    else:
        WHISPERX_DEVICE = "cpu"
        WHISPERX_COMPUTE_TYPE = "float32"
    
    WHISPERX_MODEL_SIZE = model_size

def load_transcription_model(use_whisperx):
    model = None
    if (use_whisperx):
        device = WHISPERX_DEVICE
        compute_type = WHISPERX_COMPUTE_TYPE
        model_dir = WHISPERX_MODEL

        print("Loading whisperX transcription model...")
        model = whisperx.load_model(WHISPERX_MODEL_SIZE, device, compute_type=compute_type, download_root=model_dir)
    else:
        print("Loading whisper transcription model...")
        model = whisper.load_model("turbo")
    
    return model

"""
    Transcription functions.
"""
def transcribe_whisper(model, filepath, text_output):
    print("Transcribing filepath with Whisper: {}".format(filepath))
    result = model.transcribe(filepath)

    print("Whisper: Saving text...")
    f = open(text_output, "w")
    f.write(result["text"])
    f.close()

    print("Whisper: Finished getting segments.\n")
    return result["segments"]

def transcribe_whisperx(model, filepath, text_output):
    print("WhisperX: Loading audio... {}".format(filepath))
    audio = whisperx.load_audio(filepath)

    print("Transcribing filepath with WhisperX: {}".format(filepath))
    result = model.transcribe(audio, batch_size=WHISPERX_BATCH_SIZE)

    # print("WhisperX: Saving text...")
    # f = open(text_output, "w")
    # f.write(result["text"])
    # f.close()

    print("WhisperX: Aligning output...")
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=WHISPERX_DEVICE)
    result = whisperx.align(result["segments"], model_a, metadata, audio, WHISPERX_DEVICE, return_char_alignments=False)

    print("WhisperX: Finished aligning segments.\n")
    return result["segments"]

def transcribe_file(filename, use_whisperx, audio_dir, text_dir, segment_dir, model = None, dump = True):
    if(model == None):
        model = load_transcription_model(use_whisperx)
    
    filepath = os.path.join(audio_dir, filename)
    filestem = os.path.splitext(filename)[0]

    print("Transcribing file: {}".format(filepath))
    output_filename = os.path.join(text_dir, filestem + ".txt")
    segments = []
    if(use_whisperx):
        segments = transcribe_whisperx(model, filepath, output_filename)
    else:
        segments = transcribe_whisper(model, filepath, output_filename)
    print("Finished transcribing file in {}.\n".format(output_filename))
    
    if(dump):
        print("Dumping segments for {}".format(filename))
        segment_output = os.path.join(segment_dir, filestem + ".json")
        with open(segment_output, "w") as json_file:
            json.dump(segments, json_file)
        print("Finished dumping segments in {}.\n".format(segment_output))

    return segments

"""
    Multitrack Diarazation Helpers
"""
def tag_file_with_speakers(segments, filename, segment_dir):
    tagged_segments = []
    speaker_name = os.path.splitext(filename)[0]
    segment_output = os.path.join(segment_dir, speaker_name + ".json")

    print("Tagging segments for speaker {}".format(speaker_name))
    for segment in segments:
        t_s = format_segment(speaker=speaker_name, text=segment["text"], start=segment["start"], end=segment["end"])
        tagged_segments.append(t_s)
    print("Finished tagging segments for speaker {}\n".format(speaker_name))

    print("Dumping segments for {}".format(filename))
    with open(segment_output, "w") as json_file:
	    json.dump(tagged_segments, json_file)
    print("Finished dumping segments in {}.\n".format(segment_output))

    return tagged_segments

def transcribe_and_tag_file_list(audio_filenames, use_whisperx, audio_dir, text_dir, segment_dir):
    model = load_transcription_model(use_whisperx)

    all_segments = []
    for filename in audio_filenames:
        # filename is speakername.mp3
        segments = transcribe_file(filename, use_whisperx, audio_dir, text_dir, segment_dir, model = model, dump = False)
        tagged_segments = tag_file_with_speakers(segments, filename, segment_dir)
        all_segments.extend(tagged_segments)

    return all_segments

def patch_together_segments(all_segments):
    print("Patch: Sorting segments...")
    sorted_segments = sorted(all_segments, key=lambda x: (x['start'], x['end']))

    print("Patch: Patching together segments...")
    patched_segments = []

    current_speaker = sorted_segments[0]["speaker"]
    current_text = sorted_segments[0]["text"]
    current_start = sorted_segments[0]["start"]
    current_end = sorted_segments[0]["end"]

    for segment in sorted_segments[1:]:
        next_speaker = segment["speaker"]
        if next_speaker == current_speaker:
            current_text = current_text + " " + segment["text"]
            current_end = segment["end"]
        if next_speaker != current_speaker:
            p_s = format_segment(speaker=current_speaker, text=current_text, start=current_start, end=current_end)
            patched_segments.append(p_s)

            current_speaker = segment["speaker"]
            current_text = segment["text"]
            current_start = segment["start"]
            current_end = segment["end"]

    # Handling final segment
    p_s = format_segment(speaker=current_speaker, text=current_text, start=current_start, end=current_end)
    patched_segments.append(p_s)

    print("Patch: Finished patching together segments...\n")
    return patched_segments

def compile_full_transcript(segments, output_filename, text_dir):
    print("Compile: Compiling full transcript...")
    output_filepath = os.path.join(text_dir, output_filename)
    f_compiled = open(output_filepath, "w")
    for segment in segments:
        f_compiled.write("{} [{},{}]: {}\n".format(segment["speaker"],segment["start"], segment["end"], segment["text"]))
    f_compiled.close()
    print("Compile: Finished compiling transcript at {}!\n".format(output_filepath))

"""
    Handling a multitrack transcription
"""
def multitrack(is_preloaded, use_whisperx, patch_together, output_filename = "compiled_multitrack.txt"):
    MULTITRACK_DIR = "/multitrack_audio"

    all_segments = []
    if(is_preloaded):
        MULTITRACK_AUDIO_DIR, MULTITRACK_SEGMENT_DIR, MULTITRACK_TEXT_DIR = setup_audio_dir(MULTITRACK_DIR, clear = False)
        
        print("Loading multitrack segments from file...")
        all_segments = load_tagged_segments(segment_dir = MULTITRACK_SEGMENT_DIR)
        print("Loaded segments from file.\n")
    else:
        # Setup...
        MULTITRACK_AUDIO_DIR, MULTITRACK_SEGMENT_DIR, MULTITRACK_TEXT_DIR = setup_audio_dir(MULTITRACK_DIR)

        # Get filenames
        audio_filenames = get_filenames(directory = MULTITRACK_AUDIO_DIR, file_type = ".mp3")
        if len(audio_filenames) == 0:
            print("No files provided in multitrack dir: {}. Ending...\n".format(MULTITRACK_AUDIO_DIR))
            return

        # Performing transcriptions...
        print("Transcribing all files: {}".format(audio_filenames))
        all_segments = transcribe_and_tag_file_list(
            audio_filenames = audio_filenames,
            use_whisperx = use_whisperx,
            audio_dir = MULTITRACK_AUDIO_DIR,
            text_dir = MULTITRACK_TEXT_DIR,
            segment_dir = MULTITRACK_SEGMENT_DIR
        )
        print("Finished transcribing {}! Results in {}.\n".format(audio_filenames, MULTITRACK_SEGMENT_DIR))

    if(patch_together):
        print("Beginning patching segments for full transcript...")
        patched_segments = patch_together_segments(all_segments)
        compile_full_transcript(patched_segments, output_filename, text_dir=MULTITRACK_TEXT_DIR)
        print("Finished transcript for {}! Results in {}.\n".format(output_filename, MULTITRACK_TEXT_DIR))
    

"""
    Handling a singletrack transcription
"""
def singletrack(use_whisperx):
    # Setup Directories
    SINGLETRACK_DIR = "/singletrack_audio"
    SINGLETRACK_AUDIO_DIR, SINGLETRACK_SEGMENT_DIR, SINGLETRACK_TEXT_DIR = setup_audio_dir(SINGLETRACK_DIR)

    # Get filename
    file_options = get_filenames(directory = SINGLETRACK_AUDIO_DIR, file_type = ".mp3")
    if(len(file_options) == 0):
        print("No audio file provided in {}. Ending...\n".format(SINGLETRACK_AUDIO_DIR))
        return
    elif(len(file_options) > 1):
        print("More than one file provided in /singletrack_audio. Using first file...")
    filename = file_options[0]

    # Transcribe file...
    print("Transcribing {}...".format(filename))
    transcribe_file(
        filename = filename, 
        use_whisperx = use_whisperx, 
        audio_dir = SINGLETRACK_AUDIO_DIR,
        text_dir = SINGLETRACK_TEXT_DIR, 
        segment_dir = SINGLETRACK_SEGMENT_DIR
    )
    print("Finished transcribing {}! Results in {}.\n".format(filename, SINGLETRACK_TEXT_DIR))

    