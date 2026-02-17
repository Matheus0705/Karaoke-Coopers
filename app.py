import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- 1. LOGO NO TOPO (Nome corrigido) ---
try:
    st.image("9d8daa_198ec12882054dceb6d49d760eba30f0~mv2.jpg", width=250)
except:
    st.markdown("### 🎤 KARAOKÊ COOPER'S")

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
        return None

# --- GESTÃO DE ESTADO (MEMÓRIA) ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = []
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0

# --- DICIONÁRIO DE TRADUÇÃO COMPLETO ---
idiomas = {
    "Português 🇧🇷": {
        "titulo": "Acompanhe sua vez aqui!",
        "col_pos": "Posição", "col_mus": "Música", "col_art": "Artista", "col_sen": "Sua Senha",
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", "vazio": "Fila vazia! Peça a primeira!",
        "conf": "Confirmar ✅", "canc": "Cancelar ❌",
        "erro": "Desculpe, no momento não temos essa música. Cheque com o DJ, pois algumas músicas não aparecerão devido a direitos autorais, obrigado!"
    },
    "English 🇺🇸": {
        "titulo": "Track your turn here!",
        "col_pos": "Pos.", "col_mus": "Song", "col_art": "Artist", "col_sen": "Token",
        "busca": "SEARCH YOUR SONG OR ARTIST", "vazio": "Empty queue!",
        "conf": "Confirm ✅", "canc": "Cancel ❌",
        "erro": "Sorry, song not found. Check with the DJ for copyright reasons!"
    },
    "Español 🇪🇦": {
        "titulo": "¡Sigue tu turno aquí!",
        "col_pos": "Pos.", "col_mus": "Canción", "col_art": "Artista", "col_sen": "Código",
        "busca": "BUSCA TU MÚSICA O ARTISTA", "vazio": "¡Lista vacía!",
        "conf": "Confirmar ✅", "canc": "Cancelar ❌",
        "erro": "Lo sentimos, canción no disponible. ¡Consulta al DJ!"
    },
    "Français 🇫🇷": {
        "titulo": "Suivez votre tour !",
        "col_pos": "Pos.", "col_mus": "Chanson", "col_art": "Artiste", "col_sen": "Code",
        "busca": "CHERCHEZ VOTRE CHANSON", "vazio": "File vide !",
        "conf": "Confirmer ✅", "canc": "Annuler ❌",
        "erro": "Désolé, nous n'avons pas cette chanson pour le moment."
    }
}

# Seletor de Idiomas
escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]
st.markdown(f"### {t['titulo']}")

# --- FILA EM FORMATO DE PLANILHA ---
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Colunas: 3=Música, 4=Artista, 5=Senha
        fila_visual = df_atual.iloc[:, [3, 4, 5]].copy()
        fila_visual.columns = [t["col_mus"], t["col_art"], "senha_hidden"]
        
        # Só mostra a senha se ela foi gerada por este usuário
        def mostrar_minha_senha(row):
            val = str(row["senha_hidden"]).strip()
            if val in st.session_state.minhas_senhas:
                return f"🔑 {val}"
            return ""

        fila_visual[t["col_sen"]] = fila_visual.apply(mostrar_minha_senha, axis=1)
        
        # Coluna de Posição 1º, 2º...
        fila_visual.insert(0, t["col_pos"], [f"{i+1}º" for i in range(len(fila_visual))])
        
        # Exibe como tabela limpa
        st.table(fila_visual.drop(columns=["senha_hidden"]))
    except:
        st.write(t["vazio"])
else:
    st.write(t["vazio"])

st.divider()

# --- BUSCA E PEDIDO ---
if st.session_state.musica_escolhida is None:
    busca = st.text_input(f"🔍 {t['busca']}", key=f"inp_{st.session_state.reset_busca}").strip().lower()
    
    if busca:
        df_cat = carregar_catalogo()
        if df_cat is not None:
            res = df_cat[df_cat.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                         df_cat.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(8)
            
            if not res.empty:
                for i, row in res.iterrows():
                    if st.button(f"🎵 {row.iloc[1]} - {row.iloc[2]}", key=f"s_{i}"):
                        st.session_state.musica_escolhida = row
                        st.rerun()
            else:
                st.error(t["erro"])
else:
    m = st.session_state.musica_escolhida
    st.success(f"📌 {m.iloc[1]} - {m.iloc[2]}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t["conf"], type="primary"):
            nova_senha = gerar_senha()
            
            # ID DA SENHA QUE VOCÊ ENVIOU
            id_senha = "694761068" 
            
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                f"entry.{id_senha}": nova_senha
            }
            
            requests.post(url_form, data=dados)
            st.session_state.minhas_senhas.append(nova_senha)
            st.balloons()
            
            st.session_state.musica_escolhida = None
            st.session_state.reset_busca += 1
            time.sleep(2)
            st.rerun()
    with c2:
        if st.button(t["canc"]):
            st.session_state.musica_escolhida = None
            st.rerun()
