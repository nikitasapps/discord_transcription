import os, shutil
import json

"""
    Filesystem helpers
"""
def get_filenames(directory, file_type = ".mp3"):
    filenames = []
    for item in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, item)) and (os.path.splitext(item)[1] == file_type):
            filenames.append(item)
    return filenames

def create_dirs(dirs, log = False):
    for path in dirs:
        try:
            os.mkdir(path)
            if(log):
                print(f"Directory '{path}' created successfully.")
        except FileExistsError:
            if(log):
                print(f"Directory '{path}' already exists.")

def clear_dirs(dirs):
    for folder in dirs:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

def setup_audio_dir(directory, clear = True):
    print("Cleaning up audio directories...")
    curr_dir_path = os.path.dirname(os.path.realpath(__file__))
    audio_dir = curr_dir_path + directory
    segment_dir = audio_dir + "/segments"
    text_dir = audio_dir + "/text"
    
    create_dirs([audio_dir, segment_dir, text_dir])
    if(clear):
        clear_dirs([segment_dir, text_dir])

    print("Finished setting up audio directories!\n")
    return audio_dir, segment_dir, text_dir


"""
Multitrack Helpers
"""
def format_segment(speaker, text, start, end):
    seg = {}
    seg["speaker"] = speaker
    seg["text"] = text
    seg["start"] = start
    seg["end"] = end
    return seg

def load_tagged_segments(segment_dir):
    segment_filenames = get_filenames(directory=segment_dir, file_type=".json")
    if(len(segment_filenames) == 0):
        print("WARN: You have no files in {} to preload.".format(segment_dir))
    
    all_segments = []
    for file in segment_filenames:
        filepath = os.path.join(segment_dir, file)
        print(filepath)
        with open(filepath, "r") as json_file:
            tagged_segments = json.loads(json_file.read())
        all_segments.extend(tagged_segments)
    return all_segments