# Barte Python SDK

[![Tests](https://github.com/buserbrasil/barte-python-sdk/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/buserbrasil/barte-python-sdk/actions/workflows/tests.yml)

A Python SDK for integrating with the Barte payment platform API. This library provides a simple and efficient way to interact with Barte's payment services, allowing you to process payments, manage transactions, and handle customer data securely.

## Features

- Simple and intuitive API client
- Secure payment processing
- Card tokenization support
- Comprehensive error handling
- Type hints for better development experience

## Installation

```bash
pip install barte-python-sdk
```

## Quick Start

```python
from barte import BarteClient

# Initialize the client
client = BarteClient(api_key="your_api_key", environment="sandbox")

# Create a card token
buyer = client.get_buyer({"documentNumber": "00011122233"})

card_token = client.create_card_token({
    "holderName": "Barte Card Test",
    "number": "5383638854440891",
    "cvv": "220",
    "expiration": "12/2025",
    "buyerUuid": buyer.uuid,
})
```

## Documentation

- [OpenAPI Documentation](https://app.swaggerhub.com/apis-docs/b6782/barte-api/1.0.0#/) - Complete API reference
- [Integration Guide](https://barte.notion.site/Guia-de-Integra-o-d25d74ee606f4b9ab33efd9e6a4ea22e#460c4da9a5904fc79b789492438bafc4) - Detailed integration guide with examples and best practices

## Running Tests

To run the test suite, follow these steps:

1. Run tests using pytest:
```bash
uv run pytest tests/ -v --cov=barte --cov-report=xml
```

## Examples

You can find example implementations in the `examples` directory. To run the examples:

1. Clone the repository:
```bash
git clone https://github.com/buser-brasil/barte-python-sdk.git
cd barte-python-sdk
```

2. Run specific examples:
```bash
uv run examples/card_token_example.py
```

Make sure to set up your API credentials before running the examples.

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch:
```bash
git checkout -b feature/amazing-feature
```

3. Install development dependencies:
```bash
uv sync
```

4. Make your changes and ensure tests pass
5. Commit your changes:
```bash
git commit -m 'Add amazing feature'
```

6. Push to the branch:
```bash
git push origin feature/amazing-feature
```

7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation as needed
- Use type hints
- Write meaningful commit messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or need support, please open an issue on GitHub or contact our support team.
