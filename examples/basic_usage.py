from barte import BarteClient

# Inicializa o cliente
client = BarteClient(
    api_key="sua_api_key_aqui",
    environment="sandbox"  # Use "production" para ambiente de produção
)

# Exemplo de criação de cobrança
charge_data = {
    "amount": 1000,  # Valor em centavos
    "description": "Teste de cobrança",
    "payment_method": "pix",
    "customer": {
        "name": "João da Silva",
        "tax_id": "123.456.789-00",
        "email": "joao@exemplo.com"
    }
}

try:
    # Criar cobrança
    charge = client.create_charge(charge_data)
    print("Cobrança criada:", charge)

    # Consultar cobrança
    charge_id = charge["id"]
    charge_details = client.get_charge(charge_id)
    print("Detalhes da cobrança:", charge_details)

    # Listar cobranças
    charges = client.list_charges({"status": "pending"})
    print("Lista de cobranças:", charges)

    # Cancelar cobrança
    cancelled_charge = client.cancel_charge(charge_id)
    print("Cobrança cancelada:", cancelled_charge)

except Exception as e:
    print("Erro:", str(e)) 