# Barte Python SDK

[![Tests](https://github.com/buserbrasil/barte-python-sdk/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/buserbrasil/barte-python-sdk/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/buser-brasil/barte-python-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/buser-brasil/barte-python-sdk)

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
client = BarteClient(api_key="your_api_key")

# Create a card token
card_token = client.create_card_token(
    card_number="4111111111111111",
    expiration_month="12",
    expiration_year="2025",
    security_code="123"
)
```

## Running Tests

To run the test suite, follow these steps:

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests using pytest:
```bash
python -m pytest tests/ -v
```

## Examples

You can find example implementations in the `examples` directory. To run the examples:

1. Clone the repository:
```bash
git clone https://github.com/buser-brasil/barte-python-sdk.git
cd barte-python-sdk
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Run specific examples:
```bash
python examples/card_token_example.py
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
pip install -r requirements-dev.txt
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
