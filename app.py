import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configurações de Estética e Layout
st.set_page_config(page_title="ICM - Performance & Biomecânica", layout="wide")

# Estilo para o título e cores do Instituto
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    h1 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Sistema de Avaliação - Instituto Corpo em Movimento")

# --- SIDEBAR: GESTÃO ---
with st.sidebar:
    st.header("📋 Registro da Avaliação")
    professor = st.selectbox("Professor Responsável", ["Selecione...", "Rodrigo Rocha", "Ricardo", "Outro"])
    nome_aluno = st.text_input("Nome do Aluno")
    data_aval = st.date_input("Data", datetime.now())
    peso_aluno = st.number_input("Peso (kg)", value=80.0)
    idade = st.number_input("Idade", value=27)
    st.divider()
    st.info("Todos os dados serão salvos no Google Sheets e os vídeos no Drive.")

# --- ABAS PRINCIPAIS ---
tab_anamnese, tab_cardio, tab_funcional = st.tabs(["📋 Anamnese", "🏃 Performance (Bruce/Jump)", "💪 Avaliação Funcional"])

# --- ABA 1: ANAMNESE ---
with tab_anamnese:
    st.subheader("Triagem e Objetivos")
    col_a, col_b = st.columns(2)
    with col_a:
        objetivo = st.selectbox("Objetivo Principal", ["Hipertrofia", "Performance LPO", "Emagrecimento", "Reabilitação", "Saúde"])
        lesoes = st.text_area("Histórico de lesões ou dores:")
    with col_b:
        medicamentos = st.text_input("Medicamentos em uso:")
        nivel_atv = st.select_slider("Nível de atividade atual", options=["Sedentário", "Leve", "Moderado", "Ativo", "Atleta"])

# --- ABA 2: PERFORMANCE (BRUCE & MY JUMP) ---
with tab_cardio:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Protocolo de Bruce (VO2 Max)")
        t_min = st.number_input("Minutos", 0, 30, 0, key="b_min")
        t_seg = st.number_input("Segundos", 0, 59, 0, key="b_seg")
        t_total = t_min + (t_seg/60)
        vo2 = 14.8 - (1.379 * t_total) + (0.451 * (t_total**2)) - (0.012 * (t_total**3)) if t_total > 0 else 0
        st.metric("VO2 Max Estimado", f"{vo2:.2f} ml/kg/min")
        
        fc_max = 220 - idade
        st.caption(f"Zonas de Treino: L1 (70%): {int(fc_max*0.7)}bpm | L2 (90%): {int(fc_max*0.9)}bpm")
    
    with c2:
        st.subheader("My Jump (Potência)")
        altura_salto = st.number_input("Salto (cm)", 0.0, 100.0, 0.0)
        potencia = (60.7 * altura_salto) + (45.3 * peso_aluno) - 2055 if altura_salto > 0 else 0
        st.metric("Potência de Pico", f"{potencia:.0f} Watts")

# --- ABA 3: AVALIAÇÃO FUNCIONAL ---
with tab_funcional:
    st.subheader("Análise Biomecânica (Score Total: /15)")
    
    checklists = {
        "1. OVERHEAD SQUAT": ["Tronco inclinado", "Calcanhar subiu", "Braços à frente", "Valgo dinâmico"],
        "2. GOOD MORNING": ["Flexão lombar", "Joelho dominante", "Perda cervical", "Amplitude reduzida"],
        "3. LUNGE IN LINE": ["Valgo dinâmico", "Oscilação de tronco", "Perda de equilíbrio", "Não tocou o joelho"],
        "4. FLEXÃO DE BRAÇO": ["Seringada (lombar caiu)", "Escápula alada", "Cabeça caiu (perda cervical)", "Quadril subiu primeiro"],
        "5. EQ. UNIPODAL": ["Queda de quadril (Trendelenburg)", "Oscilação excessiva tornozelo", "Uso dos braços p/ equilíbrio", "Tempo inferior a 30s"]
    }
    
    notas_finais = {}
    
    for ex, falhas in checklists.items():
        with st.expander(ex, expanded=True):
            col_check, col_res = st.columns([2, 1])
            with col_check:
                marcadas = 0
                for falha in falhas:
                    if st.checkbox(falha, key=f"ch_{ex}_{falha}"):
                        marcadas += 1
            with col_res:
                sugestao = max(0, 3 - marcadas)
                nota = st.slider(f"Nota {ex}", 0, 3, value=sugestao, key=f"sl_{ex}")
                notas_finais[ex] = nota
            
            # Opção de Vídeo Direto
            st.file_uploader(f"Filmar/Anexar execução de {ex}", type=['mp4', 'mov'], key=f"vid_{ex}")

    score_total = sum(notas_finais.values())
    st.divider()
    st.markdown(f"### 📊 SCORE TOTAL: {score_total} / 15")

# --- BOTÃO FINAL ---
if st.button("💾 SALVAR AVALIAÇÃO COMPLETA NO DRIVE"):
    if professor != "Selecione..." and nome_aluno:
        st.success(f"Avaliação de {nome_aluno} registrada com sucesso por {professor}!")
        st.balloons()
    else:
        st.error("⚠️ Por favor, identifique o Professor e o Aluno.")
