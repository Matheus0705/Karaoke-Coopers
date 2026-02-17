import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÃO PARA LER A FILA ---
def carregar_fila():
    # LINK NOVO formatado para exportação CSV e sem cache
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1g88-tIUw0xLedVBlp2UuZmkFG0nAOW1ef58q5j9Jndk/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        # Limpar nomes de colunas
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

def voltar_inicio():
    st.session_state.musica_escolhida = None
    st.rerun()

# --- TRADUÇÕES ---
idiomas = {
    "Português 🇧🇷": {"busca": "Pesquisar música...", "fila": "🎤 Fila de Espera", "vazio": "Fila vazia! Peça a primeira!", "sel": "Selecionado:", "pos": "Sua posição:", "conf": "Confirmar ✅", "outro": "Nova Música 🎤"},
    "English 🇺🇸": {"busca": "Search song...", "fila": "🎤 Current Queue", "vazio": "Empty queue!", "sel": "Selected:", "pos": "Your position:", "conf": "Confirm ✅", "outro": "New Song 🎤"},
    "Español 🇪🇦": {"busca": "Buscar música...", "fila": "🎤 Lista de espera", "vazio": "¡Lista vacía!", "sel": "Seleccionado:", "pos": "Tu posición:", "conf": "Confirmar ✅", "outro": "Nueva canción 🎤"},
    "Français 🇫🇷": {"busca": "Chercher...", "fila": "🎤 File d'attente", "vazio": "File vide !", "sel": "Sélectionné :", "pos": "Votre position :", "conf": "Confirmer ✅", "outro": "Nouvelle chanson 🎤"}
}

escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

st.divider()

# --- EXIBIÇÃO DA FILA AO VIVO ---
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pega as colunas de Música (índice 3) e Artista (índice 4)
        fila_visual = df_atual.iloc[:, [3, 4]].copy()
        fila_visual.columns = ["Música", "Artista"]
        # Cria o 1º, 2º, 3º...
        fila_visual.index = [f"{i+1}º" for i in range(len(fila_visual))]
        st.table(fila_visual)
    except:
        st.write("Atualizando lista...")
else:
    st.write(t["vazio"])

st.divider()

# --- SISTEMA DE PEDIDO ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None

if st.session_state.musica_escolhida is None:
    busca = st.text_input(t["busca"]).strip().lower()
    if busca:
        res = df_catalogo[df_catalogo.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                          df_catalogo.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(10)
        for i, row in res.iterrows():
            if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"b_{i}"):
                st.session_state.musica_escolhida = row
                st.rerun()
else:
    m = st.session_state.musica_escolhida
    posicao = len(df_atual) + 1
    st.success(f"{t['sel']} {m.iloc[1]}")
    st.info(f"📢 {t['pos']} {posicao}º")

    if st.button(t["conf"], type="primary"):
        # USANDO O SEU NOVO LINK DE FORMULÁRIO (se mudou o form, verifique os entries)
        url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
        dados = {
            "entry.1213556115": datetime.now().strftime("%H:%M"),
            "entry.1947522889": str(m.iloc[0]),
            "entry.1660854967": str(m.iloc[1]),
            "entry.700923343": str(m.iloc[2])
        }
        requests.post(url_form, data=dados)
        st.balloons()
        st.success("Enviado!")
        st.button(t["outro"], on_click=voltar_inicio)
