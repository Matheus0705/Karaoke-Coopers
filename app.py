import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers Portugal", layout="centered", page_icon="🎤")

# ID da sua planilha extraído do link que você enviou
SHEET_ID = "1g88-tIUw0xLedVBlp2UuZmkFG0nAOW1ef58q5j9Jndk"
# Link para salvar os dados (via formulário ou integração direta)
# Para este nível, usaremos uma técnica de salvamento simplificada
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- FUNÇÕES DE DADOS ---
@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return None

def salvar_na_fila(musica):
    # Aqui simulamos o envio. Para envio real em tempo real sem chaves complexas,
    # o ideal é usar o st.connection("gsheets") do Streamlit Cloud.
    # Por enquanto, vamos focar na interface e lógica de confirmação.
    nova_linha = {
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Codigo": musica['Código'],
        "Musica": musica['Música'],
        "Artista": musica['Artista'],
        "Status": "Aguardando"
    }
    # Mensagem de sucesso para o usuário
    return True

# --- INICIALIZAÇÃO ---
df_catalogo = carregar_catalogo()

if 'pagina' not in st.session_state:
    st.session_state.pagina = 'busca'
if 'selecao' not in st.session_state:
    st.session_state.selecao = None

# --- TRADUÇÕES E BANDEIRAS ---
idiomas = {
    "Português 🇧🇷🇵🇹": {
        "boas_vindas": "Bem-vindo ao Coopers!",
        "busca_label": "Procure por música, artista ou código:",
        "bt_confirmar": "Confirmar e ir para a fila ✅",
        "bt_cancelar": "Trocar música / Cancelar ❌",
        "aviso_repetida": "⚠️ Esta música já está na fila! Deseja pedir novamente?",
        "sucesso": "Pronto! Você está na fila. Posição estimada: ",
        "pesquisar": "Pesquisar..."
    },
    "English 🇺🇸🇬🇧": {
        "boas_vindas": "Welcome to Coopers!",
        "busca_label": "Search by song, artist or code:",
        "bt_confirmar": "Confirm and join queue ✅",
        "bt_cancelar": "Change song / Cancel ❌",
        "aviso_repetida": "⚠️ This song is already in the queue! Want to ask anyway?",
        "sucesso": "Done! You are in the queue. Estimated position: ",
        "pesquisar": "Search..."
    },
    "Español 🇪🇸": {
        "boas_vindas": "¡Bienvenidos a Coopers!",
        "busca_label": "Buscar por música, artista o código:",
        "bt_confirmar": "Confirmar y entrar en lista ✅",
        "bt_cancelar": "Cambiar / Cancelar ❌",
        "aviso_repetida": "⚠️ ¡Esta canción ya está en la lista!",
        "sucesso": "¡Listo! Estás na lista. Posición: ",
        "pesquisar": "Buscar..."
    },
    "Français 🇫🇷": {
        "boas_vindas": "Bienvenue chez Coopers !",
        "busca_label": "Chercher par titre, artiste ou code :",
        "bt_confirmar": "Confirmer ✅",
        "bt_cancelar": "Changer / Annuler ❌",
        "aviso_repetida": "⚠️ Cette chanson est déjà dans la file !",
        "sucesso": "C'est fait ! Vous êtes dans a file. Position : ",
        "pesquisar": "Chercher..."
    }
}

# --- INTERFACE ---
st.title("🎤 Karaokê Coopers")

# Seletor de Idioma
escolha_idioma = st.selectbox("Escolha seu idioma / Select language", list(idiomas.keys()))
dic = idiomas[escolha_idioma]

if st.session_state.pagina == 'busca':
    st.subheader(dic["boas_vindas"])
    termo = st.text_input(dic["busca_label"], placeholder=dic["pesquisar"]).strip().lower()

    if termo:
        res = df_catalogo[
            df_catalogo['Música'].str.lower().str.contains(termo, na=False) | 
            df_catalogo['Artista'].str.lower().str.contains(termo, na=False) |
            df_catalogo['Código'].astype(str).str.contains(termo, na=False)
        ].head(15)

        if not res.empty:
            for i, row in res.iterrows():
                if st.button(f"🎶 {row['Código']} - {row['Música']} - {row['Artista']}", key=f"btn_{i}"):
                    st.session_state.selecao = row
                    st.session_state.pagina = 'confirmacao'
                    st.rerun()
        else:
            st.warning("Nenhuma música encontrada.")

elif st.session_state.pagina == 'confirmacao':
    m = st.session_state.selecao
    st.markdown("### Confirme sua escolha:")
    st.info(f"**Música:** {m['Música']}\n\n**Artista:** {m['Artista']}\n\n**Código:** {m['Código']}")
    
    # Aqui simulamos a checagem de fila (pode ser expandido com st.connection)
    st.warning(dic["aviso_repetida"]) if False else None

    col1, col2 = st.columns(2)
