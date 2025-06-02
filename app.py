import streamlit as st
import pandas as pd
import numpy as np
import cv2
import easyocr
from PIL import Image
import os

# Constantes
QUESTOES = 40
OPCOES_VALIDAS = {'A', 'B', 'C', 'D'}
CSV_CAMINHO = "correcao.csv"

# Gabarito oficial
GABARITO = {
    1: 'B', 2: 'C', 3: 'D', 4: 'C', 5: 'B', 6: 'D', 7: 'B', 8: 'D', 9: 'B', 10: 'C',
    11: 'A', 12: 'D', 13: 'C', 14: 'A', 15: 'A', 16: 'C', 17: 'A', 18: 'A', 19: 'C', 20: 'C',
    21: 'A', 22: 'B', 23: 'A', 24: 'C', 25: 'D', 26: 'C', 27: 'C', 28: 'B', 29: 'C', 30: 'D',
    31: 'C', 32: 'C', 33: 'A', 34: 'C', 35: 'D', 36: 'A', 37: 'B', 38: 'B', 39: 'C', 40: 'C'
}

# Inicializar OCR
reader = easyocr.Reader(['pt'])

# Carregar lista de residentes
lista_df = pd.read_csv("lista.csv")
nomes_residentes = lista_df["NOME"].sort_values().tolist()

# Interface Streamlit
st.title("📝 Correção de Gabarito - PMMC 2025")

residente = st.selectbox("Selecione o residente:", nomes_residentes)
uploaded_file = st.file_uploader("Envie a imagem do gabarito", type=["jpg", "jpeg", "png"])

if uploaded_file:
    imagem = Image.open(uploaded_file)
    img_np = np.array(imagem)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    processed = clahe.apply(gray)

    st.image(imagem, caption="Imagem carregada", use_column_width=True)

    # OCR
    resultados_ocr = reader.readtext(processed, allowlist='ABCDabcd')
    respostas = [r[1].upper() for r in resultados_ocr if r[1].upper() in OPCOES_VALIDAS]

    if len(respostas) != QUESTOES:
        st.error(f"Foram detectadas {len(respostas)} respostas. São esperadas {QUESTOES}.")
        st.write("Respostas detectadas:", respostas)
    else:
        st.subheader("Respostas extraídas:")
        colunas = st.columns(4)
        for i in range(QUESTOES):
            q_num = i + 1
            cor = "✅" if respostas[i] == GABARITO[q_num] else "❌"
            colunas[i % 4].text_input(f"{q_num}", value=f"{respostas[i]} {cor}", disabled=True)

        if st.button("Confirmar e Salvar"):
            nova_linha = {"Residente": residente}
            for i in range(QUESTOES):
                nova_linha[f"Q{i+1:02}"] = respostas[i]

            if os.path.exists(CSV_CAMINHO):
                df_existente = pd.read_csv(CSV_CAMINHO)
                df_novo = pd.concat([df_existente, pd.DataFrame([nova_linha])], ignore_index=True)
            else:
                df_novo = pd.DataFrame([nova_linha])

            df_novo.to_csv(CSV_CAMINHO, index=False)
            st.success("Respostas salvas com sucesso!")
