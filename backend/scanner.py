from scapy.all import ARP, Ether, srp
import socket

def get_network_range():
    #Descobrindo o IP do da rede automaticamente
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip_local = s.getsockname()[0]
        rede = ".".join(ip_local.split('.')[:-1]) + ".0/24"
        return rede
    except Exception as e:
        print(f"Falha ao detectar rede automaticamente: {e}")
        return "192.168.15.0/24"
    finally:
        s.close()
        
def scan_network(ip_range=None):
    #Se o IP não for passado, é descoberto sozinho.
    if ip_range is None:
        ip_range = get_network_range()
        
    print(f"Escanendo rede: {ip_range}")
    
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    result = srp(packet, timeout=3, verbose=False)[0]
    
    dispositivos = []
    for sent, received in result:
        dispositivos.append({'ip': received.psrc, 'mac': received.hwsrc})
        
    return dispositivos