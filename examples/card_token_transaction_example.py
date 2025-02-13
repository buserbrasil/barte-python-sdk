from barte import BarteClient

# Inicializa o cliente
client = BarteClient(api_key="sua_api_key_aqui", environment="sandbox")

try:
    # Primeiro, criar um token de cartão (se ainda não tiver um)
    card_data = {
        "number": "4111111111111111",
        "holder_name": "João da Silva",
        "expiration_month": 12,
        "expiration_year": 2025,
        "cvv": "123",
    }

    token_response = client.create_card_token(card_data)
    token_id = token_response["id"]
    print("Token do cartão criado:", token_id)

    # Agora, realizar uma transação usando o token
    transaction_data = {
        "amount": 2500,  # R$ 25,00
        "description": "Compra com cartão tokenizado",
        "customer": {
            "name": "João da Silva",
            "tax_id": "123.456.789-00",
            "email": "joao@exemplo.com",
        },
        "installments": 1,
        "capture": True,
        "statement_descriptor": "MINHA LOJA",
    }

    # Realizar a transação com o token
    transaction = client.charge_with_card_token(token_id, transaction_data)
    print("Transação realizada com sucesso:", transaction)

    # Verificar o status da transação
    charge_id = transaction["id"]
    charge_details = client.get_charge(charge_id)
    print("Detalhes da transação:", charge_details)

except Exception as e:
    print("Erro:", str(e))
