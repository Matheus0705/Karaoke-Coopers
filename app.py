import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Configuração
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÃO PARA LER A FILA ATUAL ---
def ler_fila_atual():
    # Substitua o link abaixo pelo link da sua planilha do Google Sheets
    # Certifique-se de que o link termina com /export?format=csv
    sheet_url = "SUA_PLANILHA_LINK_AQUI/export?format=csv"
    try:
        df_fila = pd.read_csv(sheet_url)
        return len(df_fila) # Retorna quantas pessoas já estão na fila
    except:
        return 0

@st.cache_data
def carregar_catalogo():
    df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
    df.columns = [str(c).strip() for c in df.columns]
    return df

df_catalogo = carregar_catalogo()

# Resetar estado
def resetar():
    st.session_state.musica_escolhida = None
    st.rerun()

# Traduções
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {"label": "Pesquisar...", "sel": "Selecionado", "conf": "Confirmar ✅", "canc": "Voltar ❌", "sucesso": "Pedido Enviado!", "posicao": "Estás na posição nº"},
    "English 🇺🇸🇬🇧": {"label": "Search...", "sel": "Selected", "conf": "Confirm ✅", "canc": "Back ❌", "sucesso": "Sent!", "posicao": "You are at position #"}
}

st.title("🎤 Karaokê Coopers")
idioma = st.sidebar.radio("Idioma", list(idiomas_dict.keys())) # Coloquei no lado para limpar o meio
t = idiomas_dict[idioma]

# Mostrar fila atual (para a pessoa acompanhar)
fila_agora = ler_fila_atual()
st.info(f"📢 {t['posicao']} {fila_agora + 1} da fila!")

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
    st.warning(f"{t['sel']}: {m.iloc[1]}")
    
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
            st.success(f"{t['sucesso']} {t['posicao']} {fila_agora + 1}")
            st.button("Fazer novo pedido 🎤", on_click=resetar) # Este botão agora funciona!
            
    with col2:
        if st.button(t["canc"], on_click=resetar):
            pass
