import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

# Configurações
rede = "172.16.0.0/12"   # Altere para o seu range de IP local
porta = 80              # Porta onde o site NGINX está rodando

def verificar_ip(ip):
    try:
        with socket.create_connection((str(ip), porta), timeout=1):
            return str(ip)
    except:
        return None

def escanear_rede(rede, porta):
    ips_encontrados = []
    rede_local = ipaddress.IPv4Network(rede, strict=False)

    with ThreadPoolExecutor(max_workers=100) as executor:
        resultados = executor.map(verificar_ip, rede_local.hosts())

    for ip in resultados:
        if ip:
            ips_encontrados.append(ip)

    return ips_encontrados

# Executa o escaneamento
ips = escanear_rede(rede, porta)

if ips:
    print(f"Encontrado(s) host(s) com a porta {porta} aberta:")
    for ip in ips:
        print(f"- {ip}")
else:
    print(f"Nenhum host com a porta {porta} aberta foi encontrado na rede {rede}")