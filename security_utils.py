"""
Security Utilities - Encryption and Wallet Security
EthIstanbul Hackathon Project
"""

import os
import base64
import hashlib
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class WalletSecurity:
    """Wallet security and encryption utilities"""
    
    def __init__(self, master_password: str = None):
        """
        Initialize security utilities
        
        Args:
            master_password: Master password for encryption (optional)
        """
        self.master_password = master_password or os.getenv('WALLET_MASTER_PASSWORD', 'default_dev_password')
        self._cipher_cache = {}
    
    def _get_cipher(self, salt: bytes = None) -> Fernet:
        """Get or create cipher for encryption/decryption"""
        if salt is None:
            salt = b'static_salt_for_dev'  # In production, use random salt per user
        
        salt_key = salt.hex()
        if salt_key not in self._cipher_cache:
            # Derive key from master password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,  # Adjust for security vs performance
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
            self._cipher_cache[salt_key] = Fernet(key)
        
        return self._cipher_cache[salt_key]
    
    def encrypt_private_key(self, private_key: str, user_id: str = None) -> Dict[str, str]:
        """
        Encrypt private key for secure storage
        
        Args:
            private_key: Raw private key to encrypt
            user_id: User identifier for salt generation
            
        Returns:
            Dict containing encrypted data and metadata
        """
        try:
            # Generate user-specific salt
            if user_id:
                salt = hashlib.sha256(f"wallet_salt_{user_id}".encode()).digest()[:16]
            else:
                salt = b'static_salt_for_dev'
            
            cipher = self._get_cipher(salt)
            encrypted_key = cipher.encrypt(private_key.encode())
            
            return {
                'encrypted_private_key': base64.urlsafe_b64encode(encrypted_key).decode(),
                'salt': base64.urlsafe_b64encode(salt).decode(),
                'encryption_version': 'v1',
                'created_at': str(int(__import__('time').time()))
            }
            
        except Exception as e:
            raise Exception(f"Private key encryption failed: {str(e)}")
    
    def decrypt_private_key(self, encrypted_data: Dict[str, str]) -> str:
        """
        Decrypt private key from secure storage
        
        Args:
            encrypted_data: Dictionary containing encrypted key and metadata
            
        Returns:
            Decrypted private key string
        """
        try:
            encrypted_key = base64.urlsafe_b64decode(encrypted_data['encrypted_private_key'])
            salt = base64.urlsafe_b64decode(encrypted_data['salt'])
            
            cipher = self._get_cipher(salt)
            decrypted_key = cipher.decrypt(encrypted_key)
            
            return decrypted_key.decode()
            
        except Exception as e:
            raise Exception(f"Private key decryption failed: {str(e)}")
    
    def encrypt_seed_phrase(self, seed_phrase: str, user_id: str = None) -> Dict[str, str]:
        """
        Encrypt seed phrase for secure storage
        
        Args:
            seed_phrase: Raw seed phrase to encrypt
            user_id: User identifier for salt generation
            
        Returns:
            Dict containing encrypted data and metadata
        """
        try:
            # Generate user-specific salt
            if user_id:
                salt = hashlib.sha256(f"seed_salt_{user_id}".encode()).digest()[:16]
            else:
                salt = b'static_seed_salt_dev'
            
            cipher = self._get_cipher(salt)
            encrypted_seed = cipher.encrypt(seed_phrase.encode())
            
            return {
                'encrypted_seed_phrase': base64.urlsafe_b64encode(encrypted_seed).decode(),
                'salt': base64.urlsafe_b64encode(salt).decode(),
                'encryption_version': 'v1',
                'created_at': str(int(__import__('time').time()))
            }
            
        except Exception as e:
            raise Exception(f"Seed phrase encryption failed: {str(e)}")
    
    def decrypt_seed_phrase(self, encrypted_data: Dict[str, str]) -> str:
        """
        Decrypt seed phrase from secure storage
        
        Args:
            encrypted_data: Dictionary containing encrypted seed and metadata
            
        Returns:
            Decrypted seed phrase string
        """
        try:
            encrypted_seed = base64.urlsafe_b64decode(encrypted_data['encrypted_seed_phrase'])
            salt = base64.urlsafe_b64decode(encrypted_data['salt'])
            
            cipher = self._get_cipher(salt)
            decrypted_seed = cipher.decrypt(encrypted_seed)
            
            return decrypted_seed.decode()
            
        except Exception as e:
            raise Exception(f"Seed phrase decryption failed: {str(e)}")
    
    def generate_session_token(self, address: str) -> str:
        """Generate secure session token"""
        timestamp = str(int(__import__('time').time()))
        random_bytes = secrets.token_hex(16)
        
        # Create token from address, timestamp, and random data
        token_data = f"{address}_{timestamp}_{random_bytes}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return token_hash[:32]  # 32 character token
    
    def validate_private_key(self, private_key: str) -> Dict[str, any]:
        """
        Validate private key format and derive address
        
        Args:
            private_key: Private key to validate
            
        Returns:
            Dict with validation result and derived address
        """
        try:
            # Remove 0x prefix if present
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            # Check length (64 hex characters = 32 bytes)
            if len(private_key) != 64:
                return {
                    'valid': False,
                    'error': 'Private key must be 64 hex characters (32 bytes)'
                }
            
            # Check if valid hex
            try:
                int(private_key, 16)
            except ValueError:
                return {
                    'valid': False,
                    'error': 'Private key must contain only hex characters (0-9, a-f)'
                }
            
            # Derive address using eth_account
            from eth_account import Account
            account = Account.from_key('0x' + private_key)
            
            return {
                'valid': True,
                'address': account.address,
                'checksum_address': account.address
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Private key validation failed: {str(e)}'
            }
    
    def validate_seed_phrase(self, seed_phrase: str) -> Dict[str, any]:
        """
        Validate seed phrase format
        
        Args:
            seed_phrase: Seed phrase to validate
            
        Returns:
            Dict with validation result
        """
        try:
            words = seed_phrase.strip().split()
            
            if len(words) not in [12, 15, 18, 21, 24]:
                return {
                    'valid': False,
                    'error': 'Seed phrase must contain 12, 15, 18, 21, or 24 words'
                }
            
            # Basic word validation (in production, use BIP39 wordlist)
            for word in words:
                if not word.isalpha() or len(word) < 3:
                    return {
                        'valid': False,
                        'error': f'Invalid word in seed phrase: {word}'
                    }
            
            return {
                'valid': True,
                'word_count': len(words)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Seed phrase validation failed: {str(e)}'
            }
    
    def sanitize_session_data(self, session_data: Dict) -> Dict:
        """
        Remove sensitive data from session for logging/debugging
        
        Args:
            session_data: Session dictionary
            
        Returns:
            Sanitized session data
        """
        sanitized = session_data.copy()
        
        # Remove sensitive fields
        sensitive_fields = [
            'private_key', 'seed_phrase', 'encrypted_private_key', 
            'encrypted_seed_phrase', 'raw_credentials'
        ]
        
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '[REDACTED]'
        
        return sanitized

