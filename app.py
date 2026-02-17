import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÃO PARA LER A FILA ---
def carregar_fila():
    # Use o link da sua planilha nova que termina com /gviz/tq?tqx=out:csv
    url_dados = "https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/gviz/tq?tqx=out:csv"
    try:
        # Lemos a planilha e forçamos a atualização
        df_fila = pd.read_csv(url_dados)
        return df_fila
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

# --- DICIONÁRIO DE TRADUÇÃO COMPLETO ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...",
        "fila_tit": "🎤 Fila de Espera",
        "vazio": "Fila vazia! Peça a primeira!",
        "sel": "Selecionado:",
        "pos": "Sua posição na fila será:",
        "conf": "Confirmar ✅",
        "canc": "Voltar ❌",
        "sucesso": "Pedido enviado com sucesso!",
        "outro": "Pedir outra música 🎤"
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...",
        "fila_tit": "🎤 Current Queue",
        "vazio": "Empty queue! Be the first!",
        "sel": "Selected:",
        "pos": "Your position will be:",
        "conf": "Confirm ✅",
        "canc": "Back ❌",
        "sucesso": "Request sent successfully!",
        "outro": "Request another song 🎤"
    },
    "Español 🇪🇦": {
        "busca": "Buscar música o artista...",
        "fila_tit": "🎤 Lista de espera",
        "vazio": "¡Lista vacía! ¡Pide la primera!",
        "sel": "Seleccionado:",
        "pos": "Tu posición será:",
        "conf": "Confirmar ✅",
        "canc": "Volver ❌",
        "sucesso": "¡Pedido enviado con éxito!",
        "outro": "Pedir otra canción 🎤"
    },
    "Français 🇫🇷": {
        "busca": "Chercher une chanson...",
        "fila_tit": "🎤 File d'attente",
        "vazio": "File vide ! Soyez le premier !",
        "sel": "Sélectionné :",
        "pos": "Votre position sera :",
        "conf": "Confirmer ✅",
        "canc": "Retour ❌",
        "sucesso": "Demande envoyée avec succès !",
        "outro": "Demander une autre chanson 🎤"
    }
}

st.title("🎤 Karaokê Coopers")

# Idiomas agora na tela principal
escolha = st.radio("Escolha o idioma / Select language:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

st.divider()

# --- EXIBIÇÃO DA FILA ---
st.subheader(t["fila_tit"])
df_atual = carregar_fila()

if not df_atual.empty:
    # Ajuste: Pega a coluna 3 (Música) e coluna 2 (Hora) para mostrar na fila
    # Na sua planilha Form_Responses2, a música parece estar na 4ª coluna (índice 3)
    try:
        fila_visual = df_atual.iloc[:, [1, 3]].tail(5) # Mostra as últimas 5
        fila_visual.columns = ["Hora", "Música"]
        st.table(fila_visual)
    except:
        st.write("Carregando fila...")
else:
    st.write(t["vazio"])

st.divider()

# --- LÓGICA DE PEDIDO ---
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
    
    # Todos os textos agora usam a variável t[] para tradução
    st.success(f"{t['sel']} {m.iloc[1]}")
    st.info(f"📢 {t['pos']} {posicao}º")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2])
            }
            requests.post(url_form, data=dados)
            st.balloons()
            st.success(t["sucesso"])
            st.button(t["outro"], on_click=voltar_inicio)
    with col2:
        if st.button(t["canc"], on_click=voltar_inicio):
            pass
