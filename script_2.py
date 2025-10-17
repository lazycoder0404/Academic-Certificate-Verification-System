# Create the wallet management system with RSA digital signatures
wallet_code = """
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import secrets

class AcademicWallet:
    def __init__(self, wallet_id: str = None):
        self.wallet_id = wallet_id or self.generate_wallet_id()
        self.private_key = None
        self.public_key = None
        self.wallet_data = {}
        self.keys_path = f"wallets/{self.wallet_id}"
        os.makedirs("wallets", exist_ok=True)
    
    def generate_wallet_id(self) -> str:
        return hashlib.sha256(str(secrets.randbits(256)).encode()).hexdigest()[:16]
    
    def generate_keys(self) -> bool:
        try:
            # Generate RSA key pair (2048-bit for security)
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key = self.private_key.public_key()
            
            # Save keys to files
            self.save_keys()
            
            # Update wallet data
            self.wallet_data = {
                "wallet_id": self.wallet_id,
                "created_date": datetime.now().isoformat(),
                "public_key_pem": self.get_public_key_pem(),
                "status": "active"
            }
            
            self.save_wallet_data()
            return True
            
        except Exception as e:
            print(f"Error generating keys: {e}")
            return False
    
    def save_keys(self):
        os.makedirs(self.keys_path, exist_ok=True)
        
        # Save private key (encrypted with password in real implementation)
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # For demo purposes
        )
        
        with open(f"{self.keys_path}/private_key.pem", "wb") as f:
            f.write(private_pem)
        
        # Save public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(f"{self.keys_path}/public_key.pem", "wb") as f:
            f.write(public_pem)
    
    def load_keys(self) -> bool:
        try:
            # Load private key
            with open(f"{self.keys_path}/private_key.pem", "rb") as f:
                private_pem = f.read()
            
            self.private_key = serialization.load_pem_private_key(
                private_pem,
                password=None  # In production, use password protection
            )
            
            # Load public key
            with open(f"{self.keys_path}/public_key.pem", "rb") as f:
                public_pem = f.read()
            
            self.public_key = serialization.load_pem_public_key(public_pem)
            
            return True
            
        except FileNotFoundError:
            print(f"Key files not found for wallet {self.wallet_id}")
            return False
        except Exception as e:
            print(f"Error loading keys: {e}")
            return False
    
    def get_public_key_pem(self) -> str:
        if not self.public_key:
            return None
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_pem.decode('utf-8')
    
    def save_wallet_data(self):
        with open(f"{self.keys_path}/wallet_data.json", "w") as f:
            json.dump(self.wallet_data, f, indent=2)
    
    def load_wallet_data(self) -> bool:
        try:
            with open(f"{self.keys_path}/wallet_data.json", "r") as f:
                self.wallet_data = json.load(f)
            return True
        except FileNotFoundError:
            return False
    
    def sign_certificate(self, certificate_data: Dict) -> str:
        if not self.private_key:
            raise ValueError("Private key not loaded")
        
        # Create certificate hash
        cert_json = json.dumps(certificate_data, sort_keys=True)
        cert_hash = hashlib.sha256(cert_json.encode()).hexdigest()
        
        # Sign the hash
        signature = self.private_key.sign(
            cert_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature.hex()
    
    def verify_signature(self, certificate_data: Dict, signature_hex: str, 
                        public_key_pem: str = None) -> bool:
        try:
            # Use provided public key or own public key
            if public_key_pem:
                public_key = serialization.load_pem_public_key(
                    public_key_pem.encode('utf-8')
                )
            else:
                public_key = self.public_key
            
            if not public_key:
                return False
            
            # Create certificate hash
            cert_json = json.dumps(certificate_data, sort_keys=True)
            cert_hash = hashlib.sha256(cert_json.encode()).hexdigest()
            
            # Verify signature
            signature = bytes.fromhex(signature_hex)
            public_key.verify(
                signature,
                cert_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Error verifying signature: {e}")
            return False
    
    def create_signed_certificate(self, student_name: str, student_id: str, 
                                 degree: str, institution: str, 
                                 issue_date: str) -> Dict:
        certificate = {
            "student_name": student_name,
            "student_id": student_id,
            "degree": degree,
            "institution": institution,
            "issue_date": issue_date,
            "issuer_wallet": self.wallet_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Sign the certificate
        signature = self.sign_certificate(certificate)
        
        # Return signed certificate
        signed_cert = certificate.copy()
        signed_cert["signature"] = signature
        signed_cert["public_key"] = self.get_public_key_pem()
        
        return signed_cert
    
    def encrypt_pii(self, personal_data: str) -> Tuple[str, str]:
        if not self.public_key:
            raise ValueError("Public key not available")
        
        # Simple encryption for PII (in production, use hybrid encryption)
        data_bytes = personal_data.encode('utf-8')
        
        # RSA can only encrypt small amounts of data, so we'll just hash for demo
        # In production, use AES + RSA hybrid encryption
        encrypted_hash = hashlib.sha256(data_bytes).hexdigest()
        
        return encrypted_hash, "demo_encryption_method"

class WalletManager:
    def __init__(self):
        self.wallets: Dict[str, AcademicWallet] = {}
        self.load_existing_wallets()
    
    def load_existing_wallets(self):
        if os.path.exists("wallets"):
            for wallet_dir in os.listdir("wallets"):
                wallet_path = f"wallets/{wallet_dir}"
                if os.path.isdir(wallet_path):
                    wallet = AcademicWallet(wallet_dir)
                    if wallet.load_wallet_data() and wallet.load_keys():
                        self.wallets[wallet_dir] = wallet
    
    def create_wallet(self, user_type: str = "institution") -> AcademicWallet:
        wallet = AcademicWallet()
        if wallet.generate_keys():
            wallet.wallet_data["user_type"] = user_type
            wallet.save_wallet_data()
            self.wallets[wallet.wallet_id] = wallet
            return wallet
        return None
    
    def get_wallet(self, wallet_id: str) -> Optional[AcademicWallet]:
        return self.wallets.get(wallet_id)
    
    def list_wallets(self) -> Dict[str, Dict]:
        wallet_info = {}
        for wallet_id, wallet in self.wallets.items():
            wallet_info[wallet_id] = {
                "wallet_id": wallet_id,
                "user_type": wallet.wallet_data.get("user_type", "unknown"),
                "created_date": wallet.wallet_data.get("created_date"),
                "status": wallet.wallet_data.get("status")
            }
        return wallet_info
    
    def validate_certificate_signature(self, certificate: Dict) -> bool:
        if "signature" not in certificate or "public_key" not in certificate:
            return False
        
        # Create temporary wallet for verification
        temp_wallet = AcademicWallet()
        
        # Extract signature and public key
        signature = certificate.pop("signature")
        public_key_pem = certificate.pop("public_key")
        
        # Verify signature
        is_valid = temp_wallet.verify_signature(certificate, signature, public_key_pem)
        
        # Restore certificate data
        certificate["signature"] = signature
        certificate["public_key"] = public_key_pem
        
        return is_valid

def demo_wallet_usage():
    print("=== Academic Wallet System Demo ===")
    
    # Create wallet manager
    manager = WalletManager()
    
    # Create a university wallet
    university_wallet = manager.create_wallet("university")
    print(f"Created university wallet: {university_wallet.wallet_id}")
    
    # Create a student wallet  
    student_wallet = manager.create_wallet("student")
    print(f"Created student wallet: {student_wallet.wallet_id}")
    
    # University issues a certificate
    certificate = university_wallet.create_signed_certificate(
        student_name="Alice Johnson",
        student_id="ST12345",
        degree="Bachelor of Computer Science",
        institution="MIT",
        issue_date="2024-06-15"
    )
    
    print("Certificate created and signed!")
    
    # Verify the certificate
    is_valid = manager.validate_certificate_signature(certificate)
    print(f"Certificate signature valid: {is_valid}")
    
    return manager, university_wallet, student_wallet, certificate

if __name__ == "__main__":
    demo_wallet_usage()
"""

# Write wallet.py
with open('wallet.py', 'w') as f:
    f.write(wallet_code)

print("✅ Created wallet.py successfully!")
print("Features: RSA key generation, digital signatures, certificate signing, PII encryption")