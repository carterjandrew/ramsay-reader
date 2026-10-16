import toml
import os
import subprocess


class Inferencer:
    def __init__(self, config, config_path):
        self.config: dict = config
        self.config_path = config_path

    def write_config(self):
        with open(self.config_path, 'w') as f:
            toml.dump(self.config, f)

    def inference(self, gen_text, output_dir, output_file):
        self.config['gen_text'] = gen_text
        self.config['output_dir'] = output_dir
        self.config['output_file'] = output_file
        self.write_config()
        subprocess.run(['f5-tts_infer-cli', '-c', self.config_path])


gordon_config = dict(
    model='F5TTS_Base',
    ref_audio='/home/carter/ramsay-reader/data/ref/1.wav',
    ref_text='/home/carter/ramsay-reader/data/ref/1.txt',
    ckpt_file='/home/carter/ramsay-reader/finetuned_10000_f5_v1/last.safetensors',
    vocab_file='/home/carter/ramsay-reader/finetuned_10000_f5_v1/vocab.txt',
    gen_text='Hello world',
    remove_silence=True,
    output_dir='./data/ramsay/outputs/',
    output_file='1.wav',
)

normal_config = dict(
    model='F5TTS_Base',
    ref_audio='/home/carter/ramsay-reader/data/ref/1.wav',
    ref_text='/home/carter/ramsay-reader/data/ref/1.txt',
#     ckpt_file='/home/carter/ramsay-reader/finetuned_10000_f5_v1/last.safetensors',
#     vocab_file='/home/carter/ramsay-reader/finetuned_10000_f5_v1/vocab.txt',
    gen_text='Hello world',
    remove_silence=True,
    output_dir='./data/ramsay/outputs/',
    output_file='1.wav',
)

if __name__ == '__main__':
    inferencer = Inferencer(
        config=gordon_config,
        config_path='/tmp/config.toml'
    )
    inferencer.inference(
        gen_text='allright you swine today ill be teaching your bone headed thick skulled no brain wandering megatronic ass how to make the worlds best play dough',
        output_file='test.wav',
        output_dir='./data/'
    )
