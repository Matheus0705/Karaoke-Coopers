import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

@st.cache_data
def carregar_catalogo():
    try:
        # Carrega o CSV local
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return None

df_catalogo = carregar_catalogo()

# 2. Dicionário de Tradução
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {
        "label": "Pesquisar música ou artista:",
        "sel": "Selecionado",
        "conf": "Confirmar Música ✅",
        "canc": "Voltar / Trocar ❌",
        "sucesso": "Pedido enviado com sucesso! 🎉"
    },
    "English 🇺🇸🇬🇧": {
        "label": "Search song or artist:",
        "sel": "Selected",
        "conf": "Confirm Song ✅",
        "canc": "Back / Change ❌",
        "sucesso": "Order sent successfully! 🎉"
    },
    "Español 🇪🇸": {
        "label": "Buscar música o artista:",
        "sel": "Seleccionado",
        "conf": "Confirmar Canción ✅",
        "canc": "Volver / Cambiar ❌",
        "sucesso": "¡Pedido enviado con éxito! 🎉"
    },
    "Français 🇫🇷": {
        "label": "Rechercher chanson ou artiste :",
        "sel": "Sélectionné",
        "conf": "Confirmer ✅",
        "canc": "Retour / Changer ❌",
        "sucesso": "Commande envoyée ! 🎉"
    }
}

# 3. Interface
st.title("🎤 Karaokê Coopers")

idioma = st.radio("Escolha o idioma / Select language:", list(idiomas_dict.keys()), horizontal=True)
t = idiomas_dict[idioma]

if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None

if st.session_state.musica_escolhida is None:
    # TELA DE BUSCA
    busca = st.text_input(t["label"]).strip().lower()
    if busca:
        res = df_catalogo[
            df_catalogo.iloc[:, 1].astype(str).str.lower().str.contains(busca, na=False) | 
            df_catalogo.iloc[:, 2].astype(str).str.lower().str.contains(busca, na=False)
        ].head(10)

        for i, row in res.iterrows():
            if st.button(f"🎶 {row.iloc[0]} - {row.iloc[1]} - {row.iloc[2]}", key=f"btn_{i}"):
                st.session_state.musica_escolhida = row
                st.rerun()
else:
    # TELA DE CONFIRMAÇÃO
    m = st.session_state.musica_escolhida
    st.success(f"{t['sel']}: {m.iloc[1]}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
            # URL de envio do teu Google Form (termina em formResponse)
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            # Dados mapeados com os IDs que me enviaste
            dados_envio = {
                "entry.1213556115": datetime.now().strftime("%H:%M:%S"), # Data/Hora
                "entry.1947522889": str(m.iloc[0]),                    # Código
                "entry.1660854967": str(m.iloc[1]),                    # Música
                "entry.700923343": str(m.iloc[2])                      # Artista
            }
            
            try:
                # Envia os dados para a planilha via Formulário
                requests.post(url_form, data=dados_envio)
                st.balloons()
                st.success(t["sucesso"])
                
                # Botão para resetar e permitir nova música
                if st.button("Pedir outra música"):
                    st.session_state.musica_escolhida = None
                    st.rerun()
            except:
                st.error("Erro ao enviar pedido. Verifique a internet.")
                
    with col2:
        if st.button(t["canc"]):
            st.session_state.musica_escolhida = None
            st.rerun()
