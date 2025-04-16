import os
import gc
import json
import shutil
from pytubefix import Playlist
from tqdm import tqdm
import ffmpeg
from df.enhance import enhance, init_df, load_audio, save_audio
import whisper
from pydub import AudioSegment
import pandas as pd
import torch


class PlaylistAudioDownloader:
    playlist_link = 'https://www.youtube.com/playlist?list=PLTzMGnJjrsSyTppvwM66fJbQQFeaEgyxE'
    playlist = Playlist(playlist_link)
    download_path = './data/pytube_audio'

    def __init__(self):
        print(f"Downloading audio files for {self.playlist.length} videos")
        os.makedirs(self.download_path, exist_ok=True)
        for video in tqdm(self.playlist.videos):
            save_path = os.path.join(
                self.download_path,
                f'{video.title}.m4a',
            )
            if not os.path.exists(save_path):
                audio_stream = video.streams.filter(only_audio=True).first()
                if (audio_stream):
                    audio_stream.download(
                        output_path=self.download_path
                    )
                else:
                    print(f'No audio stream found for {video.title}')


class WavConverter:
    downloader = PlaylistAudioDownloader()
    output_path = './data/wav_raw'

    def __init__(self):
        print("Using ffmpeg to convert m4a to wav")
        os.makedirs(self.output_path, exist_ok=True)
        download_path = self.downloader.download_path
        for filename in tqdm(os.listdir(download_path)):
            title = filename[:filename.find('.')]
            in_path = os.path.join(
                download_path,
                filename
            )
            out_path = os.path.join(
                self.output_path,
                f'{title}.wav'
            )
            if not os.path.exists(out_path):
                ffmpeg.input(
                    in_path
                ).output(
                    out_path
                ).run()


class AudioCleaner:
    converter = WavConverter()
    output_path = './data/wav_clean'
    temp_path = './data/temp'
    segment_length = 5 * 60 * 1000

    def split_audio(self, audio: AudioSegment):
        segments = []
        for start in range(0, len(audio), self.segment_length):
            end = min(
                start + self.segment_length,
                len(audio)
            )
            segments.append(audio[start:end])
        return segments

    def process_segment(self, segment: AudioSegment, i: int) -> AudioSegment:
        out_path = os.path.join(self.temp_path, f'{i}.wav')
        segment.export(out_path, format='wav')
        audio, _ = load_audio(out_path, sr=self.df_state.sr())
        enhanced = enhance(self.model, self.df_state, audio)
        enhanced_path = os.path.join(self.temp_path, f'{i}-e.wav')
        save_audio(enhanced_path, enhanced, self.df_state.sr())
        enhanced_segment = AudioSegment.from_file(enhanced_path)
        return enhanced_segment

    def process_file(self, in_path, out_path):
        audio = AudioSegment.from_file(in_path)
        segments = self.split_audio(audio)
        os.makedirs(self.temp_path, exist_ok=True)
        enhanced_segments = [
            self.process_segment(segment, i) for i, segment in enumerate(segments)
        ]
        enhanced_audio: AudioSegment = sum(enhanced_segments)
        enhanced_audio.export(out_path, format='wav')

    def process_files(self):
        input_path = self.converter.output_path
        for filename in tqdm(os.listdir(input_path)):
            in_path = os.path.join(input_path, filename)
            out_path = os.path.join(self.output_path, filename)
            if not os.path.exists(out_path):
                self.process_file(in_path, out_path)

    def clean(self):
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
        del self.model
        del self.df_state
        gc.collect()
        torch.cuda.empty_cache()

    def __init__(self):
        print("Using deepfilternet to clean audio")
        self.model, self.df_state, _ = init_df(
            model_base_dir='DeepFilterNet3'
        )
        os.makedirs(self.output_path, exist_ok=True)
        self.process_files()
        self.clean()


class AudioTranscriber:
    cleaner = AudioCleaner()
    output_dir = './data/whisper_transcripts'

    def __init__(self):
        print("Using whisper to transcibe cleaned audio")
        model = whisper.load_model(
            'turbo',
            device='cuda'
        )
        os.makedirs(self.output_dir, exist_ok=True)
        input_path = self.cleaner.output_path
        for filename in tqdm(os.listdir(input_path)):
            title = filename[:filename.find('.')]
            in_path = os.path.join(
                input_path,
                filename
            )
            out_path = os.path.join(
                self.output_dir,
                f'{title}.json'
            )
            if not os.path.exists(out_path):
                result = model.transcribe(
                    audio=in_path,
                    word_timestamps=True
                )
                with open(out_path, 'w') as f:
                    json.dump(result, f)


class AudioSegmenter:
    output_loc = './data/audio_segments'
    transcriber = AudioTranscriber()
    meta_path = os.path.join(output_loc, 'meta.pkl')
    metadata = []

    def __init__(self):
        print("Splitting audio files using whisper segments")
        os.makedirs(self.output_loc, exist_ok=True)
        transcript_dir = self.transcriber.output_dir
        audio_dir = self.transcriber.cleaner.output_path
        for filename in tqdm(os.listdir(audio_dir)):
            title = filename[:filename.find('.')]
            out_dir = os.path.join(
                self.output_loc,
                title
            )
            os.makedirs(out_dir, exist_ok=True)
            audio_path = os.path.join(
                audio_dir,
                filename
            )
            transcript_path = os.path.join(
                transcript_dir,
                f'{title}.json'
            )
            audio = AudioSegment.from_file(audio_path)
            with open(transcript_path, 'r') as f:
                transcript = json.load(f)
            for i, segment in enumerate(transcript['segments']):
                out_path = os.path.join(
                    out_dir,
                    f'{i}.wav'
                )
                if os.path.exists(out_path):
                    continue
                start = int(segment['start'] * 1000)
                end = int(segment['end'] * 1000)
                if start >= end - 2000 or start + 10000 < end:
                    continue
                audio_segment = audio[start:end]
                audio_segment.export(out_path, format='wav')
                segment['index'] = i
                segment['title'] = title
                self.metadata.append(segment)
        if os.path.exists(self.meta_path):
            self.df = pd.read_pickle(self.meta_path)
            temp = pd.DataFrame(self.metadata)
            self.df = pd.concat([
                self.df,
                temp
            ])
        else:
            self.df = pd.DataFrame(self.metadata)
            self.df.to_pickle(self.meta_path)


if __name__ == '__main__':
    audio_segmenter = AudioSegmenter()
    print(f'Dataset has {audio_segmenter.df.shape[0]} sentences')
