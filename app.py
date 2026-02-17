import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÕES CORE ---
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- INTERFACE E LOGO ---
st.markdown("<h1 style='text-align: center;'>🎤 Karaokê Coopers</h1>", unsafe_content_html=True)

idiomas = {
    "Português BR": {
        "busca": "Pesquisar música ou artista...", 
        "fila": "Fila de Espera", 
        "vazio": "Aguardando o primeiro pedido...", 
        "sucesso": "SUA SENHA:", 
        "posicao_txt": "Sua posição na fila será:",
        "erro_dj": "Desculpe, no momento não temos essa música. Cheque com o DJ, pois algumas músicas não irão aparecer na lista oficial devido a direitos autorais, obrigado!"
    },
    "English us": {
        "busca": "Search song or artist...", 
        "fila": "Current Queue", 
        "vazio": "Waiting for requests...", 
        "sucesso": "YOUR TOKEN:", 
        "posicao_txt": "Your position will be:",
        "erro_dj": "Sorry, we don't have this song. Check with the DJ, as some songs may not appear due to copyright, thank you!"
    },
    "Español EA": {
        "busca": "Buscar música...", 
        "fila": "Lista de espera", 
        "vazio": "¡Lista vacía!", 
        "sucesso": "TU CÓDIGO:", 
        "posicao_txt": "Tu posición será:",
        "erro_dj": "Lo sentimos, no tenemos esta canción. Consulta con el DJ, ¡gracias!"
    },
    "Français FR": {
        "busca": "Chercher...", 
        "fila": "File d'attente", 
        "vazio": "File vide !", 
        "sucesso": "VOTRE CODE:", 
        "posicao_txt": "Votre position :",
        "erro_dj": "Désolé, nous n'avons pas cette chanson. Vérifiez auprès du DJ, merci !"
    }
}

escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

# --- CAIXA DE SENHA FIXA NO TOPO ---
if "minha_senha" in st.session_state:
    st.info(f"🔑 {t['sucesso']} {st.session_state.minha_senha}")

st.divider()

# --- FILA DE ESPERA ---
st.subheader(f"📊 {t['fila']}")
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pega Senha (5), Música (3) e Artista (4) da sua planilha
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy() 
        fila_visual.columns = ["Senha", "Música", "Artista"]
        fila_visual.index = [f"{i+1}º" for i in range(len(fila_visual))]
        st.table(fila_visual)
    except:
        st.write(t["vazio"])
else:
    st.write(t["vazio"])

st.divider()

# --- LÓGICA DE PEDIDO ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0

if st.session_state.musica_escolhida is None:
    # O reset_busca limpa o campo de texto automaticamente após o pedido
    busca = st.text_input(t["busca"], key=f"input_{st.session_state.reset_busca}").strip().lower()
    if busca:
        df_cat = carregar_catalogo()
        res = df_cat[df_cat.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                     df_cat.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(10)
        
        if not res.empty:
            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"btn_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
        else:
            st.error(t["erro_dj"])
else:
    m = st.session_state.musica_escolhida
    # Estética das caixas coloridas restaurada
    st.markdown(f"<div style='background-color: #28a745; padding: 15px; border-radius: 10px; color: white; font-weight: bold;'>🎵 Selecionada: {m.iloc[1]} - {m.iloc[2]}</div>", unsafe_content_html=True)
    st.markdown(f"<div style='background-color: #007bff; padding: 10px; border-radius: 10px; color: white; margin-top: 8px;'>📢 {t['posicao_txt']} {len(df_atual)+1}º</div>", unsafe_content_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CONFIRMAR ✅", type="primary", use_container_width=True):
            nova_senha = gerar_senha()
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            # --- LEMBRETE: Altere 'entry.XXXXX' para o seu ID real da Senha ---
            id_da_senha = "entry.18065" 
            
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                id_da_senha: nova_senha
            }
            
            requests.post(url_form, data=dados)
            st.session_state.minha_senha = nova_senha
            st.balloons() # Balões ativados!
            
            # Reseta estado e limpa a barra de busca
            st.session_state.musica_escolhida = None
            st.session_state.reset_busca += 1
            time.sleep(2)
            st.rerun()

    with col2:
        if st.button("CANCELAR ❌", use_container_width=True):
            st.session_state.musica_escolhida = None
            st.rerun()
