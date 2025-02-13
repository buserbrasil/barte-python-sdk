from barte import BarteClient, PixCharge, PixQRCode
from datetime import datetime, timedelta


def main():
    # Initialize the client
    client = BarteClient(
        api_key="your_api_key",
        environment="sandbox",  # Use "production" for production environment
    )

    # Create a PIX charge with expiration
    expiration = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    pix_data = {
        "amount": 15000,  # R$ 150,00
        "currency": "BRL",
        "description": "Example PIX charge",
        "customer": {
            "name": "John Doe",
            "tax_id": "123.456.789-00",
            "email": "john@example.com",
        },
        "expiration_date": expiration,
        "metadata": {"order_id": "123", "product_id": "456"},
    }

    # Create PIX charge
    pix_charge: PixCharge = client.create_pix_charge(pix_data)
    print("\nPIX Charge Created:")
    print(f"ID: {pix_charge.id}")
    print(f"Amount: R$ {pix_charge.amount / 100:.2f}")
    print(f"Status: {pix_charge.status}")
    print(f"Customer: {pix_charge.customer.name}")
    print(f"Created at: {pix_charge.created_at}")

    # Get QR code data
    # Option 1: Using the charge object method
    pix_charge = pix_charge.get_qr_code()
    print("\nPIX Payment Information (via charge):")
    print(f"QR Code: {pix_charge.qr_code}")
    print(f"QR Code Image URL: {pix_charge.qr_code_image}")
    print(f"Copy and Paste code: {pix_charge.copy_and_paste}")

    # Option 2: Getting QR code directly
    qr_code: PixQRCode = client.get_pix_qrcode(pix_charge.id)
    print("\nPIX Payment Information (direct):")
    print(f"QR Code: {qr_code.qr_code}")
    print(f"QR Code Image URL: {qr_code.qr_code_image}")
    print(f"Copy and Paste code: {qr_code.copy_and_paste}")

    # Get charge details after a while
    updated_charge: PixCharge = client.get_charge(pix_charge.id)
    print(f"\nCharge status: {updated_charge.status}")

    # List all PIX charges
    print("\nRecent PIX charges:")
    charges = client.list_charges({"payment_method": "pix", "limit": 5})
    for charge in charges:
        if isinstance(charge, PixCharge):
            print(f"- {charge.id}: R$ {charge.amount / 100:.2f} ({charge.status})")

    # Cancel the charge if still pending
    if updated_charge.status == "pending":
        canceled_charge = updated_charge.cancel()
        print(f"\nCharge canceled: {canceled_charge.status}")
    else:
        print(f"\nCharge cannot be canceled: {updated_charge.status}")


if __name__ == "__main__":
    main()
