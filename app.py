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
CSV_CAMINHO = "CORREÇÃO PMMC 2025 respostas.csv"

# Gabarito oficial
GABARITO = {
    1: 'B', 2: 'C', 3: 'D', 4: 'C', 5: 'B', 6: 'D', 7: 'B', 8: 'D', 9: 'B', 10: 'C',
    11: 'A', 12: 'D', 13: 'C', 14: 'A', 15: 'A', 16: 'C', 17: 'A', 18: 'A', 19: 'C', 20: 'C',
    21: 'A', 22: 'B', 23: 'A', 24: 'C', 25: 'D', 26: 'C', 27: 'C', 28: 'B', 29: 'C', 30: 'D',
    31: 'C', 32: 'C', 33: 'A', 34: 'C', 35: 'D', 36: 'A', 37: 'B', 38: 'B', 39: 'C', 40: 'C'
}

# Inicializar OCR
reader = easyocr.Reader(['pt'])

# Lista de residentes manualmente definida
dados_residentes = """NOME,ANO,PROGRAMA
Alexia Allis Rocha Lima,R2,PMC-CHOV
Alice Morellato Haddad,R1,Unicamp
Aline Brandao De Almeida Amazonas Biazoli,R1,PMC-CHOV
Ana Cecília Venâncio,R1,Unicamp
Ana Flavia Aggio Jamberci,R1,PUCCAMP
Ana Luisa Chen,R2,Unicamp
Andre Paiva Garcia Beck,R2,PMC-CHOV
Anivaldo Barbosa de Sousa Neto,R2,PUCCAMP
Armindo Albuquerque,R1,Unicamp
Bárbara Vilella Nakamuta,R1,Unicamp
Beatriz De Sousa Kato,R1,PMC-CHOV
Beatriz Gasparotti De Camargo,R1,PUCCAMP
Beatriz Tiaki,R1,PMC-CHOV
Beatriz Zangrossi Rodrigues,R2,PMC-CHOV
Carolina Almeida,R1,Unicamp
Clarrisa Ricci Goulardins,R1,Unicamp
Dandara Pereira Alves,R1,PMC-Gatti
Daniel Fonseca,R2,Unicamp
Dayane Moreira Duarte,R1,PMC-CHOV
Debora Roveron,R2,Unicamp
Elisa de Castro Barros Giudice,R2,PUCCAMP
Eliseu Ribeiro Caldas,R1,PMC-CHOV
Erick Bonatelli Cardim,R2,PMC-CHOV
Fernanda Sabarim,R2,PMC-CHOV
Flávia Fernanda Moreno,R1,PMC-Gatti
Gabriela Fernandes Conrado,R2,PMC-CHOV
Gabrielly Paola Souza Marçal,R1,PMC-CHOV
Gideone Cruz Da Silva,R1,PMC-CHOV
Giovana Miho,R2,Unicamp
Giovanna Santos Garlo,R1,PMC-CHOV
Giulia Medici,R2,Unicamp
Giulia Peters Santos,R1,PMC-CHOV
Guilherme Barros Bonelli,R1,Unicamp
Gustavo Luis de Oliveira,R2,PMC-CHOV
Helena Lopes De Barros,R1,Unicamp
Helena Machado Galhardo,R2,PMC-CHOV
Isabela Almeida,R2,Unicamp
Isabella Venturini De Abreu Ferreira,R1,PMC-CHOV
Isabelle Caroline Viterbino Loraschi,R2,PMC-CHOV
Iumi Belmont Martins Ujisato,R2,PMC-CHOV
Jhan Carla Laime,R2,PMC-CHOV
João Ítalo,R1,PMC-Gatti
Jonatas Dos Santos Ribeiro,R1,PMC-CHOV
Jose Camargo Junior,R1,Unicamp
José Henrique Beserra,R1,PMC-CHOV
Julia Breda Roque,R2,PMC-Gatti
Julia Jeniffer Menezes,R2,PMC-CHOV
Juliana Gonçalves Rosa,R2,PMC-Gatti
Juliana Monteiro Sampaio de Faria,R2,PMC-CHOV
Karina Fernades Ruiz Ferreira,R1,PMC-CHOV
Kathia Terumi Otsuki,R2,PMC-CHOV
Laura Bertollo Poiani,R1,PMC-CHOV
Laura Carvalho,R2,Unicamp
Leandro Manoel Afonso Mendes,R2,PMC-CHOV
Letícia Dantas Trindade,R1,Unicamp
Leticia Teixeira Marcondes,R2,PUCCAMP
Luis Rodolfo Ferreira Santos,R1,PMC-CHOV
Luiz Fernando Martins e Silva,R2,Unicamp
Luiz Henrique Novi,R1,PUCCAMP
Luiza D´Ottaviano Cobos,R1,PMC-CHOV
Luiza Kassar,R2,Unicamp
Marcela Oliveira Silva,R1,PMC-CHOV
Maria Victoria Vargas,R2,Unicamp
Mariana De Oliveira,R1,Unicamp
Marianna Freitas,R1,Unicamp
Marina Stavarengo Schreen Fontana,R1,PMC-CHOV
Maryna Fernanda Nora Santos,R2,PMC-CHOV
Mateus Henrique Pizzon,R2,PMC-Gatti
Matheus Hoffmann,R1,PMC-CHOV
Mathias Machado,R1,Unicamp
Monique Conceição Ananias,R2,PMC-Gatti
Murilo Castro,R1,Unicamp
Murilo Da Silva Rodrigues,R1,PMC-CHOV
Natalia Bergamo,R2,Unicamp
Nathalia Braido,R2,Unicamp
Nathalia Rodrigeus,R2,Unicamp
Nayane Salvador Silva,R1,PMC-CHOV
Olgata Marianne,R2,Unicamp
Paulo Okuda,R1,Unicamp
Perola Maria Bianchini Lande dos Santos,R2,PMC-CHOV
Rafael Augusto,R2,Unicamp
Rafael Gonçalves Rosa de Oliveira,R2,PMC-CHOV
Rafael Machado Martinucci,R1,PMC-CHOV
Raquel Rocha,R2,Unicamp
Rebeca de Barros,R2,Unicamp
Samyla De Almeida Silva,R1,PMC-Gatti
Tatiana Yamamoto,R1,PMC-CHOV
Vanessa Alves Martins,R2,PMC-CHOV
Vinícius Rosa,R1,PMC-CHOV
Vitoria Rezende Oliveira,R2,PMC-CHOV
Yzodara Dandara Duarte Ramos,R2,PMC-CHOV"""

from io import StringIO
lista_df = pd.read_csv(StringIO(dados_residentes))
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
