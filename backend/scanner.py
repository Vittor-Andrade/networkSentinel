import socket
import sqlite3
import urllib.request
import time
from scapy.all import ARP, Ether, srp

def get_vendor(mac):
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS fabricantes_cache (mac TEXT PRIMARY KEY, fabricante TEXT)")
    
    mac_upper = mac.upper()
    prefixo = mac_upper[:8]

    BASE_OFFLINE = {
        "1A:DD:44": "Roteador Principal",
        "E8:45:8B": "MitraStar Technology",
        "74:E6:B8": "LG Electronics",
        "38:8B:59": "Google, Inc.",
        "10:7C:61": "ASUSTek COMPUTER INC.",
        "CE:71:F1": "Fabricante Desconhecido",
        "BE:E1:70": "Fabricante Desconhecido"
    }

    try:
        cursor.execute("SELECT fabricante FROM fabricantes_cache WHERE mac = ?", (mac_upper,))
        result = cursor.fetchone()
        if result:
            conn.close()
            return result[0]

        if prefixo in BASE_OFFLINE:
            fabricante = BASE_OFFLINE[prefixo]
            cursor.execute("INSERT OR REPLACE INTO fabricantes_cache (mac, fabricante) VALUES (?, ?)", (mac_upper, fabricante))
            conn.commit()
            conn.close()
            return fabricante

        time.sleep(0.5) 
        url = f"https://api.macvendors.com/{mac_upper}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            fabricante = response.read().decode('utf-8')
            cursor.execute("INSERT OR REPLACE INTO fabricantes_cache (mac, fabricante) VALUES (?, ?)", (mac_upper, fabricante))
            conn.commit()
            conn.close()
            return fabricante
    except:
        conn.close()
        return "Fabricante Desconhecido"

def get_network_range():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip_local = s.getsockname()[0]
        return ".".join(ip_local.split('.')[:-1]) + ".0/24"
    except:
        return "192.168.15.0/24"
    finally:
        s.close()

def scan_network(ip_range=None):
    if ip_range is None:
        ip_range = get_network_range()
    
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=False)[0]

    dispositivos = []
    for sent, received in result:
        mac = received.hwsrc
        fabricante = get_vendor(mac)
        dispositivos.append({
            'ip': received.psrc, 
            'mac': mac,
            'fabricante': fabricante
        })
    return dispositivos