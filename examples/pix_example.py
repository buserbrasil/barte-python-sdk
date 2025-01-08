from barte import BarteClient
from datetime import datetime, timedelta

# Inicializa o cliente
client = BarteClient(
    api_key="sua_api_key_aqui",
    environment="sandbox"
)

try:
    # Criar uma cobrança PIX
    # Define data de expiração para 24 horas
    expiration_date = (datetime.utcnow() + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    pix_data = {
        "amount": 9990,  # R$ 99,90
        "description": "Pedido #123 - Loja Virtual",
        "customer": {
            "name": "João da Silva",
            "tax_id": "123.456.789-00",
            "email": "joao@exemplo.com",
            "phone": "+5511999999999"
        },
        "expiration_date": expiration_date
    }
    
    # Criar a cobrança PIX
    charge = client.create_pix_charge(pix_data)
    print("Cobrança PIX criada:", charge)
    
    # Obter dados do QR Code
    charge_id = charge["id"]
    qr_code_data = client.get_pix_qrcode(charge_id)
    print("\nDados do QR Code PIX:")
    print("QR Code:", qr_code_data["qr_code"])
    print("Imagem do QR Code:", qr_code_data["qr_code_image"])
    print("PIX Copia e Cola:", qr_code_data["copy_and_paste"])
    
    # Monitorar status da cobrança
    charge_status = client.get_charge(charge_id)
    print("\nStatus da cobrança:", charge_status["status"])

except Exception as e:
    print("Erro:", str(e)) 