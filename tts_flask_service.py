from f5_tts.model import DiT
from f5_tts.infer.utils_infer import (
    load_vocoder,
    load_model,
    preprocess_ref_audio_text,
    infer_process,
)

# Load vocoder
vocoder = load_vocoder()

# Load TTS model with fixed configuration
model_cfg = dict(
    dim=1024,
    depth=22,
    heads=16,
    ff_mult=2,
    text_dim=512,
    text_mask_padding=False,
    conv_layers=4,
    pe_attn_head=1,
    checkpoint_activations=False
)
ckpt_path = "finetuned_10000_f5_v1/last.safetensors"
vocab_file = 'finetuned_10000_f5_v1/vocab.txt'
tts_model = load_model(
    DiT,
    model_cfg,
    ckpt_path,
    vocab_file=vocab_file
)

# Preprocess reference audio and text
ref_audio_path = "data/ref/1.wav"
ref_text = "Now, aromatic kaffir lime leaves. Then ground cumin, coriander and turmeric."
ref_audio, ref_text = preprocess_ref_audio_text(ref_audio_path, ref_text)


def synthesize_speech(gen_text, remove_silence=False, cross_fade_duration=0.15, nfe_step=32, speed=1.0):
    final_wave, final_sample_rate, _ = infer_process(
        ref_audio,
        ref_text,
        gen_text,
        tts_model,
        vocoder,
        cross_fade_duration=cross_fade_duration,
        nfe_step=nfe_step,
        speed=speed,
        show_info=print,
        progress=None
    )
    return final_sample_rate, final_wave
