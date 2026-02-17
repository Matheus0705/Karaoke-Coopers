import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- FUNÇÃO PARA GERAR SENHA ALEATÓRIA ---
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
    df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
    df.columns = [str(c).strip() for c in df.columns]
    return df

df_catalogo = carregar_catalogo()

def voltar_inicio():
    st.session_state.musica_escolhida = None

# --- TRADUÇÕES ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música...", "fila": "🎤 Fila", "vazio": "Fila vazia!", 
        "sel": "Selecionado:", "pos": "Sua posição:", "conf": "Confirmar ✅", 
        "sucesso": "Pedido enviado!", "senha_txt": "SUA SENHA:", "voltar": "Voltar ❌",
        "erro": "Desculpe, no momento não temos essa música. Cheque com o DJ!"
    },
    "English 🇺🇸": {
        "busca": "Search song...", "fila": "🎤 Queue", "vazio": "Empty!", 
        "sel": "Selected:", "pos": "Your position:", "conf": "Confirm ✅", 
        "sucesso": "Sent!", "senha_txt": "YOUR TOKEN:", "voltar": "Back ❌",
        "erro": "Sorry, song not found. Check with the DJ!"
    }
}

st.title("🎤 Karaokê Coopers")
escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

st.divider()

# --- FILA COM SENHA ---
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pega a coluna da Música (3), Artista (4) e SENHA (5 - assumindo que é a próxima)
        # Se a senha não aparecer, mude o [3, 4, 5] para os números certos da sua planilha
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy() 
        fila_visual.columns = ["Senha", "Música", "Artista"]
        st.table(fila_visual)
    except:
        st.write("Atualizando lista...")
else:
    st.write(t["vazio"])

st.divider()

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
            # GERA A SENHA NA HORA
            token = gerar_senha()
            
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            # ADICIONE O ID DA PERGUNTA "SENHA" ABAIXO
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                "entry.000000000": token # <--- SUBSTITUA O 000000 PELO ID DA SENHA
            }
            
            requests.post(url_form, data=dados)
            
            # MOSTRA A SENHA GRANDE PARA O CLIENTE
            st.balloons()
            st.markdown(f"### {t['sucesso']}")
            st.code(f"{t['senha_txt']} {token}", language="text")
            st.warning("Tire um print ou anote sua senha!")
            
            time.sleep(5) # Dá tempo de ver a senha antes de resetar
            st.session_state.musica_escolhida = None
            st.rerun()
            
    with col2:
        st.button(t["voltar"], on_click=voltar_inicio)
