import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÃO PARA LER A FILA DO GOOGLE SHEETS ---
def carregar_fila():
    # Link formatado para exportar os dados reais da planilha em CSV
    url_dados = "https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv"
    try:
        # Lemos a planilha ignorando o cache para ter dados frescos
        df_fila = pd.read_csv(url_dados)
        df_fila.columns = [c.strip() for c in df_fila.columns]
        return df_fila
    except:
        return pd.DataFrame()

# --- CARREGAR CATÁLOGO DE MÚSICAS ---
@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df_catalogo = carregar_catalogo()

# Função para limpar a seleção e voltar à busca
def voltar_inicio():
    st.session_state.musica_escolhida = None
    st.rerun()

# --- DICIONÁRIO DE TRADUÇÃO COMPLETO ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...",
        "fila_tit": "🎤 Fila de Espera Atual",
        "vazio": "Fila vazia! Peça a primeira música!",
        "sel": "Selecionado:",
        "pos": "Sua posição na fila será:",
        "conf": "Confirmar ✅",
        "canc": "Voltar ❌",
        "sucesso": "Pedido enviado com sucesso!",
        "outro": "Pedir outra música 🎤",
        "col_hora": "Hora",
        "col_musica": "Música"
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...",
        "fila_tit": "🎤 Current Queue",
        "vazio": "Empty queue! Be the first one!",
        "sel": "Selected:",
        "pos": "Your position will be:",
        "conf": "Confirm ✅",
        "canc": "Back ❌",
        "sucesso": "Request sent successfully!",
        "outro": "Request another song 🎤",
        "col_hora": "Time",
        "col_musica": "Song"
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
        "outro": "Pedir otra canción 🎤",
        "col_hora": "Hora",
        "col_musica": "Canción"
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
        "outro": "Demander une autre chanson 🎤",
        "col_hora": "Heure",
        "col_musica": "Chanson"
    }
}

st.title("🎤 Karaokê Coopers")

# 1. Seleção de Idioma no topo da interface principal
escolha = st.radio("Escolha o idioma / Select language:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

st.divider()

# 2. Exibição da Fila de Espera (Tabela ao Vivo)
st.subheader(t["fila_tit"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pegamos a coluna da Hora (índice 1) e da Música (índice 3)
        fila_visual = df_atual.iloc[:, [1, 3]].copy()
        fila_visual.columns = [t["col_hora"], t["col_musica"]]
        st.table(fila_visual)
    except:
        st.info("Atualizando fila...")
else:
    st.write(t["vazio"])

st.divider()

# 3. Lógica de Pedido de Música
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
    posicao_prevista = len(df_atual) + 1
    
    st.success(f"{t['sel']} {m.iloc[1]} - {m.iloc[2]}")
    st.info(f"📢 {t['pos']} {posicao_prevista}º")

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
            try:
                requests.post(url_form, data=dados)
                st.balloons()
                st.success(t["sucesso"])
                # Botão de reset com tradução
                st.button(t["outro"], on_click=voltar_inicio)
            except:
                st.error("Erro de conexão. Tente novamente.")
                
    with col2:
        if st.button(t["canc"], on_click=voltar_inicio):
            pass
