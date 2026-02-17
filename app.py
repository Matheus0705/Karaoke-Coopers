import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time
import random
import string

# 1. Configuração de Página e Estética
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# 2. Funções de Suporte (Geradores e Leitores)
def gerar_senha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def carregar_fila():
    # O timestamp evita que o Google entregue uma versão "velha" (cache) da planilha
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    try:
        df = pd.read_csv(url_dados)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60) # Atualiza o catálogo a cada 60 segundos se houver mudança
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 3. Gerenciamento de Estado (Memória do App)
if 'minhas_senhas' not in st.session_state:
    st.session_state.minhas_senhas = []
if 'musica_escolhida' not in st.session_state:
    st.session_state.musica_escolhida = None
if 'reset_busca' not in st.session_state:
    st.session_state.reset_busca = 0

# 4. Interface - Título com Microfone (Correção definitiva do erro de HTML)
st.markdown("<h1 style='text-align: center;'>🎤 Karaokê Coopers</h1>", unsafe_allow_html=True)

# 5. Dicionário de Idiomas (Super Completo)
idiomas = {
    "Português BR": {
        "busca": "PESQUISE SUA MÚSICA OU ARTISTA", 
        "fila": "Acompanhe sua vez aqui!", 
        "vazio": "Aguardando o primeiro pedido da noite...", 
        "sucesso": "SUA SENHA:",
        "col_pos": "Posição", "col_sen": "Senha", "col_mus": "Música", "col_art": "Artista",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Selecionada:", "pos_fila": "Sua posição na fila será:"
    },
    "English us": {
        "busca": "SEARCH YOUR SONG OR ARTIST", 
        "fila": "Follow your turn here!", 
        "vazio": "Waiting for the first request...", 
        "sucesso": "YOUR TOKEN:",
        "col_pos": "Position", "col_sen": "Token", "col_mus": "Song", "col_art": "Artist",
        "btn_conf": "CONFIRM ✅", "btn_canc": "CANCEL_CANCEL ❌", "sel": "Selected:", "pos_fila": "Your position will be:"
    },
    "Español EA": {
        "busca": "BUSQUE SUA MÚSICA...", 
        "fila": "¡Sigue tu turno aquí!", 
        "vazio": "¡Lista vacía!", 
        "sucesso": "TU CÓDIGO:",
        "col_pos": "Posición", "col_sen": "Código", "col_mus": "Música", "col_art": "Artista",
        "btn_conf": "CONFIRMAR ✅", "btn_canc": "CANCELAR ❌", "sel": "Seleccionada:", "pos_fila": "Tu posición será:"
    }
}

escolha = st.radio("Selecione o idioma:", list(idiomas.keys()), horizontal=True, label_visibility="collapsed")
t = idiomas[escolha]

# 6. Box de Pedidos do Cliente (Fixo no topo)
if st.session_state.minhas_senhas:
    with st.expander("🎫 MEUS PEDIDOS / MY REQUESTS", expanded=True):
        for s in st.session_state.minhas_senhas:
            st.info(f"🎵 {s['musica']} | 🔑 {t['sucesso']} {s['senha']}")

st.divider()

# 7. Exibição da Fila (Estética de Tabela Profissional)
st.subheader(t["fila"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Pega Senha (5), Música (3) e Artista (4)
        fila_visual = df_atual.iloc[:, [5, 3, 4]].copy()
        
        # Insere a coluna Posição à esquerda (Posição 0)
        posicoes = [f"{i+1}º" for i in range(len(fila_visual))]
        fila_visual.insert(0, t["col_pos"], posicoes)
        
        # Aplica nomes traduzidos
        fila_visual.columns = [t["col_pos"], t["col_sen"], t["col_mus"], t["col_art"]]
        
        # Renderiza a tabela limpa
        st.table(fila_visual)
    except:
        st.write(t["vazio"])
else:
    st.write(t["vazio"])

st.divider()

# 8. Sistema de Busca e Pedido
if st.session_state.musica_escolhida is None:
    # O reset_busca limpa o campo após o pedido ser feito
    busca = st.text_input(t["busca"], key=f"input_{st.session_state.reset_busca}").strip().upper()
    
    if busca:
        df_cat = carregar_catalogo()
        if not df_cat.empty:
            # Filtra por música ou artista
            res = df_cat[df_cat.iloc[:, 1].str.contains(busca, case=False, na=False) | 
                         df_cat.iloc[:, 2].str.contains(busca, case=False, na=False)].head(10)
            
            if not res.empty:
                for i, row in res.iterrows():
                    if st.button(f"🎶 {row.iloc[1]} - {row.iloc[2]}", key=f"song_{i}"):
                        st.session_state.musica_escolhida = row
                        st.rerun()
            else:
                st.error("Música não encontrada / Song not found")
else:
    # Tela de Confirmação (Estética colorida original)
    m = st.session_state.musica_escolhida
    st.success(f"{t['sel']} {m.iloc[1]}")
    st.info(f"{t['pos_fila']} {len(df_atual)+1}º")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button(t["btn_conf"], type="primary", use_container_width=True):
            nova_senha = gerar_senha()
            url_form = "https://docs.google.com/forms/d/e/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/formResponse"
            
            # --- ATENÇÃO: SUBSTITUA O ID ABAIXO PELO SEU ID DA SENHA ---
            id_da_senha = "entry.18065" 
            
            dados = {
                "entry.1213556115": datetime.now().strftime("%H:%M"),
                "entry.1947522889": str(m.iloc[0]),
                "entry.1660854967": str(m.iloc[1]),
                "entry.700923343": str(m.iloc[2]),
                id_da_senha: nova_senha
            }
            
            try:
                requests.post(url_form, data=dados, timeout=5)
                # Salva na memória local do navegador para o cliente ver
                st.session_state.minhas_senhas.append({"musica": m.iloc[1], "senha": nova_senha})
                st.balloons() # Balões ativados!
                
                # Reseta estados para nova busca
                st.session_state.musica_escolhida = None
                st.session_state.reset_busca += 1
                time.sleep(1)
                st.rerun()
            except:
                st.error("Erro de conexão. Tente novamente!")
            
    with col_c2:
        if st.button(t["btn_canc"], use_container_width=True):
            st.session_state.musica_escolhida = None
            st.rerun()
