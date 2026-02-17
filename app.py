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
    timestamp = int(time.time() * 1000)
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&gid=403883912&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados, storage_options={'Cache-Control': 'no-cache'})
        if not df.empty:
            df = df.dropna(subset=[df.columns[3]])
            df = df[df.iloc[:, 3].str.strip() != ""]
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=10)
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
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

# 5. Dicionário de Idiomas
idiomas = {
    "Português BR": {
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", "fila": "Acompanhe sua vez aqui!", 
        "vazio": "Aguardando pedidos na fila...", "sucesso": "SUA SENHA:",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Selecionada:",
        "aviso_fila": "ℹ️ A fila atualiza automaticamente.",
        "processando": "DJ salvando seu pedido...",
        "alerta_confirm": "⚠️ Ao confirmar, sua música entrará na fila oficial."
    },
    "English us": {
        "busca": "SEARCH YOUR SONG OR ARTIST", "fila": "Follow your turn here!", 
        "vazio": "Waiting for requests...", "sucesso": "YOUR TOKEN:",
        "btn_conf": "CONFIRM ✅", "btn_canc": "CANCEL ❌", "sel": "Selected:",
        "aviso_fila": "ℹ️ The queue updates automatically.",
        "processando": "DJ saving your request...",
        "alerta_confirm": "⚠️ By confirming, your song will enter the official queue."
    },
    "Español EA": {
        "busca": "BUSCAR MÚSICA O ARTISTA", "fila": "¡Sigue tu turno aquí!", 
        "vazio": "Esperando pedidos...", "sucesso": "TU CÓDIGO:",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Seleccionada:",
        "aviso_fila": "La fila se actualiza automáticamente.",
        "processando": "¡DJ guardando su pedido!",
        "alerta_confirm": "⚠️ Al confirmar, tu canción entrará en la fila oficial."
    },
    "Français FR": {
        "busca": "CHERCHER MUSIQUE OU ARTISTE", "fila": "Suivez votre tour ici!", 
        "vazio": "En attente de demandes...", "sucesso": "VOTRE CODE:",
        "btn_conf": "CONFIRMER ✅", "btn_canc": "ANNULER ❌", "sel": "Sélectionnée:",
        "aviso_fila": "La file d'attente s'actualise automatiquement.",
        "processando": "DJ enregistre votre demande...",
        "alerta_confirm": "⚠️ En confirmant, votre chanson entrera dans la file officielle."
    }
}

escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True, label_visibility="collapsed")
t = idiomas[escolha]

# 6. Auto-Refresh automático (30 segundos)
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = time.time()
    st.rerun()

# 7. Meus Pedidos
if st.session_state.minhas_senhas:
    with st.expander("🎫 MEUS PEDIDOS / MY REQUESTS", expanded=True):
        for s in st.session_state.minhas_senhas:
            st.info(f"🎵 {s['musica']} | 🔑 {t['sucesso']} {s['senha']}")

st.divider()

# 8. Fila de Espera
st.subheader(t["fila"])
df_fila = carregar_fila()

if not df_fila.empty:
    for i in range(len(df_fila)):
        try:
            m_f = df_fila.iloc[i, 3]
            a_f = df_fila.iloc[i, 4]
            s_f = df_fila.iloc[i, 5]
            st.success(f"**{i+1}º** — 🎵 **{m_f}** ({a_f})  \n🔑 {t['sucesso']} **{s_f}**")
        except:
            continue
    st.caption(t["aviso_fila"])
else:
    st.warning(t["vazio"])

st.divider()

# 9. Busca e Confirmação
if st.session_state.musica_escolhida is None:
    # Usei o reset_busca para limpar o campo após o envio
    busca = st.text_input(t["busca"], key=f"in_{st.session_state.reset_busca}", placeholder="Ex: Queen...").strip().upper()
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
    st.info(f"✨ **{t['sel']}** {m.iloc[1]} - {m.iloc[2]}")
    st.warning(t["alerta_confirm"])
    
    col1, col2 = st.columns(2)
    with col1:
        # Mudança principal: O botão dispara uma função direta
        if st.button(t["btn_conf"], type="primary", use_container_width=True):
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
                # Post sem spinner travando o rerun
                requests.post(url_form, data=dados, timeout=5)
                st.session_state.minhas_senhas.append({"musica": m.iloc[1], "senha": nova_senha})
                # Reseta os estados ANTES do rerun
                st.session_state.musica_escolhida = None
                st.session_state.reset_busca += 1
                st.balloons()
                time.sleep(0.5) # Pausa mínima só para o balão começar
                st.rerun()
            except:
                st.error("Erro ao enviar.")
    with col2:
        if st.button(t["btn_canc"], use_container_width=True):
            st.session_state.musica_escolhida = None
            st.rerun()
