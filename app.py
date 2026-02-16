import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers Portugal", layout="centered", page_icon="🎤")

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return None

df_catalogo = carregar_catalogo()

# Dicionário de Tradução
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {"label": "Pesquisar...", "sel": "Selecionado", "conf": "Confirmar ✅", "canc": "Voltar ❌", "pos": "Fila:", "sucesso": "Enviado!"},
    "English 🇺🇸🇬🇧": {"label": "Search...", "sel": "Selected", "conf": "Confirm ✅", "canc": "Back ❌", "pos": "Queue:", "sucesso": "Sent!"},
    "Español 🇪🇸": {"label": "Buscar...", "sel": "Seleccionado", "conf": "Confirmar ✅", "canc": "Volver ❌", "pos": "Lista:", "sucesso": "¡Enviado!"},
    "Français 🇫🇷": {"label": "Chercher...", "sel": "Sélectionné", "conf": "Confirmer ✅", "canc": "Retour ❌", "pos": "File:", "sucesso": "Envoyé!"}
}

# Interface
st.title("🎤 Karaokê Coopers")

# Menu Lateral para Admin
menu = st.sidebar.selectbox("Menu", ["Catálogo", "Administrador"])

if menu == "Catálogo":
    idioma = st.radio("Idioma", list(idiomas_dict.keys()), horizontal=True)
    t = idiomas_dict[idioma]

    if 'musica_escolhida' not in st.session_state:
        st.session_state.musica_escolhida = None

    if st.session_state.musica_escolhida is None:
        busca = st.text_input(t["label"]).strip().lower()
        if busca:
            res = df_catalogo[df_catalogo.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                              df_catalogo.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(10)
            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[0]} - {row.iloc[1]} - {row.iloc[2]}", key=f"b_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
    else:
        m = st.session_state.musica_escolhida
        st.success(f"{t['sel']}: {m.iloc[1]}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t["conf"], type="primary"):
                try:
                    # Tenta ler a fila (sem cache para pegar o dado real)
                    fila = conn.read(ttl=0)
                    nova = pd.DataFrame([{
                        "Data": datetime.now().strftime("%H:%M"),
                        "Codigo": str(m.iloc[0]),
                        "Musica": str(m.iloc[1]),
                        "Artista": str(m.iloc[2]),
                        "Status": "Aguardando"
                    }])
                    fila_atualizada = pd.concat([fila, nova], ignore_index=True)
                    conn.update(data=fila_atualizada)
                    st.balloons()
                    st.success(f"{t['sucesso']} {t['pos']} #{len(fila_atualizada)}")
                except Exception as e:
                    st.error("Erro de conexão. Verifique se a planilha está como EDITOR.")
                    st.info(f"Detalhe: {e}")
        with col2:
            if st.button(t["canc"]):
                st.session_state.musica_escolhida = None
                st.rerun()

elif menu == "Administrador":
    senha = st.text_input("Senha", type="password")
    if senha == "coopers123":
        st.subheader("Fila de Espera")
        df_fila = conn.read(ttl=0)
        st.dataframe(df_fila)
        if st.button("Limpar Fila"):
            conn.update(data=pd.DataFrame(columns=["Data", "Codigo", "Musica", "Artista", "Status"]))
            st.rerun()
