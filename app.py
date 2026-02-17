import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# 1. Configuração de Página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÕES CORE ---
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    timestamp = int(time.time())
    url = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60) # Cache de 1 minuto para o catálogo não pesar
def carregar_catalogo():
    try:
        return pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
    except:
        return pd.DataFrame()

# --- ESTADO DA SESSÃO ---
if 'minhas_senhas' not in st.session_state: st.session_state.minhas_senhas = []
if 'musica_escolhida' not in st.session_state: st.session_state.musica_escolhida = None

# --- INTERFACE ---
st.markdown("<h1 style='text-align: center;'>🎤 Karaokê Coopers</h1>", unsafe_content_html=True)

idiomas = {
    "Português 🇧🇷": {
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", 
        "fila": "Acompanhe sua vez aqui!", 
        "vazio": "Aguardando o primeiro pedido...",
        "sucesso": "SUA SENHA:",
        "erro_dj": "Desculpe, no momento não temos essa música. Cheque com o DJ!"
    },
    "English 🇺🇸": {
        "busca": "SEARCH YOUR SONG OR ARTIST", 
        "fila": "Follow your turn here!", 
        "vazio": "Waiting for the first request...",
        "sucesso": "YOUR TOKEN:",
        "erro_dj": "Song not found. Check with the DJ!"
    }
}

escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True, label_visibility="collapsed")
t = idiomas[escolha]

# Exibição de Senhas (Box Azul Fixo)
if st.session_state.minhas_senhas:
    for s in st.session_state.minhas_senhas:
        st.info(f"🔑 {t['sucesso']} {s['senha']} | 🎵 {s['musica']}")

st.divider()

# --- FILA DE ESPERA ---
df_atual = carregar_fila()
with st.expander(f"📊 {t['fila']}", expanded=True):
    if not df_atual.empty:
        try:
            exibir = df_atual.iloc[:, [5, 3, 4]].copy()
            exibir.columns = ["Senha", "Música", "Artista"]
            exibir.index = [f"{i+1}º" for i in range(len(exibir))]
            st.table(exibir)
        except: st.write(t["vazio"])
    else: st.write(t["vazio"])

st.divider()

# --- LÓGICA DE BUSCA ---
if st.session_state.musica_escolhida is None:
    # Usamos uma chave que NUNCA muda para evitar o erro de recarregamento
    busca = st.text_input(t["busca"], key="campo_pesquisa_fixo").strip().upper()
    
    if busca:
        cat = carregar_catalogo()
        res = cat[cat.iloc[:, 1].str.contains(busca, case=False, na=False) | 
                  cat.iloc[:, 2].str.contains(busca, case=False, na=False)].head(10)
        
        if not res.empty:
            for i, row in res.iterrows():
                # On_click ajuda a evitar o clique duplo
                if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"s_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
        else:
            st.warning(t["erro_dj"])
else:
    # TELA DE CONFIRMAÇÃO
    m = st.session_state.musica_escolhida
    st.success(f"✅ Selecionada: {m.iloc[1]}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("CONFIRMAR ✅", type="primary", use_container_width=True):
            senha = gerar_senha()
            payload = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                "entry.18065": senha # Troque pelo seu ID
            }
            requests.post("https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse", data=payload)
            
            st.session_state.minhas_senhas.append({"musica": m.iloc[1], "senha": senha})
            st.balloons()
            
            # O TRUQUE PARA LIMPAR A BUSCA:
            st.session_state.musica_escolhida = None
            st.session_state.campo_pesquisa_fixo = "" # Limpa o valor do campo diretamente
            time.sleep(1)
            st.rerun()
    with c2:
        if st.button("CANCELAR ❌", use_container_width=True):
            st.session_state.musica_escolhida = None
            st.rerun()
