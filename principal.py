import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from database import (
    init_db, sincronizar_bases_json, validar_bi_angolano, 
    validar_telefone_angolano, DB_NAME, OPCOES_CARGOS
)
from agri_rules import REGRAS_CULTURAS, gerar_diretrizes_produto

st.set_page_config(page_title="Plataforma de Previsão Climática", layout="wide")
init_db()

st.markdown("""
<style>
    /* Estilização dos cabeçalhos das tabelas */
    .stDataFrame table thead tr th {
        background-color: #00ADB5 !important;
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    table thead tr th {
        background-color: #00ADB5 !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_atual" not in st.session_state:
    st.session_state["usuario_atual"] = None

def tela_login():
    st.title("🌾 Sistema de Gestão Agrícola - Acesso")
    aba1, aba2 = st.tabs(["Entrar", "Criar Conta (Subscrição)"])

    with aba1:
        st.subheader("Autenticação de Utilizador")
        bi_login = st.text_input("Número do BI:")
        senha_login = st.text_input("Palavra-passe:", type="password")
        
        if st.button("Entrar"):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT nome_usuario, status FROM usuarios_sistema WHERE bi = ? AND senha = ?", (bi_login.strip(), senha_login))
            user = cursor.fetchone()
            conn.close()

            if user:
                nome, status = user
                if status == "APROVADO":
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_atual"] = nome
                    st.success(f"Bem-vindo, {nome}!")
                    st.rerun()
                elif status == "EM_ANALISE":
                    st.warning("⏳ A sua subscrição ainda está a ser analisada pelos administradores.")
                else:
                    st.error("A sua permissão de acesso a este sistema foi recusada pela direção.")
            else:
                st.error("BI ou palavra-passe incorretos.")

    with aba2:
        st.subheader("Formulário de Subscrição de Acesso")
        with st.form("form_subscricao"):
            bi_sub = st.text_input("Número do BI (14 caracteres):")
            nome_sub = st.text_input("Nome Completo:")
            cargo_sub = st.selectbox("Função / Cargo Atual:", OPCOES_CARGOS)
            senha_sub = st.text_input("Escolha a sua Palavra-passe:", type="password")
            telefone_sub = st.text_input("Número de Telefone (9 dígitos):")
            
            submetido = st.form_submit_button("Avançar para Confirmação")

        if submetido:
            if not validar_bi_angolano(bi_sub):
                st.error("Formato de BI angolano inválido. Deve ter 14 caracteres.")
            elif not validar_telefone_angolano(telefone_sub):
                st.error("Número de telefone inválido.")
            else:
                st.session_state["temp_sub"] = {
                    "bi": bi_sub.strip(),
                    "nome": nome_sub.strip(),
                    "cargo": cargo_sub,
                    "senha": senha_sub,
                    "telefone": telefone_sub.strip()
                }

        if "temp_sub" in st.session_state:
            dados = st.session_state["temp_sub"]
            st.info("📌 **Confirme os seus dados antes de submeter:**")
            st.write(f"**BI:** {dados['bi']}")
            st.write(f"**Nome:** {dados['nome']}")
            st.write(f"**Cargo:** {dados['cargo']}")
            st.write(f"**Telefone:** {dados['telefone']}")

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("Confirmar Subscrição"):
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                        INSERT INTO usuarios_sistema (bi, nome_usuario, cargo, senha, telefone, status)
                        VALUES (?, ?, ?, ?, ?, 'EM_ANALISE')
                        """, (dados["bi"], dados["nome"], dados["cargo"], dados["senha"], dados["telefone"]))
                        conn.commit()
                        sincronizar_bases_json()
                        st.success("Subscrição gravada e sincronizada para análise dos administradores!")
                        del st.session_state["temp_sub"]
                    except sqlite3.IntegrityError:
                        st.error("Este BI já tem uma subscrição cadastrada.")
                    finally:
                        conn.close()
            with col_c2:
                if st.button("Corrigir Dados"):
                    del st.session_state["temp_sub"]
                    st.rerun()

if not st.session_state["autenticado"]:
    tela_login()
    st.stop()

st.sidebar.title(f"👤 {st.session_state['usuario_atual']}")
if st.sidebar.button("Terminar Sessão"):
    st.session_state["autenticado"] = False
    st.rerun()

""" Comande do Previsão do sistema """
st.title("📊 Painel de Previsão Climática e Orientação Agrícola")

