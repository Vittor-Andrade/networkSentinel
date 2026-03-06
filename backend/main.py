from fastapi import FastAPI
from scanner import scan_network 
from database import salvar_no_historico
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuração do CORS para o React conseguir conversar com o Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"] 
)

# Rota inicial para teste
@app.get("/")
def home():
    return {"status": "Sistema de Segurança Online"}

class DispositivoConhecido(BaseModel):
    mac: str
    nome: str
    tipo: str 
    
@app.post("/api/cadastrar")
def cadastrar_dispositivo(disp: DispositivoConhecido):
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        # Insere ou atualiza o dispositivo na whitelist
        cursor.execute('''
            INSERT OR REPLACE INTO conhecidos (mac, nome, tipo)
            VALUES(?, ?, ?)   
        ''', (disp.mac.lower(), disp.nome, disp.tipo))
        conn.commit()
        return {"status": "sucesso", "mensagem": f"{disp.nome} cadastrado!"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

@app.get("/api/dispositivos")
def salvar_no_historico(dispositivos): #usando o INSERT OR REPLACE para evitar DUPLICATAS no Banco
    conn = sqlite3.connenct('seguranca.db')
    cursor = conn.cursor()
    for d in dispositivos:
        cursor.execute('''
            INSERT OR REPLACE INTO dispositivos_descobertos (ip, mac, last_seen) VALUES (?, ?, CURRENT_TIMESTAMP)     
        ''', (d['ip'], d['mac']))
        conn.commit()
        conn.close()

def get_dispositivos():
    range_rede = "192.168.15.1/24"
    dispositivos = scan_network(range_rede)
    
    # Busca a lista de conhecidos no banco
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    cursor.execute("SELECT mac, nome FROM conhecidos")
    whitelist = {row[0].lower(): row[1] for row in cursor.fetchall()}
    conn.close()
    
    resultado_final = []
    
    for d in dispositivos:
        # Garantimos que o MAC está em minúsculo para comparar
        mac_atual = d['mac'].lower()
        
        # O print corrigido (sem o erro de NameError)
        print(f"Debug: Processando MAC {mac_atual}")
        
        if mac_atual in whitelist:
            d['status'] = "Conhecido"
            d['nome_personalizado'] = whitelist[mac_atual]
        else:
            d['status'] = "INTRUSO"
            d['nome_personalizado'] = "Desconhecido"
        
        resultado_final.append(d)
    
    # Salvamos o resultado já processado no histórico
    salvar_no_historico(resultado_final)
    
    return resultado_final