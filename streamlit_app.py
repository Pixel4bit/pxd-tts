import os
import streamlit as st
from kokoro import KModel, KPipeline
import torch
import soundfile as sf
import tempfile

# os.system('pip install --upgrade pip;')
# os.system('pip install -q kokoro>=0.9.2 soundfile;')
# os.system('apt-get -qq -y install espeak-ng > /dev/null 2>&1')

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
    '🇺🇸 🚺 Yola ❤️': 'af_heart',
    '🇺🇸 🚺 Yanti 🔥': 'af_bella',
    '🇺🇸 🚹 Yanto': 'am_michael',
    '🇬🇧 🚺 Juni': 'bf_emma',
    '🇬🇧 🚹 Jono': 'bm_george',
}

for v in CHOICES.values():
    pipelines[v[0]].load_voice(v)

def generate_audio(text, voice, speed=1.0, use_gpu=False):
    text = text.strip()[:CHAR_LIMIT]
    pipeline = pipelines[voice[0]]
    pack = pipeline.load_voice(voice)
    use_gpu = use_gpu and CUDA_AVAILABLE
    
    # --- START OF MODIFIED CODE ---
    all_audio_tensors = []  # List to store audio chunks (as torch tensors)
    all_tokens = []       # List to store all tokens (phonemes)
    sample_rate = 24000     # Kokoro produces audio at 24kHz

    # Iterate through the pipeline generator to get all chunks
    for _, ps, _ in pipeline(text, voice, speed):
        ref_s = pack[len(ps)-1]
        model = models[True] if use_gpu else models[False]
        audio_tensor = model(ps, ref_s, speed) # Audio as torch.Tensor
        all_audio_tensors.append(audio_tensor)
        all_tokens.extend(ps) # Add phonemes to the total list

    # If no audio was generated
    if not all_audio_tensors:
        return None, None, []

    # Concatenate all audio chunks into one large tensor
    final_audio_tensor = torch.cat(all_audio_tensors, dim=0)
    final_audio_numpy = final_audio_tensor.numpy() # Convert to numpy array for soundfile

    return sample_rate, final_audio_numpy, all_tokens
    # --- END OF MODIFIED CODE ---

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
if 'audio_file_path' not in st.session_state:
    st.session_state.audio_file_path = None
if 'audio_tokens' not in st.session_state:
    st.session_state.audio_tokens = []

st.title("🎤 A.I powered Text-to-Speech")

st.session_state.input_text = st.text_area(
    "Input Text",
    value=st.session_state.input_text,
    height=200,
    key="main_text_input"
)

st.info('Untuk saat ini bahasa yang tersedia hanya American dan British English')

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📙 Kokoro A.I", use_container_width=True):
        st.session_state.input_text = get_kokoro_text()
        st.session_state.audio_file_path = None
        st.session_state.audio_tokens = []
with col2:
    if st.button("📕 Natural Language Processing (NLP)", use_container_width=True):
        st.session_state.input_text = get_nlp_text()
        st.session_state.audio_file_path = None
        st.session_state.audio_tokens = []
with col3:
    if st.button("📗 Text-to-Speech", use_container_width=True):
        st.session_state.input_text = get_tts_text()
        st.session_state.audio_file_path = None
        st.session_state.audio_tokens = []

voice_key = st.selectbox("Pilih Voice", options=list(CHOICES.keys()), index=0)
voice = CHOICES[voice_key]
speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
use_gpu = st.checkbox("Gunakan GPU (jika tersedia)", value=CUDA_AVAILABLE and True)

if st.button("🔊 Hasilkan Suara", use_container_width=True):
    st.session_state.audio_file_path = None
    st.session_state.audio_tokens = []
    with st.spinner("Menghasilkan suara..."):
        sr, audio, tokens = generate_audio(st.session_state.input_text, voice, speed, use_gpu)
        if audio is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                sf.write(f.name, audio, sr)
                st.session_state.audio_file_path = f.name
                st.session_state.audio_tokens = tokens
        else:
            st.error("Gagal menghasilkan audio.")

if st.session_state.audio_file_path:
    st.audio(st.session_state.audio_file_path, format="audio/wav")
    st.download_button(
        "💾 Download",
        open(st.session_state.audio_file_path, 'rb'),
        file_name="output.wav",
        mime="audio/wav",
        key="download_audio_button"
    )
    st.markdown("**Token (phonemes):**")
    st.code(' '.join(st.session_state.audio_tokens))