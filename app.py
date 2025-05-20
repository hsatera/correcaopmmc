import streamlit as st
import cv2
import numpy as np
from PIL import Image
import easyocr

st.title("📝 Leitor de Respostas - Programa Mais Médicos Campineiro")

# Configurações
QUESTÕES = 40
COLUNAS = 4
opções_válidas = {'A', 'B', 'C', 'D'}

# Inicializar EasyOCR
reader = easyocr.Reader(['pt'])

# Função de processamento de imagem
def processar_imagem(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    return enhanced

# Interface principal
uploaded_file = st.file_uploader("Carregue a foto do gabarito", 
                               type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # Carregar imagem
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    
    # Pré-processamento
    processed = processar_imagem(img_array)
    
    # Exibir imagens
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Imagem Original")
    with col2:
        st.image(processed, caption="Imagem Processada")
    
    # OCR com EasyOCR
    results = reader.readtext(processed, allowlist='ABCDabcd')
    respostas = [r[1].upper() for r in results if r[1].upper() in opções_válidas]
    
    # Validação
    if len(respostas) != QUESTÕES:
        st.warning(f"Detectadas: {len(respostas)} | Esperado: {QUESTÕES}")
    
    # Exibir respostas
    st.subheader("Respostas Detectadas:")
    
    cols = st.columns(COLUNAS)
    for i in range(QUESTÕES):
        with cols[i % COLUNAS]:
            número = f"{i+1:02d}"
            resposta = respostas[i] if i < len(respostas) else "?"
            st.text_input(número, value=resposta, key=i)

    st.info("Verifique as respostas e faça ajustes manuais se necessário")
