import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÃO PARA GERAR SENHA ALEATÓRIA (4 dígitos) ---
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# --- FUNÇÃO DE LEITURA DA FILA ---
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
        return None

df_catalogo = carregar_catalogo()

def voltar_inicio():
    st.session_state.musica_escolhida = None

# --- DICIONÁRIO DE TRADUÇÃO ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...", "fila": "🎤 Fila de Espera", "vazio": "Fila vazia!", 
        "sel": "Selecionado:", "pos": "Sua posição:", "conf": "Confirmar ✅", "voltar": "Voltar ❌",
        "sucesso": "Pedido enviado!", "senha_txt": "SUA SENHA:", "aviso_senha": "Mostre esta senha ao DJ quando for chamado!",
        "erro": "Desculpe, no momento não temos essa música. Cheque com o DJ, pois algumas músicas não irão aparecer na lista oficial devido a direitos autorais, obrigado!"
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...", "fila": "🎤 Current Queue", "vazio": "Empty queue!", 
        "sel": "Selected:", "pos": "Your position:", "conf": "Confirm ✅", "voltar": "Back ❌",
        "sucesso": "Request sent!", "senha_txt": "YOUR TOKEN:", "aviso_senha": "Show this token to the DJ when called!",
        "erro": "Sorry, we don't have this song at the moment. Please check with the DJ, as some songs may not appear on the official list due to copyright reasons, thank you!"
    }
}

st.title("🎤 Karaokê Coopers")
escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

st.divider()

# --- EXIBIÇÃO DA FILA COM SENHA ---
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Posição das colunas na planilha Form_Responses2:
        # [0]=Data/Hora Google, [1]=Sua Hora, [2]=Código, [3]=Música, [4]=Artista, [5]=Senha
        # Vamos mostrar Senha (5), Música (3) e Artista (4)
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy() 
        fila_visual.columns = ["Senha", "Música", "Artista"]
        st.table(fila_visual)
    except:
        st.write("Atualizando lista de cantores...")
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
        if not res.empty:
            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"b_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
        else:
            st.error(t["erro"])
else:
    m = st.session_state.musica_escolhida
    posicao = len(df_atual) + 1
    
    st.success(f"{t['sel']} {m.iloc[1]}")
    st.info(f"📢 {t['pos']} {posicao}º")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
            # 1. Gera a senha
            token = gerar_senha()
            
            # 2. Envia para o formulário
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                "entry.480072027": token  # ID DA SENHA QUE DESCOBRI PARA TI
            }
            
            requests.post(url_form, data=dados)
            
            # 3. Mostra a senha na tela
            st.balloons()
            st.success(t["sucesso"])
            st.code(f"{t['senha_txt']} {token}", language="text")
            st.warning(t["aviso_senha"])
            
            # 4. Espera e reseta
            time.sleep(6) 
            st.session_state.musica_escolhida = None
            st.rerun()
            
    with col2:
        st.button(t["voltar"], on_click=voltar_inicio)
