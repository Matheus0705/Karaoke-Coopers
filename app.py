import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- 1. FUNÇÕES DE APOIO ---
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

def voltar_inicio():
    st.session_state.musica_escolhida = None

# --- 2. MEMÓRIA DE PEDIDOS DO CLIENTE ---
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = []

# --- 3. DICIONÁRIO DE TRADUÇÃO ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...",
        "fila": "🎤 Fila de Espera",
        "meus_pedidos": "🎫 Meus Pedidos (Mostre ao DJ)",
        "vazio": "Fila vazia! Peça a primeira!",
        "sel": "Selecionado:",
        "pos": "Sua posição:",
        "conf": "Confirmar ✅",
        "sucesso": "Pedido enviado!",
        "erro": "Desculpe, não encontramos essa música...",
        "aviso_dj": "Cheque com o DJ sobre direitos autorais.",
        "dj_admin": "PAINEL DO DJ ATIVO 🎧"
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...",
        "fila": "🎤 Current Queue",
        "meus_pedidos": "🎫 My Tokens (Show to DJ)",
        "vazio": "Empty queue!",
        "sel": "Selected:",
        "pos": "Your position:",
        "conf": "Confirm ✅",
        "sucesso": "Sent!",
        "erro": "Song not found...",
        "aviso_dj": "Check with the DJ regarding copyrights.",
        "dj_admin": "DJ PANEL ACTIVE 🎧"
    },
    "Español 🇪🇦": {
        "busca": "Buscar canción o artista...",
        "fila": "🎤 Lista de espera",
        "meus_pedidos": "🎫 Mis pedidos (Mostrar al DJ)",
        "vazio": "¡Lista vacía!",
        "sel": "Seleccionado:",
        "pos": "Tu posición:",
        "conf": "Confirmar ✅",
        "sucesso": "¡Pedido enviado!",
        "erro": "Lo sentimos, canción no encontrada...",
        "aviso_dj": "Consulta con el DJ sobre los derechos de autor.",
        "dj_admin": "PANEL DE DJ ACTIVO 🎧"
    },
    "Français 🇫🇷": {
        "busca": "Chercher une chanson...",
        "fila": "🎤 File d'attente",
        "meus_pedidos": "🎫 Mes tickets (Montrer au DJ)",
        "vazio": "File vide !",
        "sel": "Sélectionné :",
        "pos": "Votre position :",
        "conf": "Confirmer ✅",
        "sucesso": "Envoyé !",
        "erro": "Désolé, chanson non trouvée...",
        "aviso_dj": "Vérifiez auprès du DJ pour les droits d'auteur.",
        "dj_admin": "PANNEAU DJ ACTIF 🎧"
    }
}

st.title("🎤 Karaokê Coopers")
escolha = st.radio("Idioma / Language:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

# --- 4. CARTÃO FIXO: MEUS PEDIDOS (CLIENTE) ---
if st.session_state.minhas_senhas:
    with st.expander(t["meus_pedidos"], expanded=True):
        for p in st.session_state.minhas_senhas:
            st.success(f"🎵 **{p['musica']}** | 🔑 SENHA: `{p['senha']}`")

st.divider()

# --- 5. FILA GERAL E MODO DJ ---
st.subheader(t["fila"])
df_atual = carregar_fila()

busca = st.text_input(t["busca"]).strip().lower()

# LÓGICA DO DJ
if busca == "coopersdj":
    st.warning(t["dj_admin"])
    if not df_atual.empty:
        musica_agora = df_atual.iloc[0, 3] # Coluna D da sua planilha
        st.write(f"📀 **Tocando agora:** {musica_agora}")
        
        if st.button("✅ CONCLUIR E CHAMAR PRÓXIMO", type="primary", use_container_width=True):
            url_script = "https://script.google.com/macros/s/AKfycbw_EO6sUbJOP1l6uXIsb9BtUHrb91ivduWCWplbLt1zaWexivJi_hPIKHz-n7hy5u7p/exec"
            try:
                r = requests.get(url_script)
                st.toast("Fila atualizada!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("Erro ao conectar com a planilha.")
    else:
        st.write("A fila está vazia.")
    st.stop() 

# EXIBIÇÃO DA FILA (CLIENTE)
if not df_atual.empty:
    try:
        # Colunas: 5 (Senha), 3 (Música), 4 (Artista)
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy() 
        fila_visual.columns = ["Senha", "Música", "Artista"]
        fila_visual.index = [f"{i+1}º" for i in range(len(fila_visual))]
        st.table(fila_visual)
    except:
        st.write("Atualizando...")
else:
    st.write(t["vazio"])

st.divider()

# --- 6. BUSCA E PEDIDO ---
df_catalogo = carregar_catalogo()

if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None

if st.session_state.musica_escolhida is None:
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
            st.caption(t["aviso_dj"])
else:
    m = st.session_state.musica_escolhida
    posicao = len(df_atual) + 1
    st.warning(f"{t['sel']} {m.iloc[1]}")
    st.info(f"📢 {t['pos']} {posicao}º")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
            token = gerar_senha()
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                "entry.1691316531": token  # ID DA SENHA
            }
            
            requests.post(url_form, data=dados)
            st.session_state.minhas_senhas.append({"musica": m.iloc[1], "senha": token})
            st.balloons()
            st.success(t["sucesso"])
            time.sleep(2)
            st.session_state.musica_escolhida = None
            st.rerun()
            
    with col2:
        if st.button("Voltar"):
            st.session_state.musica_escolhida = None
            st.rerun()
