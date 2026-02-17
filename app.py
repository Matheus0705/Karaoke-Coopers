import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÃO PARA LER A FILA DO GOOGLE SHEETS ---
def carregar_fila():
    # SUBSTITUA PELO SEU LINK DA PLANILHA (com o final /gviz/tq?tqx=out:csv)
    url_dados = "LINK_DA_SUA_PLANILHA"
    try:
        # Lemos a planilha em tempo real
        df_fila = pd.read_csv(url_dados)
        return df_fila
    except:
        return pd.DataFrame()

@st.cache_data
def carregar_catalogo():
    df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
    df.columns = [str(c).strip() for c in df.columns]
    return df

df_catalogo = carregar_catalogo()

def voltar_inicio():
    st.session_state.musica_escolhida = None
    st.rerun()

# Traduções
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {"label": "Pesquisar música...", "conf": "Confirmar ✅", "canc": "Voltar ❌", "fila_titulo": "🎤 Fila de Espera Atual", "vazio": "Fila vazia! Peça a primeira!"},
    "English 🇺🇸🇬🇧": {"label": "Search song...", "conf": "Confirm ✅", "canc": "Back ❌", "fila_titulo": "🎤 Current Queue", "vazio": "Empty queue! Be the first!"}
}

st.title("🎤 Karaokê Coopers")
idioma = st.sidebar.radio("Idioma", list(idiomas_dict.keys()))
t = idiomas_dict[idioma]

# --- BLOCO DA FILA AO VIVO ---
st.subheader(t["fila_titulo"])
df_atual = carregar_fila()

if not df_atual.empty:
    # Mostramos apenas as colunas de Música e Artista (ajuste os índices se necessário)
    # Supondo que Música está na coluna 2 e Artista na coluna 3 da sua planilha
    fila_visual = df_atual.iloc[:, [2, 3]].head(5) 
    fila_visual.columns = ["Música", "Artista"]
    st.table(fila_visual) # Mostra uma tabelinha limpa com as próximas 5
else:
    st.write(t["vazio"])

st.divider()

# --- LÓGICA DE PEDIDO ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None

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
    posicao_prevista = len(df_atual) + 1
    
    st.warning(f"Selecionada: {m.iloc[1]}")
    st.info(f"Sua posição na fila será: {posicao_prevista}º")

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
            st.success("Pedido enviado! Fique de olho na tabela acima.")
            st.button("Fazer outro pedido 🎤", on_click=voltar_inicio)
    with col2:
        if st.button(t["canc"], on_click=voltar_inicio):
            pass
