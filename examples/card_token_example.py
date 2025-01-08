from barte import BarteClient

# Inicializa o cliente
client = BarteClient(
    api_key="sua_api_key_aqui",
    environment="sandbox"
)

# Dados do cartão
card_data = {
    "number": "4111111111111111",
    "holder_name": "João da Silva",
    "expiration_month": 12,
    "expiration_year": 2025,
    "cvv": "123"
}

try:
    # Criar token do cartão
    token_response = client.create_card_token(card_data)
    print("Token do cartão criado:", token_response)
    
    # O token pode ser usado para criar uma cobrança
    charge_data = {
        "amount": 1000,
        "description": "Teste de cobrança com cartão",
        "payment_method": "credit_card",
        "card_token": token_response["id"],
        "customer": {
            "name": "João da Silva",
            "tax_id": "123.456.789-00",
            "email": "joao@exemplo.com"
        }
    }
    
    charge = client.create_charge(charge_data)
    print("Cobrança criada com cartão:", charge)

except Exception as e:
    print("Erro:", str(e)) 