from barte import BarteClient


def main():
    # Initialize the client
    client = BarteClient(
        api_key="your_api_key",
        environment="sandbox",  # Use "production" for production environment
    )

    # Create a credit card charge
    charge_data = {
        "amount": 1000,  # R$ 10,00
        "currency": "BRL",
        "payment_method": "credit_card",
        "description": "Example charge",
        "customer": {
            "name": "John Doe",
            "tax_id": "123.456.789-00",
            "email": "john@example.com",
        },
        "metadata": {"order_id": "123", "product_id": "456"},
    }

    # Create and print charge details
    charge = client.create_charge(charge_data)
    print("\nCredit Card Charge:")
    print(f"ID: {charge.id}")
    print(f"Amount: R$ {charge.amount / 100:.2f}")
    print(f"Status: {charge.status}")
    print(f"Customer: {charge.customer.name}")
    print(f"Created at: {charge.created_at}")

    # Create a PIX charge
    pix_data = {
        "amount": 1500,  # R$ 15,00
        "currency": "BRL",
        "description": "Example PIX charge",
        "customer": {
            "name": "John Doe",
            "tax_id": "123.456.789-00",
            "email": "john@example.com",
        },
    }

    # Create PIX charge and get QR code
    pix_charge = client.create_pix_charge(pix_data)
    pix_charge = pix_charge.get_qr_code()

    print("\nPIX Charge:")
    print(f"ID: {pix_charge.id}")
    print(f"Amount: R$ {pix_charge.amount / 100:.2f}")
    print(f"Status: {pix_charge.status}")
    print(f"QR Code: {pix_charge.qr_code}")
    print(f"Copy and Paste code: {pix_charge.copy_and_paste}")

    # List recent charges
    print("\nRecent charges:")
    charges = client.list_charges({"limit": 5})
    for charge in charges:
        print(f"- {charge.id}: R$ {charge.amount / 100:.2f} ({charge.status})")

    # Refund the credit card charge
    refund = charge.refund(amount=500)  # Partial refund of R$ 5,00
    print("\nRefund:")
    print(f"ID: {refund.id}")
    print(f"Amount: R$ {refund.amount / 100:.2f}")
    print(f"Status: {refund.status}")
    print(f"Created at: {refund.created_at}")


if __name__ == "__main__":
    main()
