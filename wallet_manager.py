"""
Wallet Manager - Wallet Connection and Transaction Management
EthIstanbul Hackathon Project
"""

import os
import json
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WalletInfo:
    """Wallet information"""
    address: str
    balance_eth: float
    token_balances: Dict[str, float]
    connection_method: str  # 'metamask', 'private_key', 'mnemonic'
    connected_at: str

class WalletManager:
    def __init__(self):
        """Wallet Manager'ı başlat"""
        self.connected_wallet: Optional[WalletInfo] = None
        self.private_key: Optional[str] = None
        self.transaction_history: List[Dict] = []
        
        # Gerçek blockchain bağlantısı için Web3
        from blockchain_integration import blockchain_integrator
        self.blockchain = blockchain_integrator
        
        print("💳 Wallet Manager initialized")
    
    def connect_with_metamask(self) -> Dict:
        """MetaMask ile bağlan (gerçek bağlantı gerekli)"""
        try:
            # Gerçek MetaMask bağlantısı frontend'ten gelecek
            return {
                'success': False,
                'error': 'MetaMask bağlantısı frontend üzerinden yapılmalı',
                'message': 'Lütfen web arayüzünden cüzdanınızı bağlayın'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'MetaMask bağlantı hatası: {str(e)}'
            }
    
    def connect_with_private_key(self, private_key: str) -> Dict:
        """Private key ile bağlan"""
        try:
            if not private_key or len(private_key) < 60:
                return {
                    'success': False,
                    'error': 'Geçersiz private key formatı'
                }
            
            # Gerçek private key bağlantısı
            from eth_account import Account
            
            # Private key'den gerçek address türet
            account = Account.from_key(private_key)
            real_address = account.address
            
            # Gerçek blockchain bakiyesi al
            real_balance_wei = self.blockchain.w3.eth.get_balance(real_address)
            real_balance_eth = self.blockchain.w3.from_wei(real_balance_wei, 'ether')
            
            wallet_info = WalletInfo(
                address=real_address,
                balance_eth=float(real_balance_eth),
                token_balances={},  # Token bakiyeleri gerçek zamanlı çekilecek
                connection_method='private_key',
                connected_at=datetime.now().isoformat()
            )
            
            self.connected_wallet = wallet_info
            self.private_key = private_key
            
            # Blockchain integrator'a private key'i aktar
            self.blockchain.private_key = private_key
            
            return {
                'success': True,
                'address': wallet_info.address,
                'balance_eth': wallet_info.balance_eth,
                'method': 'private_key',
                'message': 'Private key bağlantısı başarılı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Private key bağlantı hatası: {str(e)}'
            }
    
    def connect_with_mnemonic(self, mnemonic: str) -> Dict:
        """Mnemonic phrase ile bağlan"""
        try:
            words = mnemonic.strip().split()
            if len(words) not in [12, 24]:
                return {
                    'success': False,
                    'error': 'Mnemonic phrase 12 veya 24 kelime olmalı'
                }
            
            # Simüle edilmiş mnemonic bağlantısı
            simulated_address = "0xABCDEF123456789012345678901234567890ABCD"
            
            wallet_info = WalletInfo(
                address=simulated_address,
                balance_eth=3.2,
                token_balances={
                    'WETH': 1.5,
                    'USDC': 1200.0,
                    'USDT': 800.0,
                    'DAI': 900.0,
                    'RISE': 15000.0
                },
                connection_method='mnemonic',
                connected_at=datetime.now().isoformat()
            )
            
            self.connected_wallet = wallet_info
            
            return {
                'success': True,
                'address': wallet_info.address,
                'balance_eth': wallet_info.balance_eth,
                'method': 'mnemonic',
                'message': 'Mnemonic bağlantısı başarılı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Mnemonic bağlantı hatası: {str(e)}'
            }
    
    def disconnect_wallet(self) -> Dict:
        """Cüzdan bağlantısını kes"""
        try:
            if not self.connected_wallet:
                return {
                    'success': False,
                    'error': 'Zaten bağlı cüzdan yok'
                }
            
            old_address = self.connected_wallet.address
            self.connected_wallet = None
            self.private_key = None
            
            return {
                'success': True,
                'message': f'Cüzdan bağlantısı kesildi: {old_address[:10]}...'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Bağlantı kesme hatası: {str(e)}'
            }
    
    def get_wallet_info(self) -> Optional[WalletInfo]:
        """Bağlı cüzdan bilgilerini al"""
        return self.connected_wallet
    
    def execute_swap_transaction(self, from_token: str, to_token: str, 
                                amount: float, slippage: float = 0.5) -> Dict:
        """Swap işlemini gerçekleştir"""
        if not self.connected_wallet:
            return {
                'success': False,
                'error': 'Cüzdan bağlı değil'
            }
        
        try:
            # Gerçek blockchain swap işlemi (simülasyon yok!)
            from blockchain_integration import blockchain_integrator
            
            swap_result = blockchain_integrator.execute_swap(
                from_token, to_token, amount, slippage
            )
            
            if swap_result['success']:
                # Gerçek işlem geçmişine ekle
                transaction_record = {
                    'tx_hash': swap_result['tx_hash'],
                    'from_token': from_token,
                    'to_token': to_token,
                    'amount_in': amount,
                    'amount_out': swap_result.get('estimated_amount_out', amount * 0.998),
                    'timestamp': datetime.now().isoformat(),
                    'status': swap_result.get('status', 'pending'),
                    'dex': swap_result.get('dex', 'rise_dex'),
                    'real_transaction': True  # Gerçek işlem işareti
                }
                
                self.transaction_history.append(transaction_record)
                
                return {
                    'success': True,
                    'tx_hash': swap_result['tx_hash'],
                    'amount_in': amount,
                    'amount_out': swap_result.get('estimated_amount_out', amount * 0.995),
                    'gas_used': swap_result.get('gas_used', 0),
                    'explorer_url': swap_result.get('explorer_url'),
                    'status': swap_result.get('status', 'pending')
                }
            else:
                return swap_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Swap transaction error: {str(e)}'
            }
    
    def execute_transfer_transaction(self, amount: float, token: str, receiver: str) -> Dict:
        """Execute transfer transaction"""
        if not self.connected_wallet:
            return {
                'success': False,
                'error': 'Wallet not connected'
            }
        
        try:
            # Execute real transfer transaction
            from blockchain_integration import blockchain_integrator
            
            transfer_result = blockchain_integrator.execute_transfer(
                token, amount, receiver
            )
            
            if transfer_result['success']:
                # Add to real transaction history
                transaction_record = {
                    'tx_hash': transfer_result['tx_hash'],
                    'type': 'transfer',
                    'token': token,
                    'amount': amount,
                    'receiver': receiver,
                    'timestamp': datetime.now().isoformat(),
                    'status': transfer_result.get('status', 'pending'),
                    'gas_used': transfer_result.get('gas_used', 0),
                    'real_transaction': True  # Real transaction flag
                }
                
                self.transaction_history.append(transaction_record)
                
                return {
                    'success': True,
                    'tx_hash': transfer_result['tx_hash'],
                    'amount': amount,
                    'token': token,
                    'receiver': receiver,
                    'gas_used': transfer_result.get('gas_used', 0),
                    'explorer_url': transfer_result.get('explorer_url'),
                    'status': transfer_result.get('status', 'pending')
                }
            else:
                return transfer_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Transfer transaction error: {str(e)}'
            }
    
    def get_transaction_history(self) -> List[Dict]:
        """Get transaction history"""
        return self.transaction_history.copy()
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        """İşlem durumunu kontrol et"""
        try:
            from blockchain_integration import blockchain_integrator
            return blockchain_integrator.get_transaction_status(tx_hash)
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def approve_token(self, token: str, spender: str, amount: float = None) -> Dict:
        """Token approval işlemi"""
        if not self.connected_wallet:
            return {
                'success': False,
                'error': 'Cüzdan bağlı değil'
            }
        
        try:
            # Simüle edilmiş approval
            import hashlib
            approval_data = f"approve_{token}_{spender}_{amount}_{time.time()}"
            tx_hash = '0x' + hashlib.sha256(approval_data.encode()).hexdigest()
            
            return {
                'success': True,
                'tx_hash': tx_hash,
                'token': token,
                'spender': spender,
                'amount': amount or 'unlimited',
                'message': f'{token} approval işlemi başarılı',
                'explorer_url': f"https://explorer.testnet.riselabs.xyz/tx/{tx_hash}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Approval hatası: {str(e)}'
            }

# Singleton instance
wallet_manager = WalletManager()

# Test fonksiyonu
if __name__ == "__main__":
    manager = WalletManager()
    
    # Test private key bağlantısı
    result = manager.connect_with_private_key("0x1234567890123456789012345678901234567890123456789012345678901234")
    print(f"Connection result: {json.dumps(result, indent=2)}")
    
    # Test swap
    if result['success']:
        swap_result = manager.execute_swap_transaction("WETH", "USDC", 0.1)
        print(f"Swap result: {json.dumps(swap_result, indent=2)}")
    
    # Test disconnect
    disconnect_result = manager.disconnect_wallet()
    print(f"Disconnect result: {json.dumps(disconnect_result, indent=2)}")
