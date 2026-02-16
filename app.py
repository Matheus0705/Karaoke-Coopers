import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# 2. Conexão com a Planilha
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def carregar_catalogo():
    try:
        # Carrega o CSV local
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        # Limpa espaços nos nomes das colunas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return None

df_catalogo = carregar_catalogo()

# 3. Dicionário de Tradução (Corrigido para mudar tudo)
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {
        "label": "Pesquisar música ou artista:",
        "sel": "Selecionado",
        "conf": "Confirmar Música ✅",
        "canc": "Voltar / Trocar ❌",
        "pos": "Sua posição na fila:",
        "sucesso": "Pedido enviado!",
        "admin_tab": "Fila de Espera"
    },
    "English 🇺🇸🇬🇧": {
        "label": "Search song or artist:",
        "sel": "Selected",
        "conf": "Confirm Song ✅",
        "canc": "Back / Change ❌",
        "pos": "Your position in queue:",
        "sucesso": "Order sent!",
        "admin_tab": "Waitlist"
    },
    "Español 🇪🇸": {
        "label": "Buscar música o artista:",
        "sel": "Seleccionado",
        "conf": "Confirmar Canción ✅",
        "canc": "Volver / Cambiar ❌",
        "pos": "Tu posición en la lista:",
        "sucesso": "¡Pedido enviado!",
        "admin_tab": "Lista de espera"
    },
    "Français 🇫🇷": {
        "label": "Rechercher chanson ou artiste :",
        "sel": "Sélectionné",
        "conf": "Confirmer ✅",
        "canc": "Retour / Changer ❌",
        "pos": "Votre position :",
        "sucesso": "Commande envoyada!",
        "admin_tab": "File d'attente"
    }
}

# 4. Interface Lateral (Admin)
menu = st.sidebar.selectbox("Menu", ["Catálogo", "Admin"])

if menu == "Catálogo":
    # Seleção de idioma em bolinhas
    idioma = st.radio("Escolha o idioma / Select language:", list(idiomas_dict.keys()), horizontal=True)
    t = idiomas_dict[idioma]

    if 'musica_escolhida' not in st.session_state:
        st.session_state.musica_escolhida = None

    if st.session_state.musica_escolhida is None:
        # TELA DE BUSCA
        busca = st.text_input(t["label"]).strip().lower()
        if busca:
            # Busca usando posição das colunas para evitar KeyError
            res = df_catalogo[
                df_catalogo.iloc[:, 1].astype(str).str.lower().str.contains(busca, na=False) | 
                df_catalogo.iloc[:, 2].astype(str).str.lower().str.contains(busca, na=False)
            ].head(10)

            for i, row in res.iterrows():
                if st.button(f"🎶 {row.iloc[0]} - {row.iloc[1]} - {row.iloc[2]}", key=f"btn_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
    else:
        # TELA DE CONFIRMAÇÃO
        m = st.session_state.musica_escolhida
        st.success(f"{t['sel']}: {m.iloc[1]}") # Mensagem no idioma certo
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t["conf"], type="primary"):
                try:
                    # Enviar para o Google Sheets
                    fila = conn.read(ttl=0)
                    nova_linha = pd.DataFrame([{
                        "Data": datetime.now().strftime("%H:%M:%S"),
                        "Codigo": str(m.iloc[0]),
                        "Musica": str(m.iloc[1]),
                        "Artista": str(m.iloc[2]),
                        "Status": "Aguardando"
                    }])
                    fila_atualizada = pd.concat([fila, nova_linha], ignore_index=True)
                    conn.update(data=fila_atualizada)
                    
                    st.balloons()
                    st.info(f"{t['sucesso']} {t['pos']} #{len(fila_atualizada)}")
                    if st.button("Novo Pedido"):
                        st.session_state.musica_escolhida = None
                        st.rerun()
                except Exception as e:
                    st.error("Erro ao salvar na planilha. Verifique se ela está como EDITOR.")
        with col2:
            if st.button(t["canc"]):
                st.session_state.musica_escolhida = None
                st.rerun()

else:
    # ABA ADMIN
    senha = st.text_input("Senha Admin", type="password")
    if senha == "coopers123":
        st.subheader("Fila em Tempo Real")
        dados = conn.read(ttl=0)
        st.dataframe(dados)
        if st.button("Limpar Fila Completa"):
            vazio = pd.DataFrame(columns=["Data", "Codigo", "Musica", "Artista", "Status"])
            conn.update(data=vazio)
            st.rerun()
