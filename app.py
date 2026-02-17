import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- 1. FUNÇÕES CORE ---
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

# --- 2. GESTÃO DE ESTADO (Sessão e Memória) ---
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0
if 'minha_senha' not in st.session_state:
    st.session_state.minha_senha = None

# --- 3. DICIONÁRIO DE TRADUÇÃO COMPLETO ---
idiomas = {
    "Português 🇧🇷": {
        "busca": "Pesquisar música ou artista...",
        "fila": "Fila de Espera",
        "vazio": "Fila vazia! Peça a primeira!",
        "sel": "Selecionado:",
        "pos": "Sua posição:",
        "conf": "Confirmar ✅",
        "canc": "Cancelar ❌",
        "sucesso": "Pedido feito! Sua Senha:",
        "erro": "Desculpe, no momento não temos essa música. Cheque com o DJ, pois algumas músicas não irão aparecer na lista oficial devido a direitos autorais, obrigado!"
    },
    "English 🇺🇸": {
        "busca": "Search song or artist...",
        "fila": "Current Queue",
        "vazio": "Empty queue! Be the first!",
        "sel": "Selected:",
        "pos": "Your position:",
        "conf": "Confirm ✅",
        "canc": "Cancel ❌",
        "sucesso": "Order placed! Your Token:",
        "erro": "Sorry, we don't have this song at the moment. Please check with the DJ, as some songs may not appear on the official list due to copyright reasons, thank you!"
    },
    "Español 🇪🇦": {
        "busca": "Buscar música o artista...",
        "fila": "Lista de espera",
        "vazio": "¡Lista vacía!",
        "sel": "Seleccionado:",
        "pos": "Tu posición:",
        "conf": "Confirmar ✅",
        "canc": "Cancelar ❌",
        "sucesso": "¡Pedido realizado! Tu Código:",
        "erro": "Lo sentimos, no tenemos esta canción en este momento. Consulta con el DJ, ya que algunas canciones no aparecerán en la lista oficial debido a derechos de autor, ¡gracias!"
    },
    "Français 🇫🇷": {
        "busca": "Chercher uma chanson...",
        "fila": "File d'attente",
        "vazio": "File vide !",
        "sel": "Sélectionné :",
        "pos": "Votre position :",
        "conf": "Confirmer ✅",
        "canc": "Annuler ❌",
        "sucesso": "Demande envoyée ! Votre Code :",
        "erro": "Désolé, nous n'avons pas cette chanson pour o moment. Vérifiez auprès du DJ, car certaines chansons n'apparaîtront pas sur la liste officielle en raison de droits d'auteur, merci !"
    }
}

# --- 4. INTERFACE PRINCIPAL ---
st.title("🎤 Karaokê Coopers")

# Seletor de Idiomas Horizontal
escolha = st.radio("Idioma / Language / Idioma / Langue:", list(idiomas.keys()), horizontal=True)
t = idiomas[escolha]

# Exibição da Senha Fixa (Caso o usuário já tenha pedido)
if st.session_state.minha_senha:
    st.info(f"🔑 {t['sucesso']} {st.session_state.minha_senha}")

st.divider()

# --- 5. TABELA DE FILA ---
st.subheader(f"🎤 {t['fila']}")
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pega Senha (5), Música (3) e Artista (4)
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy()
        fila_visual.columns = ["Senha", "Música", "Artista"]
        fila_visual.index = [f"{i+1}º" for i in range(len(fila_visual))]
        st.table(fila_visual)
    except:
        st.write(t["vazio"])
else:
    st.write(t["vazio"])

st.divider()

# --- 6. LÓGICA DE BUSCA E PEDIDO ---
if st.session_state.musica_escolhida is None:
    # O reset_busca garante que o campo limpe após a confirmação
    busca = st.text_input(t["busca"], key=f"input_{st.session_state.reset_busca}").strip().lower()
    
    if busca:
        df_cat = carregar_catalogo()
        if df_cat is not None:
            res = df_cat[df_cat.iloc[:, 1].str.lower().str.contains(busca, na=False) | 
                         df_cat.iloc[:, 2].str.lower().str.contains(busca, na=False)].head(10)
            
            if not res.empty:
                for i, row in res.iterrows():
                    if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"btn_{i}"):
                        st.session_state.musica_escolhida = row
                        st.rerun()
            else:
                st.error(t["erro"])
else:
    # Tela de Confirmação
    m = st.session_state.musica_escolhida
    posicao_fila = len(df_atual) + 1
    
    st.success(f"✅ {t['sel']} {m.iloc[1]} - {m.iloc[2]}")
    st.warning(f"📢 {t['pos']} {posicao_fila}º")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["conf"], type="primary"):
            nova_senha = gerar_senha()
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            # --- COLE O ID DA SENHA AQUI ---
            id_da_senha = "INSIRA_O_ID_AQUI" 
            
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                f"entry.{id_da_senha}": nova_senha
            }
            
            try:
                requests.post(url_form, data=dados)
                st.session_state.minha_senha = nova_senha # Salva a senha na tela
                st.balloons() # Balões ativados!
                
                # Reseta o sistema para o próximo pedido
                st.session_state.musica_escolhida = None
                st.session_state.reset_busca += 1 
                time.sleep(2)
                st.rerun()
            except:
                st.error("Erro ao enviar pedido. Tente novamente.")

    with col2:
        if st.button(t["canc"]):
            st.session_state.musica_escolhida = None
            st.rerun()

# --- FIM DO CÓDIGO ---
