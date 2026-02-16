import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers Portugal", layout="centered", page_icon="🎤")

# ID da sua planilha
SHEET_ID = "1g88-tIUw0xLedVBlp2UuZmkFG0nAOW1ef58q5j9Jndk"

@st.cache_data
def carregar_catalogo():
    try:
        # Forçamos o pandas a descobrir o separador sozinho (sep=None)
        # E usamos o encoding 'latin1' para suportar acentos de Portugal/Brasil
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        
        # REMOVE ESPAÇOS E DEIXA TUDO SEM ACENTO PARA NÃO DAR KEYERROR
        df.columns = df.columns.str.strip()
        
        # Mapeamento inteligente de colunas (caso o CSV mude os nomes)
        colunas_reais = {}
        for col in df.columns:
            c = col.lower()
            if 'mús' in c or 'mus' in c: colunas_reais['musica'] = col
            if 'art' in c: colunas_reais['artista'] = col
            if 'cód' in c or 'cod' in c: colunas_reais['codigo'] = col
        
        return df, colunas_reais
    except Exception as e:
        st.error(f"Erro crítico ao ler o CSV: {e}")
        return None, None

df_catalogo, col_map = carregar_catalogo()

# --- INTERFACE ---
st.title("🎤 Karaokê Coopers")

# Se o catálogo carregou, seguimos
if df_catalogo is not None:
    # Seleção de Idioma com bandeiras lado a lado
    idiomas_opcoes = {
        "Português 🇧🇷🇵🇹": "musica",
        "English 🇺🇸🇬🇧": "song",
        "Español 🇪🇸": "musica",
        "Français 🇫🇷": "musique"
    }
    idioma_selecionado = st.selectbox("Idioma / Language", list(idiomas_opcoes.keys()))

    # Busca
    termo = st.text_input("Pesquisar música, artista ou código:").strip().lower()

    if termo:
        # Usamos o mapeamento para evitar o KeyError: 'Música'
        c_mus = col_map.get('musica', df_catalogo.columns[1])
        c_art = col_map.get('artista', df_catalogo.columns[2])
        c_cod = col_map.get('codigo', df_catalogo.columns[0])

        mask = (
            df_catalogo[c_mus].astype(str).str.lower().str.contains(termo, na=False) |
            df_catalogo[c_art].astype(str).str.lower().str.contains(termo, na=False) |
            df_catalogo[c_cod].astype(str).str.lower().str.contains(termo, na=False)
        )
        res = df_catalogo[mask].head(15)

        if not res.empty:
            for i, row in res.iterrows():
                if st.button(f"🎶 {row[c_cod]} - {row[c_mus]} - {row[c_art]}", key=f"b_{i}"):
                    st.success(f"Selecionado: {row[c_mus]}")
                    # Aqui no futuro entra o salvamento na planilha
        else:
            st.warning("Não encontrado / Not found")

else:
    st.error("Não consegui ler o arquivo 'karafuncatalog.csv'. Verifique o formato no GitHub.")
