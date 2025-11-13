import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process as aksharamukha_process
from gtts import gTTS
from io import BytesIO
import pandas as pd
import jieba   # Chinese word segmentation

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="Chinese (Simplified) → Kannada Learning",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------ HIDE STREAMLIT UI ------------------ #
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------ AUDIO GENERATOR ------------------ #
def make_audio(text, lang="kn"):
    fp = BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

# ------------------ PAGE TITLE ------------------ #
st.title("📝 Learn Kannada using Mandarin Chinese (Simplified)")
st.subheader("使用简体中文学习卡纳达语")

text = st.text_area("Enter Simplified Chinese text (输入中文):", height=120)

if st.button("Translate"):
    if text.strip():
        try:
            # ---------------- FULL SENTENCE PROCESSING ---------------- #

            # Chinese → Kannada translation
            kannada = GoogleTranslator(source="zh-CN", target="kn").translate(text)

            # Kannada → Latin script (best for Chinese learners)
            kannada_in_latin = aksharamukha_process("Kannada", "ISO", kannada)

            # Kannada → English phonetics
            kannada_english = transliterate(kannada, sanscript.KANNADA, sanscript.ITRANS)

            # Sentence audio
            audio_sentence = make_audio(kannada)

            # ---------------- OUTPUT ---------------- #
            st.markdown("## 🔹 Translation Results")

            st.markdown(f"**Chinese Input:**  \n:blue[{text}]")
            st.markdown(f"**Kannada Translation:**  \n:green[{kannada}]")
            st.markdown(f"**Kannada in Latin Script:**  \n:orange[{kannada_in_latin}]")
            st.markdown(f"**English Phonetics:**  \n`{kannada_english}`")

            st.markdown("### 🔊 Kannada Audio (Sentence)")
            st.audio(audio_sentence, format="audio/mp3")
            st.download_button("Download Sentence Audio", audio_sentence, "sentence.mp3")

            # ---------------- WORD-BY-WORD FLASHCARDS ---------------- #

            st.markdown("---")
            st.markdown("## 🃏 Flashcards (Word-by-Word)")

            # Chinese segmentation (jieba)
            chinese_words = list(jieba.cut(text))
            kan_words = kannada.split()

            # Match up to smaller length
            limit = min(len(chinese_words), len(kan_words))

            for i in range(limit):
                cw = chinese_words[i]
                kw = kan_words[i]

                # Kannada → Latin script (word)
                kw_latin = aksharamukha_process("Kannada", "ISO", kw)

                # English phonetics
                kw_ph = transliterate(kw, sanscript.KANNADA, sanscript.ITRANS)

                # Word audio
                kw_audio = make_audio(kw)

                with st.expander(f"Word {i+1}: {cw}", expanded=False):
                    st.write("**Chinese word:**", cw)
                    st.write("**Kannada word:**", kw)
                    st.write("**Kannada in Latin script:**", kw_latin)
                    st.write("**Phonetics:**", kw_ph)

                    st.audio(kw_audio, format="audio/mp3")
                    st.download_button(
                        f"Download Audio (Word {i+1})",
                        kw_audio,
                        f"word_{i+1}.mp3"
                    )

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.warning("Please enter Chinese text.")
