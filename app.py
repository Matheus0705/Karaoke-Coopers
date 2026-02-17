import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="wide", page_icon="🎤")

# --- ESTILIZAÇÃO CSS (Para parecer com o seu desenho) ---
st.markdown("""
    <style>
    .main { background-color: #2b3e36; }
    .stTable { border: 2px solid #a066ff; border-radius: 10px; }
    th { background-color: #3f51b5 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

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

# --- GESTÃO DE ESTADO ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = [] # Lista para guardar várias senhas se ele pedir mais de uma
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0

# --- DICIONÁRIO DE TRADUÇÃO COMPLETO ---
idiomas = {
    "Português 🇧🇷": {
        "titulo": "Acompanhe sua vez aqui!",
        "col_pos": "Posição", "col_mus": "Música", "col_art": "Cantor/Artista", "col_sen": "Sua Senha",
        "busca": "PESQUISE AQUI SUA MÚSICA/ ARTISTA", "vazio": "Fila vazia! Peça a primeira!",
        "conf": "Confirmar ✅", "canc": "Cancelar ❌",
        "erro": "Desculpe, no momento não temos essa música. Cheque com o DJ, pois algumas músicas não aparecerão devido a direitos autorais, obrigado!"
    },
    "English 🇺🇸": {
        "titulo": "Track your turn here!",
        "col_pos": "Position", "col_mus": "Song", "col_art": "Artist", "col_sen": "Your Token",
        "busca": "SEARCH YOUR SONG / ARTIST HERE", "vazio": "Empty queue!",
        "conf": "Confirm ✅", "canc": "Cancel ❌",
        "erro": "Sorry, song not available. Check with the DJ for copyright reasons!"
    },
    "Español 🇪🇦": {
        "titulo": "¡Sigue tu turno aquí!",
        "col_pos": "Posición", "col_mus": "Canción", "col_art": "Artista", "col_sen": "Tu Código",
        "busca": "BUSCA AQUÍ TU MÚSICA / ARTISTA", "vazio": "¡Lista vacía!",
        "conf": "Confirmar ✅", "canc": "Cancelar ❌",
        "erro": "Lo sentimos, canción no disponível. ¡Consulta al DJ!"
    },
    "Français 🇫🇷": {
        "titulo": "Suivez votre tour ici !",
        "col_pos": "Position", "col_mus": "Chanson", "col_art": "Artiste", "col_sen": "Votre Code",
        "busca": "CHERCHEZ VOTRE CHANSON / ARTISTE ICI", "vazio": "File vide !",
        "conf": "Confirmer ✅", "canc": "Annuler ❌",
        "erro": "Désolé, chanson non disponible. Vérifiez auprès du DJ !"
    }
}

# --- INTERFACE ---
st.write(f"# KARAOKÊ COOPER'S 🎤")
escolha = st.radio("Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

st.info(f"### {t['titulo']}")

# --- FILA COM LÓGICA DE SENHA PRIVADA ---
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Criar a tabela visual
        # Colunas na planilha: 5 (Senha), 3 (Música), 4 (Artista)
        fila_visual = df_atual.iloc[:, [3, 4, 5]].copy()
        fila_visual.columns = [t["col_mus"], t["col_art"], "senha_original"]
        
        # Lógica para mostrar a senha apenas se ela pertencer ao usuário
        def mascarar_senha(row):
            if str(row["senha_original"]) in st.session_state.minhas_senhas:
                return f"🔑 {row['senha_original']}"
            return "" # Fica em branco para os outros

        fila_visual[t["col_sen"]] = fila_visual.apply(mascarar_senha, axis=1)
        
        # Adicionar Posição
        fila_visual.insert(0, t["col_pos"], [f"{i+1}º" for i in range(len(fila_visual))])
        
        # Remover a coluna original da senha para não vazar
        exibicao = fila_visual.drop(columns=["senha_original"])
        
        st.table(exibicao)
    except Exception as e:
        st.write(t["vazio"])
else:
    st.write(t["vazio"])

# --- ÁREA DE PESQUISA (ESTILO DESENHO) ---
st.markdown("---")
busca = st.text_input(f"🔍 {t['busca']}", key=f"search_{st.session_state.reset_busca}").strip().lower()

if st.session_state.musica_escolhida is None:
    if busca:
        df_cat = carregar_catalogo()
        if df_cat is not None:
            res = df_cat[df_cat.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                         df_cat.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(8)
            
            if not res.empty:
                for i, row in res.iterrows():
                    if st.button(f"🎵 {row.iloc[1]} - {row.iloc[2]}", key=f"song_{i}"):
                        st.session_state.musica_escolhida = row
                        st.rerun()
            else:
                st.error(t["erro"])
else:
    # Confirmação do Pedido
    m = st.session_state.musica_escolhida
    st.success(f"📌 Selecionada: {m.iloc[1]} - {m.iloc[2]}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t["conf"], type="primary"):
            nova_senha = gerar_senha()
            # --- INSIRA SEU ID DA SENHA ABAIXO ---
            id_senha = "INSIRA_O_ID_AQUI" 
            
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                f"entry.{id_senha}": nova_senha
            }
            
            requests.post(url_form, data=dados)
            
            # Salva na lista de "minhas senhas" do navegador
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

# --- ACESSO DJ (Simples e Oculto) ---
with st.expander("Área Técnica"):
    st.write("Planilha de Controle: [Clique aqui para abrir](SUA_URL_DA_PLANILHA)")
