import streamlit as st
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator
import re

# Title and Description
st.title("YouTube Video Summarizer")
st.write("Aplikasi ini menampilkan transkrip video YouTube dan merangkumnya dalam Bahasa Inggris serta Indonesia.")

# Input YouTube URL
youtube_url = st.text_input("Masukkan URL video YouTube:")

def extract_video_id(url):
    """
    Ekstrak ID video dari berbagai format URL YouTube.
    """
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

if youtube_url:
    try:
        # Extract Video ID
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("URL tidak valid. Harap masukkan URL YouTube yang benar.")
        else:
            # Display Thumbnail
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            st.image(thumbnail_url, caption="Thumbnail Video", use_column_width=True)

            # Get Transcript
            st.write("Mengambil transkrip...")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine Transcript
            full_text = " ".join([item['text'] for item in transcript])
            st.subheader("Transkrip Asli (Bahasa Inggris):")
            st.text_area("Transkrip Asli:", full_text, height=200)

            # Button to Summarize
            if st.button("Rangkum Transkrip"):
                st.write("Merangkum transkrip...")
                summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

                # Optimized chunk size to process more text at once
                chunk_size = 2000  # Increase chunk size for fewer iterations
                num_iters = len(full_text) // chunk_size + 1

                summarized_text = []
                for i in range(num_iters):
                    start = i * chunk_size
                    end = (i + 1) * chunk_size
                    chunk = full_text[start:end]
                    if len(chunk.strip()) > 0:  # Ensure chunk is not empty
                        summary = summarizer(chunk, max_length=200, min_length=50, do_sample=False)[0]['summary_text']
                        summarized_text.append(summary)

                summarized_text = " ".join(summarized_text)
                st.subheader("Ringkasan dalam Bahasa Inggris:")
                st.text_area("Ringkasan (Bahasa Inggris):", summarized_text, height=150)

                # Translate Summary to Indonesian
                st.write("Menerjemahkan ringkasan ke Bahasa Indonesia...")
                translator = Translator()
                translated_text = translator.translate(summarized_text, dest='id').text
                st.subheader("Ringkasan dalam Bahasa Indonesia:")
                st.text_area("Ringkasan (Bahasa Indonesia):", translated_text, height=150)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
