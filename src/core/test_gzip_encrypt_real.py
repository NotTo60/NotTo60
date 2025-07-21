import os
from database import TriviaDatabase

if __name__ == "__main__":
    # Set up password for encryption
    os.environ["TRIVIA_DB_PASSWORD"] = "demo_password_123"

    db = TriviaDatabase()

    # Test data
    test_data = {"message": "Hello, this is a test of gzip and encryption!"}

    # Compress and encrypt
    compressed = db.compress_data(test_data)
    encrypted = db.encrypt_data(compressed)

    # Write to file
    with open("test_gz_enc.bin", "wb") as f:
        f.write(encrypted)
    print("Encrypted and compressed file written as test_gz_enc.bin")

    # Read back and decrypt
    with open("test_gz_enc.bin", "rb") as f:
        encrypted_read = f.read()
    decrypted = db.decrypt_data(encrypted_read)
    decompressed = db.decompress_data(decrypted)

    print("Decrypted and decompressed content:")
    print(decompressed) 