from barte import BarteClient


def main():
    # Initialize the client
    client = BarteClient(
        api_key="your_api_key",
        environment="sandbox",  # Use "production" for production environment
    )

    # Create a card token
    card_data = {
        "number": "4111111111111111",
        "holder_name": "John Doe",
        "expiration_month": 12,
        "expiration_year": 2025,
        "cvv": "123",
    }

    # Tokenize the card
    card_token = client.create_card_token(card_data)
    print("\nCard Token:")
    print(f"Token ID: {card_token.id}")
    print(f"Card Brand: {card_token.brand}")
    print(f"Last Digits: {card_token.last_digits}")
    print(f"Holder Name: {card_token.holder_name}")
    print(f"Created at: {card_token.created_at}")

    # Simulate installments
    amount = 10000  # R$ 100,00
    installments = client.simulate_installments(amount=amount, brand=card_token.brand)

    print("\nInstallment Options:")
    for option in installments.installments:
        print(
            f"{option.installments}x of R$ {option.amount / 100:.2f} "
            f"(total: R$ {option.total / 100:.2f}, interest: {option.interest_rate}%)"
        )

    # Create a charge with the card token
    charge_data = {
        "amount": amount,
        "currency": "BRL",
        "description": "Example charge with installments",
        "customer": {
            "name": "John Doe",
            "tax_id": "123.456.789-00",
            "email": "john@example.com",
        },
        "installments": 3,  # 3 installments
        "metadata": {"order_id": "123", "product_id": "456"},
    }

    # Create the charge
    charge = client.charge_with_card_token(card_token.id, charge_data)
    print("\nCharge:")
    print(f"ID: {charge.id}")
    print(f"Amount: R$ {charge.amount / 100:.2f}")
    print(f"Status: {charge.status}")
    print(f"Customer: {charge.customer.name}")
    print(f"Created at: {charge.created_at}")

    # Get charge details after a while
    updated_charge = client.get_charge(charge.id)
    print(f"\nCharge status: {updated_charge.status}")

    # List refunds for this charge
    refunds = client.get_charge_refunds(charge.id)
    if refunds:
        print("\nRefunds:")
        for refund in refunds:
            print(f"- {refund.id}: R$ {refund.amount / 100:.2f} ({refund.status})")
    else:
        print("\nNo refunds yet")

    # Create a partial refund
    refund = charge.refund(amount=3000)  # Refund R$ 30,00
    print("\nPartial Refund:")
    print(f"ID: {refund.id}")
    print(f"Amount: R$ {refund.amount / 100:.2f}")
    print(f"Status: {refund.status}")
    print(f"Created at: {refund.created_at}")


if __name__ == "__main__":
    main()
