# Distributed File Storage System

This project implements a distributed file storage system with blockchain-based metadata management and multiple web interfaces. It provides secure file storage through encryption, sharding, and distribution across multiple storage providers.

## Features

- **File Encryption**: All files are encrypted before storage.
- **File Sharding**: Encrypted files are split into multiple shards for distributed storage.
- **Blockchain Integration**: File metadata is stored on a simple blockchain for tamper-resistant record-keeping.
- **Distributed Storage**: File shards are distributed across multiple storage providers.
- **Multiple Web Interfaces**: Easy-to-use web interfaces for file upload and download, supporting multiple clients.
- **Multi-threading**: Efficient communication with multiple storage providers.

## Components

1. **Storage Provider (SP) Network** (`sp1.py`, `sp2.py`, `sp3.py`):
   - Implements multiple storage provider nodes in the blockchain network.
   - Each SP file (`sp1.py`, `sp2.py`, `sp3.py`) represents a separate node in the distributed network.
   - Handles file uploads, downloads, and blockchain operations.

2. **Web Interfaces** (`client1.py`, `client2.py`):
   - Flask-based web applications serving as client interfaces.
   - Each demo file represents a separate client in the system.
   - Provides functionality for file upload and download.

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/distributed-file-storage.git
   cd distributed-file-storage
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Start the Storage Provider nodes (run each in a separate terminal):
   ```
   python sp1.py
   python sp2.py
   python sp3.py
   ```

4. Start the web interfaces (run each in a separate terminal):
   ```
   python clinet1.py
   python client2.py
   ```

5. Access the web interfaces:
   - Client 1: `http://localhost:5000` in your web browser
   - Client 2: `http://localhost:5001` in your web browser (assuming it runs on a different port)

## Usage

1. **Uploading a File**:
   - Click on the "Upload" button in either web interface.
   - Enter the name of the file you want to upload. The file should exist in the same folder with the client.py file. 
   - The file will be encrypted, sharded, and distributed across the storage providers.

2. **Downloading a File**:
   - Click on the "Download" button in either web interface.
   - Select the file you want to download from the list of your uploaded files.
   - The file shards will be retrieved, reassembled, and decrypted for you to download.

## Security Considerations

- This system uses encryption for file storage, but proper key management is crucial.
- The blockchain implementation is basic and meant for demonstration purposes. In a production environment, a more robust blockchain solution should be implemented.

## Contributing

Contributions to improve the system are welcome. Please feel free to submit pull requests or open issues to discuss potential enhancements.

## License

[MIT License](LICENSE)
