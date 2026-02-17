import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string
import unicodedata

# 1. Configuração de Página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÕES DE APOIO ---
def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                  if unicodedata.category(c) != 'Mn').lower()

def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    timestamp = int(time.time())
    # URL ATUALIZADA COM O SEU GID: 403883912
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&gid=403883912&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- ESTADO DA SESSÃO ---
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = []
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0

# --- INTERFACE (LOGO + TÍTULO) ---
col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
with col_l2:
    # Link direto (RAW) para a logo no seu GitHub
    logo_url = "https://raw.githubusercontent.com/MatheusS77/Coopers/main/9d8daa_198ec12882054dceb6d49d760eba30f0~mv2.jpg"
    st.image(logo_url, width=250)

st.markdown("<h1 style='text-align: center; margin-top: -10px;'>🎤 Karaokê Coopers</h1>", unsafe_allow_html=True)

# --- TRADUÇÕES ---
idiomas = {
    "Português BR": {
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", "fila": "Acompanhe sua vez aqui!", 
        "vazio": "Aguardando pedidos na fila...", "sucesso": "SUA SENHA:",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Selecionada:"
    },
    "English us": {
        "busca": "SEARCH YOUR SONG OR ARTIST", "fila": "Follow your turn here!", 
        "vazio": "Waiting for requests...", "sucesso": "YOUR TOKEN:",
        "btn_conf": "CONFIRM ✅", "btn_canc": "CANCEL ❌", "sel": "Selected:"
    },
    "Español EA": {
        "busca": "BUSCAR MÚSICA O ARTISTA", "fila": "¡Sigue tu turno aquí!", 
        "vazio": "Esperando pedidos...", "sucesso": "TU CÓDIGO:",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Seleccionada:"
    },
    "Français FR": {
        "busca": "CHERCHER MUSIQUE OU ARTISTE", "fila": "Suivez votre tour aqui!", 
        "vazio": "En attente de demandes...", "sucesso": "VOTRE CODE:",
        "btn_conf": "CONFIRMER ✅", "btn_canc": "ANNULER ❌", "sel": "Sélectionnée:"
    }
}
escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True, label_visibility="collapsed")
t = idiomas[escolha]

# --- AUTO-REFRESH (30s) ---
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

# --- SEÇÃO: MEUS PEDIDOS ---
if st.session_state.minhas_senhas:
    with st.expander("🎫 MEUS PEDIDOS / MY REQUESTS", expanded=True):
        for s in st.session_state.minhas_senhas:
            st.info(f"🎵 {s['musica']} | 🔑 {t['sucesso']} {s['senha']}")

st.divider()

# --- SEÇÃO: FILA DE ESPERA (ESTILO CARDS) ---
st.subheader(f"🎤 {t['fila']}")
df_fila = carregar_fila()

if not df_fila.empty:
    for i, row in df_fila.iterrows():
        try:
            # Mapeamento conforme sua planilha: D(3)=Música, E(4)=Artista, F(5)=Senha
            musica_f = row.iloc[3]
            artista_f = row.iloc[4]
            senha_f = row.iloc[5]
            
            st.success(f"**{i+1}º** — 🎵 **{musica_f}** ({artista_f})  \n🔑 {t['sucesso']} **{senha_f}**")
        except:
            continue
else:
    st.warning(t["vazio"])

st.divider()

# --- BUSCA E PEDIDO ---
if st.session_state.musica_escolhida is None:
    input_usuario = st.text_input(t["busca"], key=f"in_{st.session_state.reset_busca}").strip()
    
    if input_usuario:
        busca_limpa = remover_acentos(input_usuario)
        df_cat = carregar_catalogo()
        
        if not df_cat.empty:
            res = df_cat[df_cat.apply(lambda x: busca_limpa in remover_acentos(x.iloc[1]) or busca_limpa in remover_acentos(x.iloc[2]), axis=1)].head(10)
            
            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"s_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
else:
    m = st.session_state.musica_escolhida
    # Texto 'Selecionada' agora traduz corretamente
    st.info(f"✨ **{t['sel']}** {m.iloc[1]} - {m.iloc[2]}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["btn_conf"], type="primary", use_container_width=True):
            with st.spinner("Enviando..."):
                nova_senha = gerar_senha()
                url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
                
                dados = {
                    "entry.1213556115": datetime.now().strftime("%H:%M"),
                    "entry.1947522889": str(m.iloc[0]),
                    "entry.1660854967": str(m.iloc[1]),
                    "entry.700923343": str(m.iloc[2]),
                    "entry.694761068": nova_senha
                }
                
                try:
                    requests.post(url_form, data=dados, timeout=5)
                    st.session_state.minhas_senhas.append({"musica": m.iloc[1], "senha": nova_senha})
                    st.balloons()
                    st.session_state.musica_escolhida = None
                    st.session_state.reset_busca += 1
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("Erro ao conectar.")
    with col2:
        if st.button(t["btn_canc"], use_container_width=True):
            st.session_state.musica_escolhida = None
            st.rerun()
