import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página - Wide para caber a tabela desenhada
st.set_page_config(page_title="Karaokê Coopers", layout="wide", page_icon="🎤")

# --- 1. CABEÇALHO (LOGO AO LADO DO TÍTULO) ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        # Nome do arquivo conforme seu GitHub
        st.image("9d8daa_198ec12882054dceb6d49d760eba30f0~mv2.jpg", width=150)
    except:
        st.write("🎤")
with col_titulo:
    # Estilizando o título para ficar alinhado verticalmente com a logo
    st.markdown("<h1 style='padding-top: 20px;'>KARAOKÊ COOPER'S</h1>", unsafe_allow_html=True)

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

# --- GESTÃO DE ESTADO (MEMÓRIA DO NAVEGADOR) ---
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
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", "vazio": "Aguardando o primeiro pedido da noite...",
        "conf": "Confirmar ✅", "canc": "Cancelar ❌",
        "erro": "Desculpe, não encontramos. Cheque com o DJ sobre direitos autorais!"
    },
    "English 🇺🇸": {
        "titulo": "Track your turn here!",
        "col_pos": "Pos.", "col_mus": "Song", "col_art": "Artist", "col_sen": "Your Token",
        "busca": "SEARCH YOUR SONG OR ARTIST", "vazio": "Waiting for requests...",
        "conf": "Confirm ✅", "canc": "Cancel ❌",
        "erro": "Sorry, not found. Check with the DJ!"
    },
    "Español 🇪🇦": {
        "titulo": "¡Sigue tu turno aquí!",
        "col_pos": "Pos.", "col_mus": "Canción", "col_art": "Artista", "col_sen": "Tu Código",
        "busca": "BUSCA TU MÚSICA O ARTISTA", "vazio": "¡Lista vacía!",
        "conf": "Confirmar ✅", "canc": "Cancelar ❌",
        "erro": "Lo sentimos, no disponível. ¡Consulta al DJ!"
    },
    "Français 🇫🇷": {
        "titulo": "Suivez votre tour !",
        "col_pos": "Pos.", "col_mus": "Chanson", "col_art": "Artiste", "col_sen": "Code",
        "busca": "CHERCHER VOTRE CHANSON", "vazio": "File vide !",
        "conf": "Confirmer ✅", "canc": "Annuler ❌",
        "erro": "Désolé, chanson não disponível."
    }
}

# Seletor de Idioma
escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]
st.markdown(f"### {t['titulo']}")

# --- 2. FILA EM FORMATO DE TABELA (ESTILO PLANILHA) ---
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Puxa colunas 3 (Música), 4 (Artista) e 5 (Senha)
        fila_visual = df_atual.iloc[:, [3, 4, 5]].copy()
        fila_visual.columns = [t["col_mus"], t["col_art"], "senha_raw"]
        
        # Lógica: Se a senha daquela linha está na lista do celular do usuário, mostra.
        def filtrar_senha(row):
            s = str(row["senha_raw"]).strip()
            if s in st.session_state.minhas_senhas:
                return f"🔑 {s}"
            return ""

        fila_visual[t["col_sen"]] = fila_visual.apply(filtrar_senha, axis=1)
        
        # Adiciona coluna de Posição
        fila_visual.insert(0, t["col_pos"], [f"{i+1}º" for i in range(len(fila_visual))])
        
        # Remove a coluna bruta para não vazar senhas alheias
        st.table(fila_visual.drop(columns=["senha_raw"]))
    except:
        st.info(t["vazio"])
else:
    st.info(t["vazio"])

st.divider()

# --- 3. ÁREA DE PESQUISA E PEDIDO ---
if st.session_state.musica_escolhida is None:
    # O key dinâmico garante que o campo limpe após o rerun
    busca = st.text_input(f"🔍 {t['busca']}", key=f"input_{st.session_state.reset_busca}").strip().lower()
    
    if busca:
        df_cat = carregar_catalogo()
        if df_cat is not None:
            res = df_cat[df_cat.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                         df_cat.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(8)
            
            if not res.empty:
                for i, row in res.iterrows():
                    if st.button(f"🎵 {row.iloc[1]} - {row.iloc[2]}", key=f"btn_{i}"):
                        st.session_state.musica_escolhida = row
                        st.rerun()
            else:
                st.error(t["erro"])
else:
    # Tela de Confirmação
    m = st.session_state.musica_escolhida
    st.success(f"📌 Selecionada: {m.iloc[1]} - {m.iloc[2]}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t["conf"], type="primary"):
            nova_senha = gerar_senha()
            id_senha_form = "694761068" # ID que você forneceu
            
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                f"entry.{id_senha_form}": nova_senha
            }
            
            # Envio
            requests.post(url_form, data=dados)
            
            # Salva no navegador do cliente
            st.session_state.minhas_senhas.append(nova_senha)
            st.balloons()
            
            # Limpa estado para o próximo
            st.session_state.musica_escolhida = None
            st.session_state.reset_busca += 1
            time.sleep(2)
            st.rerun()
    with c2:
        if st.button(t["canc"]):
            st.session_state.musica_escolhida = None
            st.rerun()
