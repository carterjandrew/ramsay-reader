#!/usr/bin/env python3
import json
import f5_tts.infer.infer_gradio as f5_script

# override before anything else happens:
# f5_script.DEFAULT_TTS_MODEL = "Ramsay_V1"
# f5_script.DEFAULT_TTS_MODEL = 'F5_TTS'
f5_script.DEFAULT_TTS_MODEL_CFG = [
    "hf://the-ramsay-experience/finetuned_10000_f5_v1/last.safetensors",
    "/home/carter/ramsay-reader/finetuned_10000_f5_v1/vocab.txt",
    json.dumps(dict(
        dim=1024,
        depth=22,
        heads=16,
        ff_mult=2,
        text_dim=512,
        conv_layers=4,
    ))
]

# now launch the app exactly as if you ran the original script
if __name__ == "__main__":
    f5_script.F5TTS_ema_model = f5_script.load_f5tts()
    f5_script.main()
