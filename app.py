import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered")

# --- CARREGANDO SUA LISTA DO KARAOKÊ ---
@st.cache_data
def carregar_musicas():
    try:
        # Lendo o arquivo CSV corretamente
        # O encoding='latin1' ajuda a ler acentos sem erro
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        
        # Criando uma coluna única para busca que combina tudo
        df['Busca'] = df['Código'].astype(str) + " - " + df['Música'] + " - " + df['Artista']
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

# Carregando os dados
df_musicas = carregar_musicas()

# --- INTERFACE DO USUÁRIO ---
st.title("🎤 Catálogo de Karaokê - Coopers")

if df_musicas is not None:
    # Seleção de Idioma (Simples e direto)
    idioma = st.selectbox("Escolha o idioma / Select language:", ["Português", "English"])
    
    texto_busca = "Digite o nome da música ou do artista:" if idioma == "Português" else "Type the song or artist name:"
    
    # Campo de busca
    busca = st.text_input(texto_busca).strip().lower()

    if busca:
        # Filtra em qualquer parte do texto (Música ou Artista)
        resultados = df_musicas[df_musicas['Busca'].str.lower().contains(busca, na=False)]
        
        if not resultados.empty:
            st.success(f"Encontramos {len(resultados)} música(s):")
            # Mostra o resultado formatado
            for item in resultados['Busca']:
                st.write(f"✅ {item}")
        else:
            msg_erro = "Não temos essa música no momento, desculpe." if idioma == "Português" else "Sorry, we don't have this song yet."
            st.warning(msg_erro)
    else:
        msg_inicial = "Aguardando sua busca..." if idioma == "Português" else "Waiting for your search..."
        st.info(msg_inicial)
else:
    st.error("O arquivo 'karafuncatalog.csv' não foi encontrado no GitHub. Verifique o nome do arquivo!")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido para uso na Coopers")
