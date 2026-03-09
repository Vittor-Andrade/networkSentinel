from fastapi import FastAPI, HTTPException
from scanner import scan_network 
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Configuração do CORS para o React conseguir conversar com o Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"] 
)

class DispositivoConhecido(BaseModel):
    mac: str
    nome: str
    tipo: str 

def salvar_no_historico(dispositivos):
    # Inserindo registros no histórico e atualizando a última visualização
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        for d in dispositivos:
            ip = d.get('ip')
            mac = d.get('mac')
            
            if ip and mac:
                # Registro cronológico no histórico com horário local
                cursor.execute('''
                    INSERT INTO historico (ip, mac, data_hora)
                    VALUES (?, ?, datetime('now', 'localtime'))
                ''', (ip, mac))
                
                # Atualização ou inserção do estado atual do dispositivo
                cursor.execute('''
                    INSERT OR REPLACE INTO dispositivos_descobertos (ip, mac, last_seen)
                    VALUES (?, ?, datetime('now', 'localtime'))
                ''', (ip, mac))
            
        conn.commit()
        print(f"[{datetime.now()}] Logs de rede atualizados com sucesso.")
    except Exception as e:
        print(f"Erro crítico ao salvar no banco: {e}")
    finally:
        conn.close()

# --- ROTAS DA API ---

@app.get("/")
def home():
    return {"status": "Network Sentinel v1.2 - Ativo"}

@app.post("/api/cadastrar")
def cadastrar_dispositivo(disp: DispositivoConhecido):
    # Rota para adicionar um dispositivo à Whitelist (Lista de Confiança)
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO conhecidos (mac, nome, tipo)
            VALUES (?, ?, ?)
        ''', (disp.mac.lower(), disp.nome, disp.tipo))
        conn.commit()
        return {"status": "sucesso", "mensagem": f"{disp.nome} foi listado como confiável!"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

@app.get("/api/dispositivos")
def get_dispositivos():
    # Rota principal de monitoramento com o Auto-Scan
    try:
        #Agora não é mais passado IP, o scanner descobre sozinho.
        dispositivos_escaneados = scan_network()
        
        # Buscando a whitelist no banco para cruzar os dados
        conn = sqlite3.connect('seguranca.db')
        cursor = conn.cursor()
        cursor.execute("SELECT mac, nome FROM conhecidos")
        whitelist = {row[0].lower(): row[1] for row in cursor.fetchall()}
        conn.close()
        
        resultado_final = []
        for d in dispositivos_escaneados:
            mac_limpo = d['mac'].lower()
            
            # Verifica se o dispositivo escaneado já é conhecido
            if mac_limpo in whitelist:
                d['status'] = "Conhecido"
                d['nome_personalizado'] = whitelist[mac_limpo]
            else:
                d['status'] = "INTRUSO"
                d['nome_personalizado'] = "Desconhecido"
            
            # Adiciona o dispositivo processado à lista final
            resultado_final.append(d)
        
        # Salva a movimentação da rede no banco de dados
        salvar_no_historico(resultado_final)
        
        return resultado_final
    except Exception as e:
        # Retorna o erro detalhado para ajudar no diagnóstico (Erro 500)
        print(f"Erro no Scan: {e}")
        raise HTTPException(status_code=500, detail=f"Falha no scan: {str(e)}")

@app.get("/api/historico")
def get_historico():
    # Retorna o histórico agrupado por dispositivo para o dashboard
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT ip, mac, strftime('%d/%m/%Y %H:%M:%S', MAX(data_hora)) as ultima_visita
            FROM historico
            WHERE mac IS NOT NULL
            GROUP BY mac
            ORDER BY ultima_visita DESC 
            LIMIT 30
        ''')
        rows = cursor.fetchall()
        # Formata os dados para o padrão que o React espera
        return [{"ip": r[0], "mac": r[1], "data": r[2]} for r in rows]
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()