# Global security instance
wallet_security = WalletSecurity()

# Utility functions
def hash_address(address: str) -> str:
    """Create hash of address for session keys"""
    return hashlib.sha256(address.lower().encode()).hexdigest()[:16]

def generate_secure_session_id(address: str) -> str:
    """Generate secure session ID"""
    return wallet_security.generate_session_token(address)

def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    if not address or len(address) != 42 or not address.startswith('0x'):
        return False
    
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False

# Test function
if __name__ == "__main__":
    import json
    
    security = WalletSecurity()
    
    # Test private key encryption
    test_private_key = "0x1234567890123456789012345678901234567890123456789012345678901234"
    
    print("🔐 Testing Private Key Encryption...")
    encrypted = security.encrypt_private_key(test_private_key, "test_user")
    print(f"Encrypted: {json.dumps(encrypted, indent=2)}")
    
    decrypted = security.decrypt_private_key(encrypted)
    print(f"Decrypted: {decrypted}")
    print(f"Match: {decrypted == test_private_key}")
    
    # Test seed phrase encryption
    test_seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    
    print("\n🌱 Testing Seed Phrase Encryption...")
    encrypted_seed = security.encrypt_seed_phrase(test_seed, "test_user")
    print(f"Encrypted: {json.dumps(encrypted_seed, indent=2)}")
    
    decrypted_seed = security.decrypt_seed_phrase(encrypted_seed)
    print(f"Decrypted: {decrypted_seed}")
    print(f"Match: {decrypted_seed == test_seed}")
    
    # Test validation
    print("\n✅ Testing Validation...")
    pk_validation = security.validate_private_key(test_private_key)
    print(f"Private Key Validation: {json.dumps(pk_validation, indent=2)}")
    
    seed_validation = security.validate_seed_phrase(test_seed)
    print(f"Seed Phrase Validation: {json.dumps(seed_validation, indent=2)}")
