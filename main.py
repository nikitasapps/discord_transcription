import argparse
from src.transcribe import init_whisperx, multitrack, singletrack

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--preloaded", action='store_true', default=False, help="Use preloaded segments")
parser.add_argument("-n", "--nopatch", action='store_true', default=False, help="Don't patch together segments")
parser.add_argument("-w", "--basewhisper", action='store_true', default=False, help="Use original whisper over whisperx and fast-whisper")
parser.add_argument("-s", "--single", action='store_true', default=False, help="Handle a single track with whisper instead")
parser.add_argument("-f", "--compiledfilename", type=str, default="compiled_multitrack.txt", help="Filename for output transcription.")
parser.add_argument("-g", "--gpu", action='store_true', default=False, help="Utilize GPU instead of CPU")
parser.add_argument("-m", "--modelsize", type=str, default="small.en", help="Whisper model type, ex. base.en, large-v2")

if __name__=="__main__":
    args = parser.parse_args()
    multi = not args.single
    is_preloaded = args.preloaded
    use_whisperx = not args.basewhisper
    patch_together = not args.nopatch
    compiled_filename = args.compiledfilename

    gpu = args.gpu
    model_size = args.modelsize

    if(use_whisperx):
        init_whisperx(gpu = gpu, model_size = model_size)
    
    if(multi):
        multitrack(
            is_preloaded = is_preloaded,
            use_whisperx = use_whisperx,
            patch_together = patch_together,
            output_filename = compiled_filename
        )
    else:
        singletrack(
            use_whisperx = use_whisperx,
        )