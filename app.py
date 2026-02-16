import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers Portugal", layout="centered", page_icon="🎤")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Para funcionar, você precisa conectar no painel do Streamlit Cloud depois!
from streamlit_gsheets import GSheetsConnection
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def carregar_catalogo():
    try:
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        # Limpa nomes de colunas de qualquer espaço invisível
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return None

df_catalogo = carregar_catalogo()

# --- DICIONÁRIO DE TRADUÇÃO ---
idiomas_dict = {
    "Português 🇧🇷🇵🇹": {
        "label": "Digite o nome da música ou artista:",
        "selecionado": "Selecionado",
        "confirmar": "Confirmar Música ✅",
        "cancelar": "Voltar / Trocar ❌",
        "posicao": "Sua posição na fila:",
        "sucesso": "✅ Música enviada com sucesso!"
    },
    "English 🇺🇸🇬🇧": {
        "label": "Type the song or artist name:",
        "selecionado": "Selected",
        "confirmar": "Confirm Song ✅",
        "cancelar": "Go Back / Change ❌",
        "posicao": "Your position in queue:",
        "sucesso": "✅ Song sent successfully!"
    },
    "Español 🇪🇸": {
        "label": "Escribe el nombre de la canción o artista:",
        "selecionado": "Seleccionado",
        "confirmar": "Confirmar Canción ✅",
        "cancelar": "Volver / Cambiar ❌",
        "posicao": "Tu posición en la lista:",
        "sucesso": "✅ ¡Canción enviada!"
    },
    "Français 🇫🇷": {
        "label": "Tapez le nom de la chanson ou de l'artiste :",
        "selecionado": "Sélectionné",
        "confirmar": "Confirmer ✅",
        "cancelar": "Retour / Changer ❌",
        "posicao": "Votre position dans la file :",
        "sucesso": "✅ Chanson envoyée !"
    }
}

# --- INTERFACE ---
st.title("🎤 Karaokê Coopers")

idioma_escolhido = st.radio("Escolha o idioma / Select language:", list(idiomas_dict.keys()), horizontal=True)
textos = idiomas_dict[idioma_escolhido]

if df_catalogo is not None:
    if 'musica_escolhida' not in st.session_state:
        st.session_state.musica_escolhida = None

    if st.session_state.musica_escolhida is None:
        busca = st.text_input(textos["label"]).strip().lower()
        if busca:
            # Busca por posição das colunas para evitar KeyError
            col_cod, col_mus, col_art = df_catalogo.columns[0], df_catalogo.columns[1], df_catalogo.columns[2]
            
            res = df_catalogo[
                df_catalogo[col_mus].astype(str).str.lower().str.contains(busca, na=False) |
                df_catalogo[col_art].astype(str).str.lower().str.contains(busca, na=False)
            ].head(10)

            for i, row in res.iterrows():
                if st.button(f"🎶 {row[col_cod]} - {row[col_mus]} - {row[col_art]}", key=f"btn_{i}"):
                    st.session_state.musica_escolhida = row
                    st.rerun()
    else:
        m = st.session_state.musica_escolhida
        col_mus = df_catalogo.columns[1]
        st.success(f"{textos['selecionado']}: {m[col_mus]}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(textos["confirmar"], type="primary"):
                try:
                    # Tenta salvar na planilha do Google
                    fila_atual = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
                    nova_musica = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Codigo": m[df_catalogo.columns[0]],
                        "Musica": m[df_catalogo.columns[1]],
                        "Artista": m[df_catalogo.columns[2]],
                        "Status": "Aguardando"
                    }])
                    fila_atual = pd.concat([fila_atual, nova_musica], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=fila_atual)
                    
                    st.balloons()
                    st.info(f"{textos['sucesso']} {textos['posicao']} #{len(fila_atual)}")
                except:
                    st.error("Erro de conexão com a planilha. Verifique os Secrets.")
                
                with col1:
            if st.button(t["conf"], type="primary"):
                try:
                    # Tenta ler a fila (limpando o cache para garantir que lê o que está no Google)
                    fila = conn.read(ttl=0) 
                    
                    # Cria a nova linha
                    nova = pd.DataFrame([{
                        "Data": datetime.now().strftime("%H:%M"),
                        "Codigo": str(m.iloc[0]),
                        "Musica": str(m.iloc[1]),
                        "Artista": str(m.iloc[2]),
                        "Status": "Aguardando"
                    }])
                    
                    # Junta e faz o update
                    fila_atualizada = pd.concat([fila, nova], ignore_index=True)
                    conn.update(data=fila_atualizada)
                    
                    st.balloons()
                    st.success(f"{t['sucesso']} {t['pos']} #{len(fila_atualizada)}")
                except Exception as e:
                    st.error(f"Erro de Conexão: Verifique se a Planilha está como EDITOR e se os Secrets estão em uma linha só.")
                    st.info(f"Detalhe técnico: {e}") # Isso vai nos dizer exatamente o que está errado
