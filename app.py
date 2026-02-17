import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# 1. CONFIGURAÇÃO DE TEMA (Cores do Logo)
# Altere os hexadecimais abaixo para as cores exatas do seu logo
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117; /* Fundo escuro */
    }
    .stButton>button {
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df_catalogo = carregar_catalogo()

# --- ESTADO DO SISTEMA ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'contador_reset' not in st.session_state:
    st.session_state.contador_reset = 0
if 'minha_senha' not in st.session_state:
    st.session_state.minha_senha = None

# --- TRADUÇÕES ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...",
        "fila": "🎤 Fila de Espera",
        "vazio": "Fila vazia! Peça a primeira!",
        "col_pos": "Posição", "col_mus": "Música", "col_art": "Artista",
        "sel": "Selecionado:", "conf": "Confirmar ✅", "canc": "Cancelar ❌",
        "sucesso": "Pedido enviado!", "senha_msg": "SUA SENHA:",
        "aviso": "Esta senha é sua identificação para o DJ!",
        "erro": "Música não encontrada. Cheque com o DJ!"
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...",
        "fila": "🎤 Current Queue",
        "vazio": "Empty queue!",
        "col_pos": "Position", "col_mus": "Song", "col_art": "Artist",
        "sel": "Selected:", "conf": "Confirm ✅", "canc": "Cancel ❌",
        "sucesso": "Sent successfully!", "senha_msg": "YOUR TOKEN:",
        "aviso": "This token is your ID for the DJ!",
        "erro": "Song not found. Check with the DJ!"
    }
}

# --- LOGO ---
# Substitua 'logo.png' pelo caminho do seu arquivo de logo no GitHub
try:
    st.image("logo.png", width=150) 
except:
    st.title("🎤 Karaokê Coopers")

escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

# --- EXIBIÇÃO DA FILA (SEM SENHA PÚBLICA) ---
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Mostramos apenas Música (3) e Artista (4). Senha (5) fica oculta.
        fila_visual = df_atual.iloc[:, [3, 4]].copy()
        fila_visual.columns = [t["col_mus"], t["col_art"]]
        
        # Criando a coluna de Posição como solicitado
        posicoes = [f"{i+1}º" for i in range(len(fila_visual))]
        fila_visual.insert(0, t["col_pos"], posicoes)
        
        st.table(fila_visual)
    except:
        st.write("Atualizando...")
else:
    st.write(t["vazio"])

# --- SENHA PRIVADA (Aparece apenas para o dono do celular) ---
if st.session_state.minha_senha:
    st.info(f"🔑 {t['senha_msg']} **{st.session_state.minha_senha}**")

st.divider()

# --- LÓGICA DE PEDIDO ---
if st.session_state.musica_escolhida is None:
    busca = st.text_input(t["busca"], key=f"input_{st.session_state.contador_reset}").strip().lower()
    if busca:
        res = df_catalogo[df_catalogo.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                          df_catalogo.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(10)
        if not res.empty:
            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"b_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
        else:
            st.error(t["erro"])
else:
    m = st.session_state.musica_escolhida
    st.success(f"{t['sel']} {m.iloc[1]}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
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
                requests.post(url_form, data=dados)
                # Salva a senha apenas neste navegador
                st.session_state.minha_senha = nova_senha 
                
                st.snow() # Efeito de neve (mais elegante que balões)
                st.toast(t["sucesso"])
                
                st.session_state.musica_escolhida = None
                st.session_state.contador_reset += 1
                time.sleep(2)
                st.rerun()
            except:
                st.error("Erro na conexão.")
    with col2:
        if st.button(t["canc"]):
            st.session_state.musica_escolhida = None
            st.rerun()
