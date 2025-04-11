import os
import pandas as pd
from datasets import Dataset, Audio

data_path = './data/audio_segments/'
meta_name = 'meta.pkl'

dataset_name = 'the-ramsay-expirience/ramsay_audio'

meta_path = os.path.join(
    data_path,
    meta_name
)
if not os.path.exists(meta_path):
    raise Exception(
        "No metadata file found under audio_segments, missing dataset"
    )

df = pd.read_pickle(meta_path)

ds = Dataset.from_pandas(df)

if __name__ == '__main__':
    audio_paths = []
    for index, row in df.iterrows():
        audio_paths.append(
            './data/audio_segments/' +
            row['title'] + '/' + str(row['id']) + '.wav'
        )
    df['audio'] = audio_paths
    ds = Dataset.from_pandas(df)
    ds = ds.cast_column('audio', Audio())
    ds.push_to_hub(dataset_name)
