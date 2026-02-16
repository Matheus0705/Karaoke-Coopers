import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

@st.cache_data
def carregar_catalogo():
    try:
        # Carrega o arquivo CSV que você subiu no GitHub
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return None

df_catalogo = carregar_catalogo()

# Dicionário de Tradução
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {"label": "Pesquisar música ou artista...", "sel": "Selecionado", "conf": "Confirmar ✅", "canc": "Voltar ❌", "sucesso": "Pedido Enviado! 🕺🏻"},
    "English 🇺🇸🇬🇧": {"label": "Search song or artist...", "sel": "Selected", "conf": "Confirm ✅", "canc": "Back ❌", "sucesso": "Request Sent! 🕺🏻"},
    "Español 🇪🇸": {"label": "Buscar música o artista...", "sel": "Seleccionado", "conf": "Confirmar ✅", "canc": "Volver ❌", "sucesso": "¡Enviado! 🕺🏻"},
    "Français 🇫🇷": {"label": "Chercher chanson ou artiste...", "sel": "Sélectionné", "conf": "Confirmer ✅", "canc": "Retour ❌", "sucesso": "Envoyé ! 🕺🏻"}
}

st.title("🎤 Karaokê Coopers")
idioma = st.radio("Idioma", list(idiomas_dict.keys()), horizontal=True)
t = idiomas_dict[idioma]

if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None

# Interface de Busca
if st.session_state.musica_escolhida is None:
    busca = st.text_input(t["label"]).strip().lower()
    if busca:
        res = df_catalogo[df_catalogo.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                          df_catalogo.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(10)
        for i, row in res.iterrows():
            if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"b_{i}"):
                st.session_state.musica_escolhida = row
                st.rerun()
else:
    m = st.session_state.musica_escolhida
    st.success(f"{t['sel']}: {m.iloc[1]} ({m.iloc[2]})")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
            # URL de submissão do seu formulário
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            # Dados mapeados com os IDs que extraímos do seu link
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"), # DATA
                "entry.1947522889": str(m.iloc[0]),                   # CODIGO
                "entry.1660854967": str(m.iloc[1]),                   # MUSICA
                "entry.700923343": str(m.iloc[2])                     # ARTISTA
            }
            
            try:
                # Faz o envio para o Google Forms
                requests.post(url_form, data=dados)
                st.balloons()
                st.success(t["sucesso"])
                # Botão para limpar a seleção e permitir nova busca
                if st.button("Pedir outra música 🎤"):
                    st.session_state.musica_escolhida = None
                    st.rerun()
            except:
                st.error("Erro de conexão ao enviar o pedido.")
    with col2:
        if st.button(t["canc"]):
            st.session_state.musica_escolhida = None
            st.rerun()
