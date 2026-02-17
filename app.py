import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# 1. Configuração de Página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# 2. Funções Core
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&gid=403883912&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=30)
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 3. Estado da Sessão
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = []
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0

# 4. Título
st.title("🎤 Karaokê Coopers")

# 5. Dicionário de Idiomas (Regra dos 4 idiomas + Avisos)
idiomas = {
    "Português BR": {
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", "fila": "Acompanhe sua vez aqui!", 
        "vazio": "Aguardando pedidos...", "sucesso": "SUA SENHA:",
        "col_pos": "Posição", "col_sen": "Senha", "col_mus": "Música", "col_art": "Artista",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Selecionada:",
        "aviso_fila": "ℹ️ A fila atualiza automaticamente a cada 30 segundos.",
        "processando": "DJ salvando seu pedido... Aguarde!",
        "alerta_confirm": "⚠️ Ao confirmar, sua música entrará na fila oficial."
    },
    "English us": {
        "busca": "SEARCH YOUR SONG OR ARTIST", "fila": "Follow your turn here!", 
        "vazio": "Waiting for requests...", "sucesso": "YOUR TOKEN:",
        "col_pos": "Position", "col_sen": "Token", "col_mus": "Song", "col_art": "Artist",
        "btn_conf": "CONFIRM ✅", "btn_canc": "CANCEL ❌", "sel": "Selected:",
        "aviso_fila": "ℹ️ The queue updates automatically every 30 seconds.",
        "processando": "DJ saving your request... Please wait!",
        "alerta_confirm": "⚠️ By confirming, your song will enter the official queue."
    },
    "Español EA": {
        "busca": "BUSCAR MÚSICA O ARTISTA", "fila": "¡Sigue tu turno aquí!", 
        "vazio": "Esperando pedidos...", "sucesso": "TU CÓDIGO:",
        "col_pos": "Posición", "col_sen": "Código", "col_mus": "Música", "col_art": "Artista",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Seleccionada:",
        "aviso_fila": "ℹ️ La fila se actualiza cada 30 segundos.",
        "processando": "¡DJ guardando su pedido! ¡Espere!",
        "alerta_confirm": "⚠️ Al confirmar, tu canción entrará en la fila oficial."
    },
    "Français FR": {
        "busca": "CHERCHER MUSIQUE OU ARTISTE", "fila": "Suivez votre tour ici!", 
        "vazio": "En attente de demandes...", "sucesso": "VOTRE CODE:",
        "col_pos": "Position", "col_sen": "Code", "col_mus": "Musique", "col_art": "Artiste",
        "btn_conf": "CONFIRMER ✅", "btn_canc": "ANNULER ❌", "sel": "Sélectionnée:",
        "aviso_fila": "ℹ️ La file d'attente s'actualise toutes les 30 secondes.",
        "processando": "DJ enregistre votre demande... Attendez!",
        "alerta_confirm": "⚠️ En confirmant, votre chanson entrera dans la file officielle."
    }
}

escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True, label_visibility="collapsed")
t = idiomas[escolha]

# 6. Box de Meus Pedidos
if st.session_state.minhas_senhas:
    with st.expander("🎫 MEUS PEDIDOS / MY REQUESTS", expanded=True):
        for s in st.session_state.minhas_senhas:
            st.info(f"🎵 {s['musica']} | 🔑 {t['sucesso']} {s['senha']}")

st.divider()

# 7. Tabela de Fila
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy()
        posicoes = [f"{i+1}º" for i in range(len(fila_visual))]
        fila_visual.insert(0, t["col_pos"], posicoes)
        fila_visual.columns = [t["col_pos"], t["col_sen"], t["col_mus"], t["col_art"]]
        st.table(fila_visual)
        st.caption(t["aviso_fila"])
    except:
        st.write(t["vazio"])
else:
    st.write(t["vazio"])

st.divider()

# 8. Busca e Confirmação com Avisos
if st.session_state.musica_escolhida is None:
    busca = st.text_input(t["busca"], key=f"in_{st.session_state.reset_busca}", placeholder="Ex: Queen, Evidências...").strip().upper()
    if busca:
        df_cat = carregar_catalogo()
        if not df_cat.empty:
            res = df_cat[df_cat.iloc[:, 1].str.contains(busca, case=False, na=False) | 
                         df_cat.iloc[:, 2].str.contains(busca, case=False, na=False)].head(10)
            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"s_{i}", use_container_width=True):
                    st.session_state.musica_escolhida = row
                    st.rerun()
else:
    m = st.session_state.musica_escolhida
    st.success(f"{t['sel']} {m.iloc[1]}")
    st.warning(t["alerta_confirm"]) # AVISO DE ATENÇÃO
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["btn_conf"], type="primary", use_container_width=True):
            with st.spinner(t["processando"]): # AVISO DE PROCESSAMENTO
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
                    st.error("Erro ao enviar pedido. Tente novamente!")
    with col2:
        if st.button(t["btn_canc"], use_container_width=True):
            st.session_state.musica_escolhida = None
            st.rerun()
