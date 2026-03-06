import sqlite3

def init_db():
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    #Tabela para salvar dispositivos conhecido (Whitelist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conhecidos (
            mac TEXT PRIMARY KEY,
            nome TEXT,
            tipo TEXT
        )
    ''')
    
    #Tabela para sabermos quem passou pela rede
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            mac TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    #Tabela para não ocupar espaço no Banco com o dispositivos MAC repetidos.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dispositivos_descobertos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            mac TEXT UNIQUE,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )       
   ''')
    conn.commit()
    conn.close()  
    
def salvar_no_historico(dispositivos):
    #Abrimos a conexão
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        for d in dispositivos:
        #Importante: Usamos o .get() para evitar erro caso a chave não exista
            ip = d.get('ip')
            mac = d.get('mac')
            if ip and mac:
                cursor.execute('INSERT INTO historico (ip, mac) VALUES (?, ?)', (ip, mac))
        
        conn.commit()
        print("Histórico salvo com sucesso no Banco.")
    except Exception as e:
        print(f"Erro ao salvar histórico: {e}")
    finally:
        #Só fechamos aqui, depois de processar TUDO
        conn.close()
        
#Inicializando o Banco ao importar o arquivo
init_db()