from infer import gordon_config, Inferencer, normal_config
import os
from tqdm import tqdm

prompt_dir = './data/ollama/inputs/'
out_dir = './data/ollama/normal_outputs/'

if __name__ == '__main__':
    os.makedirs(out_dir, exist_ok=True)
    inferencer = Inferencer(
        config_path='/tmp/config.toml',
        config=normal_config
    )
    for filename in tqdm(os.listdir(prompt_dir)):
        name = filename[:filename.find('.')]
        in_path = os.path.join(prompt_dir, filename)
        out_file = f'{name}.wav'
        with open(in_path, 'r') as f:
            prompt = f.read()
        inferencer.inference(
            gen_text=prompt,
            output_dir=out_dir,
            output_file=out_file
        )
