# 🎤 AI-Powered Text-to-Speech

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pxd-tts.streamlit.app/)

A simple yet powerful web application for converting text into natural-sounding speech using the Kokoro A.I model. This project leverages Streamlit for an interactive user interface, allowing users to input text, choose from various voices (American English and British English currently available), and generate downloadable audio.

## ✨ Features

* **Intuitive User Interface:** Built with Streamlit for a clean and easy-to-use experience.
* **Multiple Voice Options:** Choose between several male and female voices for American English and British English.
* **Adjustable Speech Speed:** Control the pace of the generated speech with a slider.
* **GPU Acceleration:** Option to utilize GPU for faster audio generation if available.
* **Downloadable Audio:** Download the generated speech as a WAV file.
* **Phoneme Display:** View the phonetic transcription (tokens) of the generated speech.
* **Pre-loaded Text Examples:** Quick buttons to load sample texts about Kokoro A.I, Natural Language Processing (NLP), and Text-to-Speech.

## 🚀 How to Run Locally

To run this application on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Pixel4bit/pxd-tts.git
    cd YOUR_REPO_NAME
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file in the root of your project with the following content:
    ```
    streamlit
    kokoro>=0.9.2
    soundfile
    torch
    [https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz#egg=en_core_web_sm](https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz#egg=en_core_web_sm)
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install system-level dependencies:**
    For the `espeak-ng` library used by Kokoro, you need to install it on your system.
    * **On Debian/Ubuntu:**
        ```bash
        sudo apt-get update
        sudo apt-get install espeak-ng
        ```
    * **On macOS (using Homebrew):**
        ```bash
        brew install espeak-ng
        ```
    * **On Windows:** You might need to find a pre-compiled binary or build it from source.

5.  **Prepare example text files:**
    Create `kokoro.md`, `nlp.md`, and `tts.md` files in the same directory as `pxd-kokoro.py`. You can fill them with any text you like. For example:

    **`kokoro.md`**
    ```markdown
    Kokoro AI is an advanced text-to-speech system designed to convert written text into natural-sounding human speech. It leverages deep learning models to synthesize high-quality audio, making it suitable for various applications, including accessibility, content creation, and interactive voice assistants.
    ```

    **`nlp.md`**
    ```markdown
    Natural Language Processing (NLP) is a subfield of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language. NLP techniques are crucial for tasks such as sentiment analysis, machine translation, speech recognition, and text summarization.
    ```

    **`tts.md`**
    ```markdown
    Text-to-Speech (TTS) technology is the process of converting written language into spoken words. A TTS system is composed of several components, including text analysis, phonetic transcription, and waveform generation, to create an audible output that mimics human speech.
    ```

6.  **Run the Streamlit application:**
    ```bash
    streamlit run pxd-kokoro.py
    ```
    The application will open in your web browser.

## ☁️ Deployment on Streamlit Community Cloud

This application can be easily deployed on [Streamlit Community Cloud](https://streamlit.io/cloud). Ensure you have the following files in your repository:

* `app.py` (your main application file)
* `requirements.txt` (as detailed in "How to Run Locally" step 3)
* `packages.txt` with the content:
    ```
    espeak-ng
    ```
* `kokoro.md`, `nlp.md`, `tts.md` (your example text files)

Streamlit Community Cloud will automatically detect these files and install the necessary dependencies, including the `espeak-ng` system package and the spaCy model.

## 🤝 Contributing

Feel free to fork this repository, open issues, or submit pull requests. Any contributions to improve the project are welcome!

## 📄 License

This project is open-source and available under the [Apache License 2.0](LICENSE).
---