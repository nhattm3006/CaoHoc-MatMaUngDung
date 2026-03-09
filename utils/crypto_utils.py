from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keys():
    """
    Generates a new RSA 2048-bit key pair.
    Returns: (public_key_pem, private_key_pem) as strings.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Serialize private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Serialize public key
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return public_key_pem, private_key_pem


def verify_signature(public_key_pem, signature_b64, data_bytes):
    """
    Verifies an RSA-SHA256 signature.
    Args:
        public_key_pem (str): The public key in PEM format.
        signature_b64 (str): The signature encoded in Base64.
        data_bytes (bytes): The original data that was signed.
    Returns:
        bool: True if verification succeeds, False otherwise.
    """
    import base64
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.exceptions import InvalidSignature

    try:
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        
        # Decode signature
        signature = base64.b64decode(signature_b64)
        
        # Verify
        public_key.verify(
            signature,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except (InvalidSignature, Exception) as e:
        print(f"Verification failed: {e}")
        return False


def sign_data(private_key_pem, data_bytes):
    """
    Signs data using RSA-SHA256.
    Args:
        private_key_pem (str): The private key in PEM format.
        data_bytes (bytes): The data to be signed.
    Returns:
        str: The signature encoded in Base64.
    """
    import base64
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )
    
    # Sign
    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Return as Base64 string
    return base64.b64encode(signature).decode('utf-8')
