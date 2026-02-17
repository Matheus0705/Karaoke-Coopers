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

# --- FUNÇÃO PARA LER A FILA (Substitua a sua por esta) ---
def carregar_fila():
    # Este link já está formatado para exportar os dados como CSV
    url_dados = "https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv"
    try:
        # Lemos a planilha. O 'storage_options' ajuda a evitar o cache antigo
        df_fila = pd.read_csv(url_dados)
        # Remove espaços em branco dos nomes das colunas
        df_fila.columns = [c.strip() for c in df_fila.columns]
        return df_fila
    except Exception as e:
        # Se der erro, ele mostra no app para sabermos o que é
        # st.error(f"Erro ao ler planilha: {e}") 
        return pd.DataFrame()
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
# --- EXIBIÇÃO DA FILA (Substitua o bloco correspondente por este) ---
st.subheader(t["fila_tit"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Nas planilhas do Forms geralmente:
        # Coluna 0: Carimbo de data/hora
        # Coluna 1: Pergunta 1 (Data/Hora no seu caso)
        # Coluna 3: Pergunta 3 (Nome da Música)
        
        # Vamos tentar pegar as colunas pelo nome ou pela posição
        # Vou usar a posição para garantir (1 e 3)
        fila_visual = df_atual.iloc[:, [1, 3]].copy()
        fila_visual.columns = ["Hora", "Música"]
        
        # Mostra a tabela para o cliente
        st.table(fila_visual)
    except Exception as e:
        st.write("Aguardando próximos cantores... 🎤")
else:
    st.write(t["vazio"])
