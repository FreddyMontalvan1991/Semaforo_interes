import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import cv2
import numpy as np
import os
import sys
import av

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from attention_processor import AttentionProcessor


class AttentionVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.processor = AttentionProcessor()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        processed_img, status, score = self.processor.process_frame(img)
        new_frame = av.VideoFrame.from_ndarray(processed_img, format="bgr24")
        return new_frame


st.set_page_config(page_title="Reconocimiento de Atención Estudiantil", layout="wide")

st.title("Sistema de Reconocimiento del Nivel de Atención de Estudiantes")
st.markdown("""
Analiza la pose de la cabeza, parpadeo y apertura de la boca para estimar el nivel de atención.
""")

webrtc_ctx = webrtc_streamer(
    key="attention-recognition",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=AttentionVideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

if webrtc_ctx.state.playing:
    st.success("Cámara activa. Analizando el nivel de atención...")
else:
    st.warning("Esperando conexión de la cámara. Presione 'START'.")

st.sidebar.header("Métricas de Atención")
st.sidebar.markdown("""
**Alto (Verde):** Atento  
**Medio (Amarillo):** Leve distracción  
**Bajo (Rojo):** Somnolencia o mirada fuera  
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado con Streamlit, MediaPipe y OpenCV.")
