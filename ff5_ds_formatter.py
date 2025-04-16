from huggingface_dataset_builder import dataset_name
from datasets import load_dataset
import pandas as pd
import os
import soundfile
from tqdm import tqdm

class FF5Formatter:
    dataset_dir = './dataset'
    wavs_dir = os.path.join(dataset_dir, 'wavs')
    hf_ds_name = dataset_name
    def __init__(self):
        self.hf_ds = load_dataset(self.hf_ds_name)
        self.df = pd.DataFrame(self.hf_ds['train'])
        os.makedirs(self.wavs_dir, exist_ok=True)
        self.formatted_df = pd.DataFrame(
            columns=['audio_file', 'text']
        )
        filepaths = list()
        for i, row in tqdm(self.df.iterrows()):
            filename = f'{i}.wav'
            filepath = os.path.join(self.wavs_dir, filename)
            filepaths.append(f'wavs/{filename}')
            soundfile.write(
                filepath,
                row['audio']['array'],
                samplerate=row['audio']['sampling_rate']
            )
        self.formatted_df['text'] = self.df['text']
        self.formatted_df['audio_file'] = filepaths
        self.formatted_df.to_csv(
            os.path.join(self.dataset_dir, 'metadata.csv'),
            index=False,
            sep='|'
        )
if __name__ == '__main__':
    FF5Formatter()
