import os
import sys
from pathlib import Path
import json

from tqdm import tqdm

def replace_bar_with_dash(dir: str | os.PathLike, dry_run=True):
    """
    Recursively replaces all occurrences in a file of the character '|' with '-'.
    """
    dir = Path(dir).resolve()
    for dirpath, dirnames, filenames in dir.walk(top_down=True):
        # Directories
        first = True
        for i, file in enumerate(dirnames):
            # Avoid processing for files that don't have a '|' in the name
            if "|" in file:
                if first:
                    print("*"*79)
                    print(f'Directories in "{dirpath}"')
                    print("*"*79)
                    first = False
                new = dirpath / file.replace("|", "-")
                if not dry_run:
                    dirnames[i] = new.name
                    (dirpath / file).rename(new)
                print(f'Renaming "{file}" -> "{new.name}"')

        # Files
        first = True
        for i, file in enumerate(filenames):
            # Avoid processing for files that don't have a '|' in the name
            if "|" in file:
                if first:
                    print("*"*79)
                    print(f'Files in "{dirpath}"')
                    print("*"*79)
                    first = False
                new = dirpath / file.replace("|", "-")
                if not dry_run:
                    (dirpath / file).rename(new)
                print(f'Renaming "{file}" -> "{new.name}"')
        

def is_dir(filename: Path):
    if not filename.is_dir():
        tqdm.write(f"\"{filename}\" is not a directory.", file=sys.stderr)
        return False
    return True

def is_file(filename: Path):
    if not filename.is_file():
        tqdm.write(f"\"{filename}\" is not a file.", file=sys.stderr)
        return False
    return True

def generate_metadata_csv(csv_file: str | os.PathLike = Path("metadata.csv"), dataset_dir: str | os.PathLike = Path("data")):
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("audio_file|text\n")

        dataset_dir = Path(dataset_dir).resolve()
        if is_dir(dataset_dir):
            transcripts_dir = dataset_dir / "whisper_transcripts"
            audio_segments_dir = dataset_dir / "audio_segments"
            if is_dir(transcripts_dir) and is_dir(audio_segments_dir):
                transcript_files = [x for x in transcripts_dir.iterdir() if x.suffix == ".json"]
                print("Linking transcript files with .wav segments")
                for transcript_file in tqdm(transcript_files):

                    if is_file(transcript_file):
                        with open(transcript_file, "r", encoding="utf-8") as t:
                            transcript = json.load(t)
                            segments = transcript["segments"]

                            # Try to match .wav segments
                            video_name = transcript_file.stem
                            wav_segments_dir = audio_segments_dir / video_name
                            if is_dir(wav_segments_dir):
                                for wav_segment in wav_segments_dir.iterdir():
                                    segment_num = int(wav_segment.stem)
                                    info = segments[segment_num]
                                    transcription = info["text"].strip()

                                    f.write(f"{wav_segment}|{transcription}\n")


if __name__ == "__main__":
    data_dir = Path("data")
    replace_bar_with_dash(data_dir, dry_run=False)
    generate_metadata_csv(data_dir / "metadata.csv")


    # wget https://huggingface.co/SWivid/F5-TTS/blob/main/F5TTS_Base/model_1200000.pt
    # mv model_1200000.pt F5-TTS/ckpts/F5TTS_Base/
    # python3 F5-TTS/src/f5_tts/train/datasets/prepare_csv_wavs.py data F5-TTS/data/ramsay_data_pinyin # NOTE: need to modify prepare_csv_wavs.py file to ignore wavs not being in wavs folder
    # accelerate config
    # accelerate launch F5-TTS/src/f5_tts/train/finetune_cli.py --exp_name F5TTS_Base --dataset_name ramsay_data --finetune --learning_rate 1e-5 --batch_size_per_gpu 1618 --batch_size_type frame --max_samples 64 --grad_accumulation_steps 1 --max_grad_norm 1 --epochs 10 --num_warmup_updates 500 --save_per_updates 10000 --last_per_updates 20000
