import time

# --- FUNÇÃO PARA LER A FILA COM "FORÇA BRUTA" ---
def carregar_fila():
    # O segredo: adicionamos um número aleatório no fim do link para o Google não usar cache antigo
    timestamp = int(time.time())
    url_dados = f"https://docs.google.com/spreadsheets/d/1FAIpQLSd8SRNim_Uz3KlxdkWzBTdO7zSKSIvQMfiS3flDi6HRKWggYQ/export?format=csv&cachebust={timestamp}"
    
    try:
        # Lemos a planilha
        df_fila = pd.read_csv(url_dados)
        
        # Limpa nomes de colunas (tira espaços)
        df_fila.columns = [c.strip() for c in df_fila.columns]
        
        # Retorna apenas as colunas que queremos mostrar (Música e Artista)
        # Se der erro aqui, vamos mostrar todas as colunas para você me dizer qual é a certa
        return df_fila
    except Exception as e:
        return pd.DataFrame()

# --- EXIBIÇÃO DA FILA NA INTERFACE ---
st.subheader(t["fila_tit"])
df_atual = carregar_fila()

if not df_atual.empty:
    try:
        # Vamos tentar exibir a coluna 3 (Música) e 4 (Artista) 
        # Se a sua planilha tiver colunas diferentes, o código abaixo se ajusta
        fila_visual = df_atual.iloc[:, [3, 4]].copy() 
        fila_visual.columns = ["Música", "Artista"]
        
        # Cria uma numeração de 1º, 2º... baseada no índice
        fila_visual.index = [f"{i+1}º" for i in range(len(fila_visual))]
        
        st.table(fila_visual)
    except:
        # Caso as colunas 3 e 4 não existam, mostramos o que tiver disponível
        st.write("Fila sendo atualizada...")
        st.dataframe(df_atual.head(5)) 
else:
    st.write(t["vazio"])
