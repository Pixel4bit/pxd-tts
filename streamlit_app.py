import streamlit as st
from kokoro import KModel, KPipeline
import torch
import soundfile as sf
import tempfile
import random
import os

# Inisialisasi
CHAR_LIMIT = 5000
CUDA_AVAILABLE = torch.cuda.is_available()

# Load model CPU dan GPU
@st.cache_resource
def load_models():
    return {
        False: KModel().to('cpu').eval(),
        True: KModel().to('cuda').eval() if CUDA_AVAILABLE else None
    }

models = load_models()

# Load pipelines
@st.cache_resource
def load_pipelines():
    pipelines = {lang_code: KPipeline(lang_code=lang_code, model=False) for lang_code in 'ab'}
    pipelines['a'].g2p.lexicon.golds['kokoro'] = 'kˈOkəɹO'
    pipelines['b'].g2p.lexicon.golds['kokoro'] = 'kˈQkəɹQ'
    return pipelines

pipelines = load_pipelines()

# Voice pilihan
CHOICES = {
    '🇺🇸 🚺 Heart ❤️': 'af_heart',
    '🇺🇸 🚺 Bella 🔥': 'af_bella',
    '🇺🇸 🚹 Michael': 'am_michael',
    '🇬🇧 🚺 Emma': 'bf_emma',
    '🇬🇧 🚹 George': 'bm_george',
}

# Pre-load voice
for v in CHOICES.values():
    pipelines[v[0]].load_voice(v)

# Fungsi TTS
def generate_audio(text, voice, speed=1.0, use_gpu=False):
    text = text.strip()[:CHAR_LIMIT]
    pipeline = pipelines[voice[0]]
    pack = pipeline.load_voice(voice)
    use_gpu = use_gpu and CUDA_AVAILABLE
    for _, ps, _ in pipeline(text, voice, speed):
        ref_s = pack[len(ps)-1]
        model = models[True] if use_gpu else models[False]
        audio = model(ps, ref_s, speed)
        return 24000, audio.numpy(), ps
    return None, None, ''

# Fungsi quotes
@st.cache_data
def get_quotes():
    with open('en.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]

@st.cache_data
def get_gatsby():
    with open('gatsby5k.md', 'r') as f:
        return f.read().strip()

@st.cache_data
def get_frankenstein():
    with open('frankenstein5k.md', 'r') as f:
        return f.read().strip()

# UI Streamlit
st.title("🎤 Kokoro A.I Text-to-Speech (Streamlit Version)")

col1, col2 = st.columns([3, 1])
with col1:
    text = st.text_area("Input Text", height=200)
with col2:
    if st.button("🎲 Random Quote"):
        text = random.choice(get_quotes())
        st.experimental_rerun()

voice_key = st.selectbox("Pilih Voice", options=list(CHOICES.keys()), index=0)
voice = CHOICES[voice_key]
speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
use_gpu = st.checkbox("Gunakan GPU (jika tersedia)", value=CUDA_AVAILABLE and True)

col3, col4 = st.columns(2)
with col3:
    if st.button("📕 Gatsby"):
        text = get_gatsby()
        st.experimental_rerun()
with col4:
    if st.button("📗 Frankenstein"):
        text = get_frankenstein()
        st.experimental_rerun()

if st.button("🔊 Hasilkan Suara"):
    with st.spinner("Menghasilkan suara..."):
        sr, audio, tokens = generate_audio(text, voice, speed, use_gpu)
        if audio is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                sf.write(f.name, audio, sr)
                st.audio(f.name, format="audio/wav")
                st.download_button("💾 Download", open(f.name, 'rb'), file_name="output.wav", mime="audio/wav")
            st.markdown("**Token (phonemes):**")
            st.code(' '.join(tokens))
        else:
            st.error("Gagal menghasilkan audio.")