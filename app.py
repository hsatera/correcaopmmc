import streamlit as st
import cv2
import numpy as np
import pandas as pd
import easyocr
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
import os

# Configurações iniciais
QUESTÕES = 40
COLUNAS = 4
opções_válidas = {'A', 'B', 'C', 'D'}

# Dados do gabarito e domínios
gabarito_data = {
    1: 'B', 2: 'C', 3: 'D', 4: 'C', 5: 'B', 6: 'D', 7: 'B', 8: 'D', 9: 'B', 10: 'C',
    11: 'A', 12: 'D', 13: 'C', 14: 'A', 15: 'A', 16: 'C', 17: 'A', 18: 'A', 19: 'C', 20: 'C',
    21: 'A', 22: 'B', 23: 'A', 24: 'C', 25: 'D', 26: 'C', 27: 'C', 28: 'B', 29: 'C', 30: 'D',
    31: 'C', 32: 'C', 33: 'A', 34: 'C', 35: 'D', 36: 'A', 37: 'B', 38: 'B', 39: 'C', 40: 'C'
}

dominio_data = {
    "Pesquisa Médica, Gestão em Saúde, Comunicação e Docência": {
        "Fácil": [1, 2, 15, 18, 23],
        "Intermediária": [16]
    },
    # ... (manter o restante da estrutura do dominio_data)
}

# Inicializar EasyOCR
reader = easyocr.Reader(['pt'])

# Funções auxiliares
def processar_imagem(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    return clahe.apply(gray)

def gerar_pdf(residente, respostas):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    
    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"Relatório de Desempenho - {residente}")
    
    # Detalhes das respostas
    y_position = 750
    c.setFont("Helvetica", 12)
    for q, r in respostas.items():
        c.drawString(100, y_position, f"Questão {q}: {r['resposta']} ({'Correta' if r['correta'] else 'Incorreta'})")
        y_position -= 20
    
    # Adicionar análise por domínio aqui
    
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# Interface Streamlit
st.title("📝 Sistema de Correção Automática - Programa Mais Médicos Campineiro")

# Etapa 1: Seleção do residente
residente = st.selectbox("Selecione o residente:", ["João Silva", "Maria Souza", "Pedro Oliveira"])

# Etapa 2: Upload da imagem
uploaded_file = st.file_uploader("Carregue a foto do gabarito", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # Processamento da imagem
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    processed = processar_imagem(img_array)
    
    # OCR
    results = reader.readtext(processed, allowlist='ABCDabcd')
    respostas = [r[1].upper() for r in results if r[1].upper() in opções_válidas]
    
    if len(respostas) != QUESTÕES:
        st.error(f"Quantidade de respostas inválida! Detectadas: {len(respostas)}")
    else:
        # Criar dicionário de resultados
        resultados = {
            q: {
                'resposta': respostas[q-1],
                'correta': respostas[q-1] == gabarito_data[q]
            } for q in range(1, QUESTÕES+1)
        }
        
        # Exibir revisão
        st.subheader("Confira as respostas detectadas:")
        cols = st.columns(COLUNAS)
        for i in range(QUESTÕES):
            with cols[i % COLUNAS]:
                q_num = i + 1
                cor = "✅" if resultados[q_num]['correta'] else "❌"
                st.text_input(f"{q_num}", 
                            value=f"{resultados[q_num]['resposta']} {cor}",
                            disabled=True)

        # Botão de confirmação
        if st.button("Confirmar e Salvar Resultados"):
            # Salvar no Excel
            df = pd.DataFrame.from_dict(resultados, orient='index')
            df['Residente'] = residente
            
            if os.path.exists('resultados.xlsx'):
                with pd.ExcelWriter('resultados.xlsx', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name='Resultados')
            else:
                df.to_excel('resultados.xlsx', sheet_name='Resultados')
            
            # Gerar PDF
            pdf = gerar_pdf(residente, resultados)
            
            st.success("Resultados salvos com sucesso!")
            st.download_button("Baixar Relatório PDF", 
                             data=pdf,
                             file_name=f"relatorio_{residente}.pdf",
                             mime="application/pdf")
