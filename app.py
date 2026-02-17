import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÕES CORE ---
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    timestamp = int(time.time())
    # Link da planilha publicada como CSV
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        df.columns = [str(c).strip() for c in df.columns]
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
        return pd.DataFrame()

# --- ESTADO DA SESSÃO ---
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = []
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0

# --- INTERFACE (TÍTULO CORRIGIDO) ---
st.markdown("<h1 style='text-align: center;'>🎤 Karaokê Coopers</h1>", unsafe_content_html=True)

# --- TRADUÇÕES ---
idiomas = {
    "Português BR": {
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", 
        "fila": "Acompanhe sua vez aqui!", 
        "vazio": "Aguardando o primeiro pedido da noite...", 
        "sucesso": "SUA SENHA:",
        "col_pos": "Posição", "col_mus": "Música", "col_art": "Artista", "col_sen": "Senha"
    },
    "English us": {
        "busca": "SEARCH YOUR SONG OR ARTIST", 
        "fila": "Follow your turn here!", 
        "vazio": "Waiting for the first request...", 
        "sucesso": "YOUR TOKEN:",
        "col_pos": "Position", "col_mus": "Song", "col_art": "Artist", "col_sen": "Token"
    },
    "Español EA": {
        "busca": "BUSQUE SUA MÚSICA...", 
        "fila": "¡Sigue tu turno aquí!", 
        "vazio": "¡Lista vacía!", 
        "sucesso": "TU CÓDIGO:",
        "col_pos": "Posición", "col_mus": "Música", "col_art": "Artista", "col_sen": "Código"
    },
    "Français FR": {
        "busca": "CHERCHEZ VOTRE MUSIQUE...", 
        "fila": "Suivez votre tour aqui!", 
        "vazio": "File d'attente vide!", 
        "sucesso": "VOTRE CODE:",
        "col_pos": "Position", "col_mus": "Musique", "col_art": "Artiste", "col_sen": "Code"
    }
}
escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True, label_visibility="collapsed")
t = idiomas[escolha]

# --- BOX DE SENHAS DO CLIENTE (FIXO NO TOPO) ---
if st.session_state.minhas_senhas:
    with st.expander("🎫 Meus Pedidos (Mostre ao DJ)", expanded=True):
        for s in st.session_state.minhas_senhas:
            st.info(f"🎵 {s['musica']} | 🔑 {t['sucesso']} {s['senha']}")

st.divider()

# --- FILA DE ESPERA (ESTÉTICA PEDIDA) ---
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pega Senha (5), Música (3) e Artista (4)
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy()
        
        # Cria a coluna "Posição" à esquerda
        posicoes = [f"{i+1}º" for i in range(len(fila_visual))]
        fila_visual.insert(0, t["col_pos"], posicoes)
        
        # Nomeia as colunas conforme o idioma
        fila_visual.columns = [t["col_pos"], t["col_sen"], t["col_mus"], t["col_art"]]
        
        # Exibe a tabela sem o índice lateral do pandas
        st.table(fila_visual)
    except:
        st.write(t["vazio"])
else:
    st.write(t["vazio"])

st.divider()

# --- BUSCA E PEDIDO ---
if st.session_state.musica_escolhida is None:
    busca = st.text_input(t["busca"], key=f"in_{st.session_state.reset_busca}").strip().upper()
    if busca:
        df_cat = carregar_catalogo()
        if not df_cat.empty:
            res = df_cat[df_cat.iloc[:, 1].str.contains(busca, case=False, na=False) | 
                         df_cat.iloc[:, 2].str.contains(busca, case=False, na=False)].head(10)
            
            if not res.empty:
                for i, row in res.iterrows():
                    if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"m_{i}"):
                        st.session_state.musica_escolhida = row
                        st.rerun()
else:
    m = st.session_state.musica_escolhida
    st.success(f"Selecionada: {m.iloc[1]}")
    st.info(f"Sua posição na fila será: {len(df_atual)+1}º")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("CONFIRMAR ✅", type="primary", use_container_width=True):
            nova_senha = gerar_senha()
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            # --- LEMBRE-SE DE CONFERIR ESTE ID ---
            id_da_senha = "entry.18065" 
            
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                id_da_senha: nova_senha
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
                st.error("Erro na conexão.")
            
    with col_c2:
        if st.button("CANCELAR ❌", use_container_width=True):
            st.session_state.musica_escolhida = None
            st.rerun()
