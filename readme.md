Based on the provided code, here's a README file for your Django application:

---

# Django Blockchain Application

This Django application simulates a blockchain system for keeping track of medical patient data securely.

## Features:

- Load or generate encryption keys.
- Create a genesis block.
- Create and add new blocks with patient data to the blockchain.
- Encrypt data before adding it to a block.
- Decrypt data retrieved from a block.
- Verify the integrity of the entire blockchain.
- Load blocks from stored files.
- Display chain status and patient data on a web page.

## Requirements:

- Python (>=3.6)
- Django
- pandas
- cryptography
- hashlib

## How to Setup:

1. Ensure you have Python and the required libraries installed.
2. Clone this repository.
3. Navigate to the root of the project and run:
```bash
python manage.py runserver
```

## Usage:

1. Start the server and navigate to the displayed IP (usually `http://127.0.0.1:8000/`).
2. The home page will display the status of the blockchain, patient data, and other statistics.
3. To add a new block with patient data, use the provided form and click on the 'Save Block' button.

## Code Overview:

- `load_or_generate_key()`: Loads an existing encryption key or generates a new one if not found.
- `index(request)`: The main view function that displays the blockchain status and patient data.
- `create_genesis_block()`: Creates the first block of the blockchain.
- `create_new_block(previous_block, data)`: Creates a new block with the provided data.
- `encrypt_data(data) & decrypt_data(encrypted_data)`: Functions to encrypt and decrypt block data using Fernet encryption.
- `save_block_to_file(block, folder='blocks') & load_block_from_file(filepath)`: Functions to save a block to a file and load a block from a file.
- `verify_blockchain(folder='blocks')`: Checks the integrity of the entire blockchain and returns a Boolean indicating its validity.
- `SaveBlock(request)`: A view function to save a new block with data from the form.

## Note:

Make sure to keep your encryption key (`key.csv`) secure and do not share or lose it, as it's essential for data encryption and decryption in the blockchain. The key is only associated with the data encryption. Even if you lose the key. the Chain will be still valid. but the data won't be readable. 

---

This README provides an overview of your application and its functionalities.