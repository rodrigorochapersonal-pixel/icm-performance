import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.graph_objects as go

# --- CONFIGURAÇÕES DE ACESSO (GOOGLE SHEETS) ---
# No Streamlit Cloud, você colará o conteúdo do seu JSON de credenciais nos 'Secrets'
def conectar_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Busca as credenciais de forma segura nos Secrets do Streamlit
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # Abre a planilha pelo nome (Certifique-se de que compartilhou a planilha com o e-mail da Service Account)
    return client.open("ICM_Database").sheet1

# --- INTERFACE E ESTILO ---
st.set_page_config(page_title="ICM Performance", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Instituto Corpo em Movimento")
st.subheader("Sistema Integrado de Avaliação Física")

# --- SIDEBAR: GESTÃO ---
with st.sidebar:
    st.header("📋 Identificação")
    professor = st.selectbox("Professor", ["Rodrigo Rocha", "Ricardo", "Outro"])
    aluno = st.text_input("Nome do Aluno")
    data_aval = st.date_input("Data da Avaliação", datetime.now())
    peso = st.number_input("Peso (kg)", value=80.0)
    idade = st.number_input("Idade", value=25)
    st.divider()
    st.image("https://via.placeholder.com/150?text=ICM+LOGO", width=150) # Substitua pelo seu logo real

# --- ABAS ---
tab_anamnese, tab_cardio, tab_funcional = st.tabs(["📋 Anamnese", "🏃 Performance", "💪 Biomecânica"])

# --- ABA 1: ANAMNESE ---
with tab_anamnese:
    col1, col2 = st.columns(2)
    with col1:
        objetivo = st.selectbox("Objetivo", ["LPO", "Hipertrofia", "Emagrecimento", "Saúde"])
        lesoes = st.text_area("Lesões/Dores")
    with col2:
        medicamentos = st.text_input("Medicamentos")
        nivel_atv = st.select_slider("Nível de Atividade", ["Sedentário", "Leve", "Moderado", "Ativo", "Atleta"])

# --- ABA 2: PERFORMANCE ---
with tab_cardio:
    c1, c2 = st.columns(2)
    with c1:
        st.write("### Bruce Protocol (VO2)")
        t_min = st.number_input("Min", 0, 30, key="m")
        t_seg = st.number_input("Seg", 0, 59, key="s")
        t_total = t_min + (t_seg/60)
        vo2 = 14.8 - (1.379 * t_total) + (0.451 * (t_total**2)) - (0.012 * (t_total**3)) if t_total > 0 else 0
        st.metric("VO2 Max", f"{vo2:.2f} ml/kg/min")
    
    with c2:
        st.write("### My Jump (Potência)")
        salto = st.number_input("Altura (cm)", 0.0, 100.0)
        watts = (60.7 * salto) + (45.3 * peso) - 2055 if salto > 0 else 0
        st.metric("Potência", f"{watts:.0f} W")

# --- ABA 3: FUNCIONAL ---
with tab_funcional:
    checklists = {
        "OHS": ["Tronco inclinado", "Calcanhar subiu", "Braços à frente", "Valgo dinâmico"],
        "Good Morning": ["Flexão lombar", "Joelho dominante", "Perda cervical", "Amplitude reduzida"],
        "Lunge": ["Valgo dinâmico", "Oscilação tronco", "Equilíbrio", "Não tocou joelho"],
        "Flexão": ["Lombar caiu", "Escápula alada", "Perda cervical", "Quadril subiu primeiro"],
        "Equilíbrio": ["Trendelenburg", "Oscilação tornozelo", "Uso braços", "Tempo < 30s"]
    }
    
    scores = {}
    for ex, falhas in checklists.items():
        with st.expander(f"{ex} (Nota 0-3)"):
            marcadas = 0
            for f in falhas:
                if st.checkbox(f, key=f"{ex}_{f}"): marcadas += 1
            sugestao = max(0, 3 - marcadas)
            scores[ex] = st.slider(f"Nota Final {ex}", 0, 3, value=sugestao, key=f"sl_{ex}")
    
    total_funcional = sum(scores.values())
    st.metric("Score Funcional Total", f"{total_funcional} / 15")

# --- SALVAMENTO ---
if st.button("💾 FINALIZAR E SALVAR"):
    if not aluno:
        st.error("Insira o nome do aluno!")
    else:
        try:
            # Tenta conectar e salvar
            sheet = conectar_google_sheets()
            dados = [
                data_aval.strftime("%d/%m/%Y"), professor, aluno, objetivo, 
                round(vo2, 2), round(watts, 2), total_funcional, str(scores)
            ]
            sheet.append_row(dados)
            st.success(f"Avaliação de {aluno} salva com sucesso!")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao conectar com Google Sheets: {e}")
            st.info("Dica: Verifique se as credenciais nos Secrets estão corretas.")
