import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- 1. FUNÇÃO DE LEITURA DA FILA (Google Sheets) ---
def carregar_fila():
    # O timestamp força o Google a entregar dados novos (evita cache antigo)
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 2. CARREGAR CATÁLOGO DE MÚSICAS ---
@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df_catalogo = carregar_catalogo()

# --- 3. FUNÇÃO PARA VOLTAR AO INÍCIO ---
def voltar_inicio():
    st.session_state.musica_escolhida = None

# --- 4. DICIONÁRIO DE TRADUÇÃO COMPLETO ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...",
        "fila": "🎤 Fila de Espera",
        "vazio": "Fila vazia! Peça a primeira!",
        "sel": "Selecionado:",
        "pos": "Sua posição:",
        "conf": "Confirmar ✅",
        "sucesso": "Pedido enviado com sucesso!",
        "outro": "Pedir outra música 🎤",
        "voltar": "Voltar ❌",
        "erro": "Desculpe, no momento não temos essa música. Cheque com o DJ, pois algumas músicas não irão aparecer na lista oficial devido a direitos autorais, obrigado!"
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...",
        "fila": "🎤 Current Queue",
        "vazio": "Empty queue! Be the first!",
        "sel": "Selected:",
        "pos": "Your position:",
        "conf": "Confirm ✅",
        "sucesso": "Request sent successfully!",
        "outro": "Request another song 🎤",
        "voltar": "Back ❌",
        "erro": "Sorry, we don't have this song at the moment. Please check with the DJ, as some songs may not appear on the official list due to copyright reasons, thank you!"
    },
    "Español 🇪🇦": {
        "busca": "Buscar música o artista...",
        "fila": "🎤 Lista de espera",
        "vazio": "¡Lista vacía!",
        "sel": "Seleccionado:",
        "pos": "Tu posición:",
        "conf": "Confirmar ✅",
        "sucesso": "¡Pedido enviado con éxito!",
        "outro": "Pedir otra canción 🎤",
        "voltar": "Volver ❌",
        "erro": "Lo sentimos, no tenemos esta canción en este momento. Consulta con el DJ, ya que algunas canciones no aparecerán en la lista oficial debido a derechos de autor, ¡gracias!"
    },
    "Français 🇫🇷": {
        "busca": "Chercher une chanson...",
        "fila": "🎤 File d'attente",
        "vazio": "File vide !",
        "sel": "Sélectionné :",
        "pos": "Votre position :",
        "conf": "Confirmer ✅",
        "sucesso": "Demande envoyée avec succès !",
        "outro": "Demander une autre chanson 🎤",
        "voltar": "Retour ❌",
        "erro": "Désolé, nous n'avons pas cette chanson pour le moment. Vérifiez auprès du DJ, car certaines chansons n'apparaîtront pas sur la liste officielle en raison de droits d'auteur, merci !"
    }
}

# --- INTERFACE ---
st.title("🎤 Karaokê Coopers")

# Seletor de Idiomas na tela principal
escolha = st.radio("Idioma / Language:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

st.divider()

# --- FILA EM TEMPO REAL ---
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pega as colunas de Música (3) e Artista (4) para a tabela
        fila_visual = df_atual.iloc[:, [3, 4]].copy() 
        fila_visual.columns = ["Música", "Artista"]
        fila_visual.index = [f"{i+1}º" for i in range(len(fila_visual))]
        st.table(fila_visual)
    except:
        st.write("Atualizando lista...")
else:
    st.write(t["vazio"])

st.divider()

# --- LÓGICA DE PEDIDO ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None

if st.session_state.musica_escolhida is None:
    busca = st.text_input(t["busca"]).strip().lower()
    if busca:
        # Filtro de busca no catálogo CSV
        res = df_catalogo[df_catalogo.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                          df_catalogo.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(10)
        
        if not res.empty:
            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"b_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
        else:
            # Mensagem de erro caso não encontre no CSV
            st.error(t["erro"])
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
            # Envia para o Google Forms
            requests.post(url_form, data=dados)
            st.balloons()
            st.toast(t["sucesso"])
            
            # Limpa escolha e volta para a tela inicial para mostrar a música na fila
            st.session_state.musica_escolhida = None
            time.sleep(1.5) # Pausa curta para o Google processar a entrada
            st.rerun()
            
    with col2:
        st.button(t["voltar"], on_click=voltar_inicio)
