import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração Base
st.set_page_config(page_title="Karaokê Coopers", layout="centered")

# --- GERADOR DE SENHA ---
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# --- LEITURA DA PLANILHA (O segredo está no cache_resource aqui) ---
def carregar_fila():
    timestamp = int(time.time())
    url = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data
def carregar_catalogo():
    try:
        return pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
    except:
        return pd.DataFrame()

# --- ESTADO DA SESSÃO ---
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = []
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0

# --- TÍTULO SIMPLES (Para nunca mais dar erro) ---
st.title("🎤 Karaokê Coopers")

# --- SENHAS FIXAS DO USUÁRIO ---
if st.session_state.minhas_senhas:
    for s in st.session_state.minhas_senhas:
        st.info(f"✅ Pedido: {s['musica']} | SENHA: {s['senha']}")

st.divider()

# --- FILA DE ESPERA ---
st.subheader("Acompanhe sua vez aqui!")
df_atual = carregar_fila()
if not df_atual.empty:
    try:
        # Pega Senha (5), Música (3) e Artista (4) - Colunas F, D, E
        exibir = df_atual.iloc[:, [5, 3, 4]].copy()
        exibir.columns = ["Senha", "Música", "Artista"]
        exibir.index = [f"{i+1}º" for i in range(len(exibir))]
        st.table(exibir)
    except:
        st.warning("Aguardando novos pedidos...")
else:
    st.write("Fila vazia! Seja o primeiro!")

st.divider()

# --- BUSCA E PEDIDO ---
if st.session_state.musica_escolhida is None:
    # O reset_key limpa o campo automaticamente após o pedido
    busca = st.text_input("PESQUISE SUA MÚSICA OU ARTISTA", key=f"busca_{st.session_state.reset_key}").strip().upper()
    if busca:
        cat = carregar_catalogo()
        res = cat[cat.iloc[:, 1].str.contains(busca, case=False, na=False) | 
                  cat.iloc[:, 2].str.contains(busca, case=False, na=False)].head(10)
        for i, row in res.iterrows():
            if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"m_{i}"):
                st.session_state.musica_escolhida = row
                st.rerun()
else:
    m = st.session_state.musica_escolhida
    st.success(f"Selecionada: {m.iloc[1]}")
    
    if st.button("CONFIRMAR ✅", type="primary", use_container_width=True):
        token = gerar_senha()
        # --- COLOQUE O SEU ID DO FORMS AQUI ---
        id_senha = "entry.18065" 
        
        payload = {
            "entry.1213556115": datetime.now().strftime("%H:%M"),
            "entry.1947522889": str(m.iloc[0]),
            "entry.1660854967": str(m.iloc[1]),
            "entry.700923343": str(m.iloc[2]),
            id_senha: token
        }
        
        try:
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse", data=payload)
            st.session_state.minhas_senhas.append({"musica": m.iloc[1], "senha": token})
            st.balloons()
            st.session_state.musica_escolhida = None
            st.session_state.reset_key += 1 # Isso limpa a caixa de texto
            time.sleep(1)
            st.rerun()
        except:
            st.error("Erro ao enviar. Tente novamente.")

    if st.button("CANCELAR ❌", use_container_width=True):
        st.session_state.musica_escolhida = None
        st.rerun()
