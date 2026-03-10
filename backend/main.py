from fastapi import FastAPI, HTTPException
from scanner import scan_network 
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

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
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        for d in dispositivos:
            ip = d.get('ip')
            mac = d.get('mac')
            if ip and mac:
                cursor.execute("INSERT INTO historico (ip, mac, data_hora) VALUES (?, ?, datetime('now', 'localtime'))", (ip, mac))
                cursor.execute("INSERT OR REPLACE INTO dispositivos_descobertos (ip, mac, last_seen) VALUES (?, ?, datetime('now', 'localtime'))", (ip, mac))
        conn.commit()
    except Exception as e:
        print(f"Erro no banco: {e}")
    finally:
        conn.close()

@app.get("/api/dispositivos")
def get_dispositivos():
    try:
        dispositivos_escaneados = scan_network()
        conn = sqlite3.connect('seguranca.db')
        cursor = conn.cursor()
        cursor.execute("SELECT mac, nome FROM conhecidos")
        whitelist = {row[0].lower(): row[1] for row in cursor.fetchall()}
        conn.close()
        
        resultado_final = []
        for d in dispositivos_escaneados:
            mac_limpo = d['mac'].lower()
            if mac_limpo in whitelist:
                d['status'] = "Conhecido"
                d['nome_personalizado'] = whitelist[mac_limpo]
            else:
                d['status'] = "INTRUSO"
                d['nome_personalizado'] = d['fabricante']
            resultado_final.append(d)
        
        salvar_no_historico(resultado_final)
        return resultado_final
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historico")
def get_historico():
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                h.ip, 
                h.mac, 
                strftime('%d/%m/%Y %H:%M:%S', MAX(h.data_hora)) as ultima_visita,
                COALESCE(f.fabricante, 'Não Identificado') as fabricante
            FROM historico h
            LEFT JOIN fabricantes_cache f ON UPPER(h.mac) = UPPER(f.mac)
            GROUP BY h.mac
            ORDER BY ultima_visita DESC 
            LIMIT 30
        ''')
        rows = cursor.fetchall()
        return [{"ip": r[0], "mac": r[1], "data": r[2], "fabricante": r[3]} for r in rows]
    except Exception as e:
        return []
    finally:
        conn.close()

@app.post("/api/cadastrar")
def cadastrar_dispositivo(disp: DispositivoConhecido):
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO conhecidos (mac, nome, tipo) VALUES (?, ?, ?)", (disp.mac.lower(), disp.nome, disp.tipo))
        conn.commit()
        return {"status": "sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()