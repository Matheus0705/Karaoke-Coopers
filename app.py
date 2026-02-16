import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Karaokê Coopers", layout="centered", page_icon="🎤")

# --- CARREGANDO SUA LISTA DO KARAOKÊ ---
@st.cache_data
def carregar_musicas():
    try:
        # sep=None com engine='python' faz o Pandas descobrir sozinho se é vírgula ou ponto e vírgula
        df = pd.read_csv('karafuncatalog.csv', encoding='latin1', sep=None, engine='python')
        
        # Limpar espaços em branco que podem vir nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # Criando uma coluna única para busca que combina tudo
        # Usamos .get() para evitar erro caso a coluna tenha nome levemente diferente
        col_codigo = 'Código' if 'Código' in df.columns else df.columns[0]
        col_musica = 'Música' if 'Música' in df.columns else df.columns[1]
        col_artista = 'Artista' if 'Artista' in df.columns else df.columns[2]

        df['Busca'] = df[col_codigo].astype(str) + " - " + df[col_musica] + " - " + df[col_artista]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

# Carregando os dados
df_musicas = carregar_musicas()

# --- INTERFACE DO USUÁRIO ---
st.title("🎤 Catálogo de Karaokê - Coopers")

if df_musicas is not None:
    # Seleção de Idioma
    idioma = st.radio("Escolha o idioma / Select language:", ("Português", "English"), horizontal=True)
    
    label_campo = "Digite o nome da música ou do artista:" if idioma == "Português" else "Type the song or artist name:"
    
    # Campo de busca (O segredo da busca em tempo real)
    busca = st.text_input(label_campo).strip().lower()

    if busca:
        # Filtra os resultados que contém o texto digitado
        resultados = df_musicas[df_musicas['Busca'].str.lower().str.contains(busca, na=False)]
        
        if not resultados.empty:
            st.success(f"Encontramos {len(resultados)} música(s):" if idioma == "Português" else f"Found {len(resultados)} song(s):")
            for item in resultados['Busca']:
                st.write(f"🎶 {item}")
        else:
            msg_vazio = "Não temos essa música no momento, desculpe." if idioma == "Português" else "Song not found, sorry."
            st.warning(msg_vazio)
    else:
        st.info("Digite algo acima para buscar sua música! 🔎" if idioma == "Português" else "Type something above to search! 🔎")
else:
    st.error("O arquivo 'karafuncatalog.csv' não pôde ser lido. Verifique se ele está no GitHub.")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido para uso na Coopers")