aba_painel, aba_historico_geral = st.tabs(["🔮 Gerar / Consultar Previsão", "📜 Todas as Previsões Gravadas (Histórico Único)"])

with aba_painel:
    st.subheader("⚙️ Configurar Parâmetros da Previsão Climática")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        dias_previsao = st.slider("Selecione o horizonte de previsão (Até 90 dias / 3 meses):", min_value=7, max_value=90, value=30)
    with col_p2:
        dias_historico_base = st.slider("Número de dias passados gravados na base para basear a previsão:", min_value=7, max_value=90, value=20)

    if st.button("🚀 Gerar / Salvar Previsão na Base"):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        data_hoje = datetime.now().date()
        datas = [data_hoje + timedelta(days=i) for i in range(1, dias_previsao + 1)]
        
        np.random.seed(int(datetime.now().timestamp()) % 1000)
        
        for d in datas:
            prec = float(np.random.uniform(0, 25))
            temp = float(np.random.uniform(18, 33))
            hum = float(np.random.uniform(50, 90))
            
            cursor.execute("""
            INSERT INTO previsoes_historico (data_previsao, precipitacao, temp_solo, humidade)
            VALUES (?, ?, ?, ?)
            """, (d.strftime('%Y-%m-%d'), prec, temp, hum))
        
        conn.commit()
        conn.close()
        sincronizar_bases_json()
        st.success(f"Previsão gerada com sucesso a começar em {datas[0].strftime('%d/%m/%Y')} até {datas[-1].strftime('%d/%m/%Y')} e salva na base!")

    conn = sqlite3.connect(DB_NAME)
    df_previsoes = pd.read_sql_query("SELECT data_previsao, precipitacao, temp_solo, humidade FROM previsoes_historico ORDER BY id DESC LIMIT ?", conn, params=(dias_previsao,))
    conn.close()

    if not df_previsoes.empty:
        df_previsoes = df_previsoes.iloc[::-1].reset_index(drop=True)
        st.markdown("---")
        st.subheader("📈 Resumo Climático Projetado")
        
        st.dataframe(
            df_previsoes.style.format({'precipitacao': '{:.2f} mm', 'temp_solo': '{:.1f} °C', 'humidade': '{:.1f} %'})
        )

        st.markdown("---")
        st.subheader("🌱 Seleção de Cultura para Diretrizes Agrícolas")
        
        culturas = list(REGRAS_CULTURAS.keys())
        cultura_selecionada = st.selectbox("Escolha o produto cultivado na fazenda:", culturas)

        if cultura_selecionada:
            total_linhas = len(df_previsoes)
            intervalos = [f"Dias {i+1} até {min(i+15, total_linhas)}" for i in range(0, total_linhas, 15)]
            
            intervalo_escolhido = st.radio("Selecione o intervalo de exibição (Blocos de 15 dias):", intervalos, horizontal=True)
            idx_inicio = intervalos.index(intervalo_escolhido) * 15
            idx_fim = min(idx_inicio + 15, total_linhas)

            df_fatiado = df_previsoes.iloc[idx_inicio:idx_fim]

            tabela_diretrizes = []
            for _, row in df_fatiado.iterrows():
                irr, pla, cul = gerar_diretrizes_produto(cultura_selecionada, row["temp_solo"], row["humidade"], row["precipitacao"])
                tabela_diretrizes.append({
                    "Data": row["data_previsao"],
                    "Orientação de Irrigação": irr,
                    "Orientação de Plantio": pla,
                    "Orientação de Cultivo": cul
                })

            df_resultado = pd.DataFrame(tabela_diretrizes)
            st.table(df_resultado)

with aba_historico_geral:
    st.subheader("📜 Consultar Todas as Previsões Registradas na Base")
    st.write("Aqui estão exibidas todas as previsões climáticas efetuadas pelos utilizadores do sistema.")
    
    conn = sqlite3.connect(DB_NAME)
    df_todas = pd.read_sql_query("SELECT id, data_previsao, precipitacao, temp_solo, humidade, criado_em FROM previsoes_historico ORDER BY id DESC", conn)
    conn.close()

    if not df_todas.empty:
        st.dataframe(df_todas.style.format({'precipitacao': '{:.2f} mm', 'temp_solo': '{:.1f} °C', 'humidade': '{:.1f} %'}))
    else:
        st.info("Nenhuma previsão foi gerada ainda na base de dados.")