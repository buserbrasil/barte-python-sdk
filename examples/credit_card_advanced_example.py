from barte import BarteClient

# Inicializa o cliente
client = BarteClient(api_key="sua_api_key_aqui", environment="sandbox")

try:
    # Primeiro, criar um token de cartão para usar nos exemplos
    card_data = {
        "number": "4111111111111111",
        "holder_name": "João da Silva",
        "expiration_month": 12,
        "expiration_year": 2025,
        "cvv": "123",
    }

    token_response = client.create_card_token(card_data)
    card_token = token_response["id"]

    # 1. Exemplo de Cobrança Recorrente
    recurring_data = {
        "amount": 5990,  # R$ 59,90
        "description": "Plano Mensal Premium",
        "customer": {
            "name": "João da Silva",
            "tax_id": "123.456.789-00",
            "email": "joao@exemplo.com",
        },
        "card_token": card_token,
        "recurrence": {"interval": "month", "interval_count": 1},
    }

    recurring_charge = client.create_recurring_charge(recurring_data)
    print("\nCobrança Recorrente criada:", recurring_charge)

    # 2. Exemplo de Cobrança Parcelada com Repasse de Taxas
    installment_with_fee_data = {
        "amount": 10000,  # R$ 100,00
        "description": "Compra Parcelada com Juros",
        "customer": {
            "name": "João da Silva",
            "tax_id": "123.456.789-00",
            "email": "joao@exemplo.com",
        },
        "card_token": card_token,
        "installments": 3,
    }

    installment_charge_with_fee = client.create_installment_charge_with_fee(
        installment_with_fee_data
    )
    print("\nCobrança Parcelada com Repasse criada:", installment_charge_with_fee)

    # 3. Exemplo de Cobrança Parcelada sem Repasse de Taxas
    installment_no_fee_data = {
        "amount": 10000,  # R$ 100,00
        "description": "Compra Parcelada sem Juros",
        "customer": {
            "name": "João da Silva",
            "tax_id": "123.456.789-00",
            "email": "joao@exemplo.com",
        },
        "card_token": card_token,
        "installments": 3,
    }

    installment_charge_no_fee = client.create_installment_charge_no_fee(
        installment_no_fee_data
    )
    print("\nCobrança Parcelada sem Repasse criada:", installment_charge_no_fee)

except Exception as e:
    print("Erro:", str(e))
