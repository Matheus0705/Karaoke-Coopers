import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTable { background-color: #1e1e1e; border-radius: 10px; }
    .fila-header { 
        background-color: #ff4b4b; 
        color: white; 
        padding: 10px; 
        border-radius: 10px 10px 0 0; 
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE ---
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1g88-tIUw0xLedVBlp2UuZmkFG0nAOW1ef58q5j9Jndk/export?format=csv&cachebust={timestamp}"
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

# --- DICIONÁRIO DE TRADUÇÃO ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...",
        "fila": "PROXIMOS CANTORES",
        "vazio": "Fila vazia! Peça a primeira!",
        "sel": "Selecionada:",
        "conf": "CONFIRMAR PEDIDO ✅",
        "canc": "CANCELAR ❌",
        "sucesso": "Pedido Feito! Sua Senha:",
        "aviso_fila": "Sua senha aparecerá na lista no topo em instantes.",
        "erro_busca": "Desculpe, não temos essa música. Cheque com o DJ (direitos autorais)."
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...",
        "fila": "UP NEXT",
        "vazio": "Empty queue! Be the first!",
        "sel": "Selected:",
        "conf": "CONFIRM ORDER ✅",
        "canc": "CANCEL ❌",
        "sucesso": "Request Sent! Your Token:",
        "aviso_fila": "Your token will appear in the list above shortly.",
        "erro_busca": "Sorry, song not found. Check with the DJ (copyright reasons)."
    },
    "Español 🇪🇦": {
        "busca": "Buscar música o artista...",
        "fila": "PRÓXIMOS",
        "vazio": "¡Lista vacía!",
        "sel": "Seleccionada:",
        "conf": "CONFIRMAR ✅",
        "canc": "CANCELAR ❌",
        "sucesso": "¡Pedido hecho! Tu Código:",
        "aviso_fila": "Tu código aparecerá en la lista arriba en breve.",
        "erro_busca": "Lo sentimos, no la encontramos. Consulta al DJ."
    },
    "Français 🇫🇷": {
        "busca": "Chercher une chanson...",
        "fila": "À VENIR",
        "vazio": "File vide !",
        "sel": "Sélectionnée :",
        "conf": "CONFIRMER ✅",
        "canc": "ANNULER ❌",
        "sucesso": "Demande envoyée ! Votre Code :",
        "aviso_fila": "Votre code apparaîtra dans la liste ci-dessus sous peu.",
        "erro_busca": "Désolé, chanson non trouvée. Vérifiez avec le DJ."
    }
}

# --- SELEÇÃO DE IDIOMA ---
escolha_idioma = st.radio("Language / Idioma:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha_idioma]

st.divider()

# --- CABEÇALHO COM LOGO E TÍTULO ---
col_logo1, col_logo2 = st.columns([1, 3])
with col_logo1:
    try:
        st.image("9d8daa_198ec12882054dceb6d49d760eba30f0~mv2.jpg", width=100) 
    except:
        st.write("🎤")
with col_logo2:
    st.title("Karaokê Coopers")

# --- INTERFACE: PARTE SUPERIOR (FILA PÚBLICA) ---
st.markdown(f'<div class="fila-header">{t["fila"]}</div>', unsafe_allow_html=True)
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy()
        fila_visual.columns = ["SENHA", "MÚSICA", "ARTISTA"]
        fila_visual.index = [f"{i+1}º" for i in range(len(fila_visual))]
        st.table(fila_visual.head(10)) 
    except:
        st.info("...")
else:
    st.info(t["vazio"])

st.divider()

# --- INTERFACE: PARTE INFERIOR (PESQUISA E PEDIDO) ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None

if st.session_state.musica_escolhida is None:
    busca = st.text_input(t["busca"], key="input_pesquisa").strip().lower()
    
    if busca:
        df_cat = carregar_catalogo()
        if not df_cat.empty:
            res = df_cat[df_cat.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                         df_cat.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(8)
            
            if not res.empty:
                for i, row in res.iterrows():
                    if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"btn_{i}"):
                        st.session_state.musica_escolhida = row
                        st.rerun()
            else:
                st.error(t["erro_busca"])
else:
    m = st.session_state.musica_escolhida
    st.success(f"✅ {t['sel']} {m.iloc[1]} ({m.iloc[2]})")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
            nova_senha = gerar_senha()
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                "entry.1583091993": nova_senha 
            }
            
            try:
                requests.post(url_form, data=dados)
                st.balloons()
                st.markdown(f"### 🎉 {t['sucesso']} **{nova_senha}**")
                st.info(t["aviso_fila"])
                
                time.sleep(5)
                st.session_state.musica_escolhida = None
                st.rerun()
            except:
                st.error("Error!")
                
    with col2:
        if st.button(t["canc"]):
            st.session_state.musica_escolhida = None
            st.rerun()
