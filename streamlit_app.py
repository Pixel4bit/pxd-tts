import os

os.system('pip install --upgrade pip; ')
os.system('pip install -q kokoro>=0.9.2 soundfile;')
os.system('apt-get -qq -y install espeak-ng > /dev/null 2>&1')

import streamlit as st
from kokoro import KModel, KPipeline
import torch
import soundfile as sf
import tempfile

CHAR_LIMIT = 5000
CUDA_AVAILABLE = torch.cuda.is_available()

@st.cache_resource
def load_models():
    return {
        False: KModel().to('cpu').eval(),
        True: KModel().to('cuda').eval() if CUDA_AVAILABLE else None
    }

models = load_models()

@st.cache_resource
def load_pipelines():
    pipelines = {lang_code: KPipeline(lang_code=lang_code, model=False) for lang_code in 'ab'}
    pipelines['a'].g2p.lexicon.golds['kokoro'] = 'kˈOkəɹO'
    pipelines['b'].g2p.lexicon.golds['kokoro'] = 'kˈQkəɹQ'
    return pipelines

pipelines = load_pipelines()

CHOICES = {
    '🇺🇸 🚺 Heart ❤️': 'af_heart',
    '🇺🇸 🚺 Bella 🔥': 'af_bella',
    '🇺🇸 🚹 Michael': 'am_michael',
    '🇬🇧 🚺 Emma': 'bf_emma',
    '🇬🇧 🚹 George': 'bm_george',
}

for v in CHOICES.values():
    pipelines[v[0]].load_voice(v)

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

@st.cache_data
def get_kokoro_text():
    with open('kokoro.md', 'r') as f:
        return "\n".join([line.strip() for line in f.readlines()])

@st.cache_data
def get_nlp_text():
    with open('nlp.md', 'r') as f:
        return f.read().strip()

@st.cache_data
def get_tts_text():
    with open('tts.md', 'r') as f:
        return f.read().strip()

if 'input_text' not in st.session_state:
    st.session_state.input_text = ""

st.title("🎤 Kokoro A.I Text-to-Speech")

st.session_state.input_text = st.text_area(
    "Input Text",
    value=st.session_state.input_text,
    height=200,
    key="main_text_input"
)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📙 Kokoro A.I", use_container_width=True):
        st.session_state.input_text = get_kokoro_text()
with col2:
    if st.button("📕 Natural Language Processing (NLP)", use_container_width=True):
        st.session_state.input_text = get_nlp_text()
with col3:
    if st.button("📗 Text-to-Speech", use_container_width=True):
        st.session_state.input_text = get_tts_text()

voice_key = st.selectbox("Pilih Voice", options=list(CHOICES.keys()), index=0)
voice = CHOICES[voice_key]
speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
use_gpu = st.checkbox("Gunakan GPU (jika tersedia)", value=CUDA_AVAILABLE and True)

if st.button("🔊 Hasilkan Suara"):
    with st.spinner("Menghasilkan suara..."):
        sr, audio, tokens = generate_audio(st.session_state.input_text, voice, speed, use_gpu)
        if audio is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                sf.write(f.name, audio, sr)
                st.audio(f.name, format="audio/wav")
                st.download_button("💾 Download", open(f.name, 'rb'), file_name="output.wav", mime="audio/wav")
            st.markdown("**Token (phonemes):**")
            st.code(' '.join(tokens))
        else:
            st.error("Gagal menghasilkan audio.")