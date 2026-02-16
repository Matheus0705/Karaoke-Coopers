import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers Portugal", layout="centered", page_icon="🎤")

# --- FUNÇÕES DE CARREGAMENTO ---
@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = df.columns.str.strip()
        
        # Mapeamento para evitar erros de acento (KeyError)
        col_map = {}
        for col in df.columns:
            c = col.lower()
            if 'mús' in c or 'mus' in c: col_map['musica'] = col
            if 'art' in c: col_map['artista'] = col
            if 'cód' in c or 'cod' in c: col_map['codigo'] = col
        return df, col_map
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return None, None

df_catalogo, col_map = carregar_catalogo()

# --- DICIONÁRIO DE TRADUÇÃO COMPLETO ---
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {
        "label": "Digite o nome da música ou artista:",
        "selecionado": "Selecionado",
        "confirmar": "Confirmar Música ✅",
        "cancelar": "Voltar / Trocar ❌",
        "posicao": "Sua posição na fila:",
        "aviso_fila": "⚠️ Esta música já foi pedida por outra pessoa!"
    },
    "English 🇺🇸🇬🇧": {
        "label": "Type the song or artist name:",
        "selecionado": "Selected",
        "confirmar": "Confirm Song ✅",
        "cancelar": "Go Back / Change ❌",
        "posicao": "Your position in queue:",
        "aviso_fila": "⚠️ This song is already in the queue!"
    },
    "Español 🇪🇸": {
        "label": "Escribe el nombre de la canción o artista:",
        "selecionado": "Seleccionado",
        "confirmar": "Confirmar Canción ✅",
        "cancelar": "Volver / Cambiar ❌",
        "posicao": "Tu posición en la lista:",
        "aviso_fila": "⚠️ ¡Esta canción ya está en la lista!"
    },
    "Français 🇫🇷": {
        "label": "Tapez le nom de la chanson ou de l'artiste :",
        "selecionado": "Sélectionné",
        "confirmar": "Confirmer ✅",
        "cancelar": "Retour / Changer ❌",
        "posicao": "Votre position dans la file :",
        "aviso_fila": "⚠️ Cette chanson est déjà dans la file !"
    }
}

# --- INTERFACE ---
st.title("🎤 Karaokê Coopers")

# Seleção por "Bolinhas" (st.radio)
idioma_escolhido = st.radio("Escolha o idioma / Select language:", list(idiomas_dict.keys()), horizontal=True)
textos = idiomas_dict[idioma_escolhido]

if df_catalogo is not None:
    # Estado do App
    if 'musica_escolhida' not in st.session_state:
        st.session_state.musica_escolhida = None

    if st.session_state.musica_escolhida is None:
        # TELA DE BUSCA
        busca = st.text_input(textos["label"]).strip().lower()
        if busca:
            c_mus = col_map.get('musica')
            c_art = col_map.get('artista')
            c_cod = col_map.get('codigo')

            res = df_catalogo[
                df_catalogo[c_mus].astype(str).str.lower().str.contains(busca, na=False) |
                df_catalogo[c_art].astype(str).str.lower().str.contains(busca, na=False)
            ].head(10)

            for i, row in res.iterrows():
                if st.button(f"🎶 {row[c_cod]} - {row[c_mus]} - {row[c_art]}", key=f"btn_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
    else:
        # TELA DE CONFIRMAÇÃO
        m = st.session_state.musica_escolhida
        c_mus = col_map.get('musica')
        st.success(f"{textos['selecionado']}: {m[c_mus]}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(textos["confirmar"], type="primary"):
                # AQUI ENTRA A GRAVAÇÃO NA PLANILHA (VIA SECRETS)
                st.balloons()
                st.info(f"✅ {textos['posicao']} #4") # Exemplo
                if st.button("Fazer novo pedido"):
                    st.session_state.musica_escolhida = None
                    st.rerun()
        with col2:
            if st.button(textos["cancelar"]):
                st.session_state.musica_escolhida = None
                st.rerun()
