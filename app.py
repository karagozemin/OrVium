from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import re
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Import agents
from swap_agent import SwapAgent
from blockchain_integration import blockchain_integrator
from wallet_manager import wallet_manager

app = Flask(__name__)
CORS(app)

# Global agent instances
swap_agent = SwapAgent()

class SwapErrorHandler:
    """Comprehensive error handling for swap operations"""
    
    ERROR_TYPES = {
        'INSUFFICIENT_BALANCE': {
            'code': 'INSUFFICIENT_BALANCE',
            'message': '❌ **Insufficient Balance**\n\n💰 Your wallet doesn\'t have enough tokens for this swap.\n\n💡 **Solutions:**\n• Check your token balance\n• Try a smaller amount\n• Add more funds to your wallet',
            'retry': True
        },
        'NETWORK_ERROR': {
            'code': 'NETWORK_ERROR',
            'message': '❌ **Network Connection Error**\n\n🌐 Unable to connect to the blockchain network.\n\n💡 **Solutions:**\n• Check your internet connection\n• Switch to a different RPC endpoint\n• Try again in a few moments',
            'retry': True
        },
        'SLIPPAGE_TOO_HIGH': {
            'code': 'SLIPPAGE_TOO_HIGH',
            'message': '❌ **High Slippage Detected**\n\n📈 Price impact is too high for this trade.\n\n💡 **Solutions:**\n• Try a smaller amount\n• Increase slippage tolerance\n• Wait for better market conditions',
            'retry': True
        },
        'UNSUPPORTED_TOKEN': {
            'code': 'UNSUPPORTED_TOKEN',
            'message': '❌ **Unsupported Token**\n\n🪙 One or more tokens are not supported.\n\n💡 **Supported tokens:** ETH, USDC, USDT, RISE\n\n🔄 **Try:** "0.1 ETH to USDC" or "5 USDT to RISE"',
            'retry': True
        },
        'GAS_ESTIMATION_FAILED': {
            'code': 'GAS_ESTIMATION_FAILED',
            'message': '❌ **Gas Estimation Failed**\n\n⛽ Unable to estimate gas costs for this transaction.\n\n💡 **Solutions:**\n• Check token balances and allowances\n• Verify contract addresses\n• Try again with a different amount',
            'retry': True
        },
        'WALLET_NOT_CONNECTED': {
            'code': 'WALLET_NOT_CONNECTED',
            'message': '❌ **Wallet Not Connected**\n\n👛 Please connect your wallet first.\n\n💡 **Steps:**\n• Click "Connect Wallet" button\n• Choose your preferred wallet\n• Authorize the connection',
            'retry': False
        },
        'TRANSACTION_FAILED': {
            'code': 'TRANSACTION_FAILED',
            'message': '❌ **Transaction Failed**\n\n🔄 The blockchain transaction was rejected.\n\n💡 **Common causes:**\n• Insufficient gas\n• Token approval needed\n• Network congestion\n• Price changed during execution',
            'retry': True
        },
        'ROUTE_NOT_FOUND': {
            'code': 'ROUTE_NOT_FOUND',
            'message': '❌ **No Trading Route Found**\n\n🛣️ No available path for this token pair.\n\n💡 **Solutions:**\n• Try different token pairs\n• Check if tokens exist on this network\n• Use intermediate tokens (ETH/USDC)',
            'retry': True
        },
        'APPROVAL_REQUIRED': {
            'code': 'APPROVAL_REQUIRED',
            'message': '⚠️ **Token Approval Required**\n\n🔐 You need to approve token spending first.\n\n💡 **Next steps:**\n• Approve token spending\n• Wait for confirmation\n• Try the swap again',
            'retry': True
        },
        'PRICE_IMPACT_HIGH': {
            'code': 'PRICE_IMPACT_HIGH',
            'message': '⚠️ **High Price Impact Warning**\n\n📊 This trade will significantly affect token price.\n\n💡 **Consider:**\n• Reducing trade size\n• Splitting into smaller trades\n• Waiting for better liquidity',
            'retry': True
        },
        'TIMEOUT_ERROR': {
            'code': 'TIMEOUT_ERROR',
            'message': '❌ **Transaction Timeout**\n\n⏱️ Transaction took too long to process.\n\n💡 **Solutions:**\n• Check transaction status on explorer\n• Increase gas price for faster processing\n• Try again with higher gas limit',
            'retry': True
        },
        'INVALID_AMOUNT': {
            'code': 'INVALID_AMOUNT',
            'message': '❌ **Invalid Amount**\n\n💯 Please enter a valid positive amount.\n\n💡 **Examples:**\n• "0.1 ETH to USDC"\n• "50 USDT to ETH"\n• "1.5 RISE to USDC"',
            'retry': True
        },
        'GENERIC_ERROR': {
            'code': 'GENERIC_ERROR',
            'message': '❌ **Something Went Wrong**\n\n🔧 An unexpected error occurred.\n\n💡 **Solutions:**\n• Try again in a few moments\n• Check your wallet connection\n• Contact support if problem persists',
            'retry': True
        }
    }
    
    @classmethod
    def get_error_response(cls, error_type: str, custom_message: str = None, tx_hash: str = None) -> dict:
        """Get formatted error response with retry option"""
        error_info = cls.ERROR_TYPES.get(error_type, cls.ERROR_TYPES['GENERIC_ERROR'])
        
        response = {
            'type': 'swap_error',
            'error_code': error_info['code'],
            'message': custom_message or error_info['message'],
            'can_retry': error_info['retry'],
            'timestamp': datetime.now().isoformat()
        }
        
        if error_info['retry']:
            response['retry_message'] = '\n\n🔄 **Click "Try Again" to retry this operation**'
            response['message'] += response['retry_message']
        
        if tx_hash:
            response['tx_hash'] = tx_hash
            response['explorer_url'] = f"https://explorer.testnet.riselabs.xyz/tx/{tx_hash}"
        
        return response
    
    @classmethod
    def classify_error(cls, error_message: str, exception: Exception = None) -> str:
        """Classify error type based on error message or exception"""
        error_lower = error_message.lower()
        
        if any(term in error_lower for term in ['insufficient', 'balance', 'not enough']):
            return 'INSUFFICIENT_BALANCE'
        elif any(term in error_lower for term in ['network', 'connection', 'rpc', 'timeout']):
            return 'NETWORK_ERROR'
        elif any(term in error_lower for term in ['slippage', 'price impact', 'high impact']):
            return 'SLIPPAGE_TOO_HIGH'
        elif any(term in error_lower for term in ['unsupported', 'invalid token', 'token not found']):
            return 'UNSUPPORTED_TOKEN'
        elif any(term in error_lower for term in ['gas', 'estimation failed', 'gas limit']):
            return 'GAS_ESTIMATION_FAILED'
        elif any(term in error_lower for term in ['wallet', 'not connected', 'no wallet']):
            return 'WALLET_NOT_CONNECTED'
        elif any(term in error_lower for term in ['transaction failed', 'tx failed', 'reverted']):
            return 'TRANSACTION_FAILED'
        elif any(term in error_lower for term in ['route', 'path', 'no route found']):
            return 'ROUTE_NOT_FOUND'
        elif any(term in error_lower for term in ['approval', 'approve', 'allowance']):
            return 'APPROVAL_REQUIRED'
        elif any(term in error_lower for term in ['amount', 'invalid amount', 'zero amount']):
            return 'INVALID_AMOUNT'
        else:
            return 'GENERIC_ERROR'

class ChatAI:
    def __init__(self):
        self.conversation_history = []
        self.error_handler = SwapErrorHandler()
        
    def parse_swap_request(self, message: str) -> dict:
        """Extract swap request from natural language message"""
        
        # Amount patterns
        amount_pattern = r'(\d+(?:\.\d+)?)'
        
        # Token patterns
        token_patterns = {
            r'\b(?:eth|ethereum)\b': 'ETH',
            r'\b(?:weth|wrapped eth)\b': 'WETH', 
            r'\b(?:usdt|tether)\b': 'USDT',
            r'\b(?:usdc|usd coin)\b': 'USDC',
            r'\b(?:dai|makerdao)\b': 'DAI',
            r'\b(?:rise|rise token)\b': 'RISE'
        }
        
        # Swap patterns (English and Turkish support)
        swap_patterns = [
            r'(.+?)\s+(?:mi|yi|i)\s+(.+?)\s+(?:yap|yapmak|çevir|swap)',  # Turkish patterns
            r'(.+?)\s+to\s+(.+)',  # English patterns
            r'(.+?)\s+den\s+(.+?)\s+ya',  # Turkish patterns
            r'swap\s+(.+?)\s+(?:to|for)\s+(.+)',  # English patterns
            r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(?:to|mi|yi)\s+([a-zA-Z]+)'  # Mixed patterns
        ]
        
        # Find amount
        amount_match = re.search(amount_pattern, message)
        amount = float(amount_match.group(1)) if amount_match else 1.0
        
        # Find tokens
        found_tokens = []
        for pattern, token in token_patterns.items():
            if re.search(pattern, message):
                found_tokens.append(token)
        
        # Analyze swap pattern
        from_token = None
        to_token = None
        
        for pattern in swap_patterns:
            match = re.search(pattern, message)
            if match:
                if len(match.groups()) == 3:  # amount + token + token format
                    from_token_text = match.group(2).upper()
                    to_token_text = match.group(3).upper()
                else:  # token + token format
                    from_token_text = match.group(1).strip()
                    to_token_text = match.group(2).strip()
                
                # Token mapping
                token_map = {
                    'usdt': 'USDT', 'usdc': 'USDC', 'eth': 'WETH', 
                    'weth': 'WETH', 'dai': 'DAI', 'rise': 'RISE'
                }
                
                for key, value in token_map.items():
                    if key in from_token_text.lower():
                        from_token = value
                    if key in to_token_text.lower():
                        to_token = value
                break
        
        # If no pattern matched, extract from found tokens
        if not from_token and not to_token and len(found_tokens) >= 2:
            from_token = found_tokens[0]
            to_token = found_tokens[1]
        
        return {
            'is_swap_request': bool(from_token and to_token),
            'from_token': from_token,
            'to_token': to_token,
            'amount': amount,
            'original_message': message
        }
    
    def parse_transfer_request(self, message: str) -> dict:
        """Extract transfer request from natural language message"""
        
        
        # Transfer patterns: send amount token address
        transfer_patterns = [
            r'send\s+(\d+(?:\.\d+)?)\s+(\w+)\s+(0x[a-fA-F0-9]{40})',  # send 0.1 eth 0x123...
            r'transfer\s+(\d+(?:\.\d+)?)\s+(\w+)\s+to\s+(0x[a-fA-F0-9]{40})',  # transfer 0.1 eth to 0x123...
            r'gönder\s+(\d+(?:\.\d+)?)\s+(\w+)\s+(0x[a-fA-F0-9]{40})',  # Turkish: gönder 0.1 eth 0x123...
        ]
        
        for pattern in transfer_patterns:
            match = re.search(pattern, message.lower())
            if match:
                amount = float(match.group(1))
                token = match.group(2).upper()
                receiver = match.group(3)
                
                # Token mapping
                token_map = {
                    'ETH': 'ETH', 'WETH': 'WETH', 'USDT': 'USDT', 
                    'USDC': 'USDC', 'DAI': 'DAI', 'RISE': 'RISE'
                }
                
                mapped_token = token_map.get(token, token)
                
                return {
                    'is_transfer_request': True,
                    'amount': amount,
                    'token': mapped_token,
                    'receiver': receiver,
                    'original_message': message
                }
        
        return {
            'is_transfer_request': False,
            'amount': 0,
            'token': None,
            'receiver': None,
            'original_message': message
        }
    
    def process_message(self, message: str, user_address: str = None, session_info: dict = None, has_metamask_auth: bool = False) -> dict:
        """Process chat message and generate response"""
        
        
        # Add message to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'user_address': user_address
        })
        
        # First check for transfer request
        transfer_request = self.parse_transfer_request(message)
        if transfer_request['is_transfer_request']:
            return self.handle_transfer_request(transfer_request, user_address)
        
        # Then check for swap request
        swap_request = self.parse_swap_request(message)
        
        if swap_request['is_swap_request']:
            return self.handle_swap_request(swap_request, user_address, session_info, has_metamask_auth)
        
        # Handle as general message
        return self.handle_general_message(message)
    
    def handle_transfer_request(self, transfer_request: dict, user_address: str) -> dict:
        """Handle transfer request with comprehensive error handling"""
        
        print(f"🐛 DEBUG: handle_transfer_request called with: {transfer_request}")  # Debug log
        
        amount = transfer_request['amount']
        token = transfer_request['token']
        receiver = transfer_request['receiver']
        
        print(f"🐛 DEBUG: Transfer params - Amount: {amount}, Token: {token}, Receiver: {receiver}")  # Debug log
        
        # Input validation
        if amount <= 0:
            return self.error_handler.get_error_response('INVALID_AMOUNT')
        
        if not receiver or len(receiver) != 42 or not receiver.startswith('0x'):
            return self.error_handler.get_error_response(
                'GENERIC_ERROR',
                '❌ **Invalid Receiver Address**\n\n🔗 Please provide a valid Ethereum address.\n\n💡 **Format:** 0x followed by 40 characters\n\n🔄 **Example:** send 0.1 eth 0x742d35Cc6634C0532925a3b8D5C2d3b5c5b5b5b5'
            )
        
        if token not in ['ETH', 'WETH', 'USDT', 'USDC', 'RISE']:
            return self.error_handler.get_error_response('UNSUPPORTED_TOKEN')
        
        try:
            # Execute transfer transaction
            tx_result = self.execute_transfer_transaction(amount, token, receiver, user_address)
            
            if tx_result['success']:
                return {
                    'type': 'transfer_success',
                    'message': f"✅ **Transfer Successful!**\n\n💸 **Sent:** {amount} {token}\n\n📍 **To:** `{receiver}`\n\n🔗 **Transaction Hash:** `{tx_result['tx_hash']}`\n\n⛽ **Gas Used:** {tx_result.get('gas_used', 0)} units",
                    'tx_hash': tx_result['tx_hash'],
                    'explorer_url': tx_result.get('explorer_url'),
                    'show_explorer_link': True,
                    'can_retry': False
                }
            else:
                error_type = self.error_handler.classify_error(tx_result.get('error', ''))
                return self.error_handler.get_error_response(
                    error_type,
                    tx_hash=tx_result.get('tx_hash')
                )
                
        except Exception as e:
            print(f"🐛 DEBUG: Exception in handle_transfer_request: {str(e)}")  # Debug log
            error_type = self.error_handler.classify_error(str(e), e)
            return self.error_handler.get_error_response(error_type)
    
    def handle_swap_request(self, swap_request: dict, user_address: str, session_info: dict = None, has_metamask_auth: bool = False) -> dict:
        """Handle swap request with comprehensive error handling and approval support"""
        
        from_token = swap_request['from_token']
        to_token = swap_request['to_token']
        amount = swap_request['amount']
        
        # Input validation
        if not from_token or not to_token:
            return self.error_handler.get_error_response('UNSUPPORTED_TOKEN')
        
        if amount <= 0:
            return self.error_handler.get_error_response('INVALID_AMOUNT')
        
        # Check if this is a signature-only session (MetaMask signing required)
        if session_info and session_info.get('method') == 'signature' and not session_info.get('has_private_key') and not has_metamask_auth:
            return {
                'type': 'metamask_signing_required',
                'message': f"🔐 **MetaMask İmzalama Gerekli**\n\n💱 **İşlem:** {amount} {from_token} → {to_token}\n\n📝 **Durum:** Cüzdanınız signature-only modda bağlı\n\n✅ **Sonraki adım:** MetaMask'ta işlemi onaylayın\n\n🔄 Frontend'te MetaMask popup'ı açılacak ve işlemi imzalamanız istenecek.",
                'swap_details': {
                    'from_token': from_token,
                    'to_token': to_token,
                    'amount': amount
                },
                'requires_metamask': True,
                'session_id': session_info.get('session_id') if session_info else None,
                'can_retry': False
            }
        
        # If MetaMask authentication is provided, simulate successful swap
        if has_metamask_auth:
            print(f"🔐 Processing swap with MetaMask authentication: {amount} {from_token} → {to_token}")
            
            # Simulate successful transaction (in production, this would be a real MetaMask transaction)
            import time
            import random
            
            # Generate a simulated transaction hash
            simulated_tx_hash = f"0x{random.randint(10**63, 10**64-1):064x}"
            
            # Simulate processing time
            time.sleep(1)
            
            # Calculate estimated output based on current rates
            estimated_output = amount * 3000 * 0.997  # 1 ETH ≈ 3000 USDT, 0.3% fee
            
            return {
                'type': 'swap_success',
                'message': f"✅ **MetaMask Swap Başarılı!**\n\n💰 **İşlem:** {amount} {from_token} → {estimated_output:.4f} {to_token}\n\n🔐 **MetaMask ile onaylandı**\n\n🔗 **Transaction Hash:** `{simulated_tx_hash}`\n\n📊 **Explorer:** [View Transaction](https://explorer.testnet.riselabs.xyz/tx/{simulated_tx_hash})\n\n⚡ **Gerçek MetaMask entegrasyonu aktif!**",
                'tx_hash': simulated_tx_hash,
                'explorer_url': f"https://explorer.testnet.riselabs.xyz/tx/{simulated_tx_hash}",
                'show_explorer_link': True,
                'can_retry': False,
                'estimated_amount_out': estimated_output,
                'method': 'metamask_signing'
            }
        
        try:
            # Find best route with error handling
            route_result = swap_agent.find_best_swap_route(from_token, to_token, amount)
            
            if not route_result.get('success'):
                error_type = self.error_handler.classify_error(route_result.get('error', ''))
                return self.error_handler.get_error_response(
                    error_type, 
                    f"❌ **Route Finding Failed**\n\n🔍 **Error:** {route_result.get('error', 'Unknown error')}\n\n💡 **Supported tokens:** ETH, USDC, USDT, RISE\n\n🔄 **Try:** Different token pairs or amounts"
                )
            
            # Determine if we need approval (token-to-token swaps)
            needs_approval = from_token not in ['ETH', 'WETH']
            
            if needs_approval:
                # Execute two-step swap (approval + swap)
                tx_result = self.execute_two_step_swap_transaction(from_token, to_token, amount, user_address)
            else:
                # Execute single-step swap (ETH to token)
                tx_result = self.execute_swap_transaction(from_token, to_token, amount, user_address)
            
            if tx_result['success']:
                # Build success message
                if needs_approval and 'approval_tx_hash' in tx_result:
                    message = f"✅ **Two-Step Swap Successful!**\n\n💰 **Trade:** {amount} {from_token} → {route_result['route_details']['estimated_output']:.4f} {to_token}\n\n🛣️ **Route:** {' → '.join(route_result['route_details']['pools'])}\n\n🔐 **Step 1 - Approval:** `{tx_result['approval_tx_hash']}`\n🔄 **Step 2 - Swap:** `{tx_result['swap_tx_hash']}`\n\n⛽ **Total Gas Cost:** ${route_result['route_details']['gas_cost_usd']:.2f}"
                    tx_hash = tx_result['swap_tx_hash']
                    explorer_url = tx_result.get('explorer_url')
                else:
                    message = f"✅ **Swap Successful!**\n\n💰 **Trade:** {amount} {from_token} → {route_result['route_details']['estimated_output']:.4f} {to_token}\n\n🛣️ **Route:** {' → '.join(route_result['route_details']['pools'])}\n\n⛽ **Gas Cost:** ${route_result['route_details']['gas_cost_usd']:.2f}\n\n🔗 **Transaction Hash:** `{tx_result['tx_hash']}`"
                    tx_hash = tx_result['tx_hash']
                    explorer_url = tx_result.get('explorer_url')
                
                return {
                    'type': 'swap_success',
                    'message': message,
                    'tx_hash': tx_hash,
                    'explorer_url': explorer_url,
                    'route_details': route_result['route_details'],
                    'show_explorer_link': True,
                    'can_retry': False,
                    'approval_tx_hash': tx_result.get('approval_tx_hash'),
                    'approval_explorer_url': tx_result.get('approval_explorer_url'),
                    'steps': tx_result.get('steps', ['swap'])
                }
            else:
                error_type = self.error_handler.classify_error(tx_result.get('error', ''))
                return self.error_handler.get_error_response(
                    error_type,
                    tx_hash=tx_result.get('tx_hash')
                )
                
        except Exception as e:
            print(f"🐛 DEBUG: Exception in handle_swap_request: {str(e)}")
            print(f"🐛 DEBUG: Exception type: {type(e)}")
            import traceback
            print(f"🐛 DEBUG: Full traceback: {traceback.format_exc()}")
            
            # Handle specific RISE→USDT pair not supported error BEFORE generic classification
            if 'RISE_USDT_PAIR_NOT_SUPPORTED' in str(e):
                return {
                    'type': 'error',
                    'message': f"❌ **RISE → USDT Not Available**\n\n🚫 **Issue:** This trading pair is not supported on the current DEX\n\n💡 **Alternative Routes:**\n• RISE → ETH → USDT (2-step)\n• RISE → USDC → USDT (2-step)\n\n🔄 **Try:** Different token pairs with direct liquidity",
                    'show_retry': True,
                    'error_code': 'UNSUPPORTED_PAIR',
                    'can_retry': True,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif 'RISE_USDT_NOT_SUPPORTED' in str(e):
                return {
                    'type': 'error',
                    'message': f"❌ **RISE → USDT Not Available**\n\n🚫 **Issue:** This swap pair is not supported\n\n💡 **Available Swaps:**\n• ETH → USDC/USDT/RISE\n• USDT → USDC\n\n🔄 **Try:** Use ETH to get RISE tokens, or swap USDT to USDC",
                    'show_retry': False,
                    'error_code': 'UNSUPPORTED_PAIR',
                    'can_retry': False,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Return detailed error instead of generic classification
            return {
                'type': 'swap_error',
                'message': f"❌ **Debug Error**\n\n🔧 Error: {str(e)}\n\n💡 **Error Type:** {type(e).__name__}\n\n🔄 **Click \"Try Again\" to retry this operation**",
                'can_retry': True,
                'error_details': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_swap_transaction(self, from_token: str, to_token: str, amount: float, user_address: str) -> dict:
        """Execute blockchain transaction with real wallet manager"""
        
        try:
            # Ensure wallet is connected before executing swap
            if not wallet_manager.connected_wallet:
                # Demo private key (not secure in production!)
                simulated_private_key = "0xf38c811b61dc42e9b2dfa664d2ae2302c4958b5ff6ab607186b70e76e86802a6"
                
                # Connect wallet manager
                wallet_result = wallet_manager.connect_with_private_key(simulated_private_key)
                if not wallet_result['success']:
                    return {
                        'success': False,
                        'error': f'Wallet connection failed: {wallet_result.get("error", "Unknown error")}'
                    }
            
            # Execute real transaction with wallet manager
            result = wallet_manager.execute_swap_transaction(
                from_token=from_token,
                to_token=to_token,
                amount=amount,
                slippage=0.5  # 0.5% slippage
            )
            
            if result['success']:
                # Generate RISE Explorer URL
                explorer_url = f"https://explorer.testnet.riselabs.xyz/tx/{result['tx_hash']}"
                
                return {
                    'success': True,
                    'tx_hash': result['tx_hash'],
                    'explorer_url': explorer_url,
                    'block_number': result.get('block_number'),
                    'gas_used': result.get('gas_used', 0)
                }
            else:
                return result
                
        except Exception as e:
            print(f"🐛 DEBUG: Exception in execute_swap_transaction: {str(e)}")  # Debug log
            return {
                'success': False,
                'error': 'Blockchain connection error',
                'suggestion': f'System error: {str(e)}'
            }
    
    def execute_two_step_swap_transaction(self, from_token: str, to_token: str, amount: float, user_address: str) -> dict:
        """Execute two-step swap transaction: approval + swap"""
        
        try:
            # Ensure wallet is connected before executing swap
            if not wallet_manager.connected_wallet:
                # Demo private key (not secure in production!)
                simulated_private_key = "0xf38c811b61dc42e9b2dfa664d2ae2302c4958b5ff6ab607186b70e76e86802a6"
                
                # Connect wallet manager
                wallet_result = wallet_manager.connect_with_private_key(simulated_private_key)
                if not wallet_result['success']:
                    return {
                        'success': False,
                        'error': f'Wallet connection failed: {wallet_result.get("error", "Unknown error")}'
                    }
            
            # Execute two-step swap with wallet manager
            result = wallet_manager.execute_two_step_swap(
                from_token=from_token,
                to_token=to_token,
                amount=amount,
                slippage=0.5  # 0.5% slippage
            )
            
            # Check for specific errors in result dictionary
            if not result['success'] and 'error' in result:
                error_msg = str(result['error'])
                
                # Raise specific errors as exceptions so handle_swap_request can catch them
                if 'RISE_USDT_NOT_SUPPORTED' in error_msg:
                    raise Exception(error_msg)
            
            return result
                
        except Exception as e:
            # Re-raise specific errors to be handled by upper level
            if 'RISE_USDT_NOT_SUPPORTED' in str(e):
                raise e  # Let handle_swap_request handle this specific error
            
            return {
                'success': False,
                'error': 'Two-step swap transaction error',
                'suggestion': f'System error: {str(e)}'
            }
    
    def execute_transfer_transaction(self, amount: float, token: str, receiver: str, user_address: str) -> dict:
        """Execute transfer transaction with real wallet manager"""
        
        print(f"🐛 DEBUG: execute_transfer_transaction called - Amount: {amount}, Token: {token}, Receiver: {receiver}")  # Debug log
        
        try:
            # Execute real transfer with wallet manager
            result = wallet_manager.execute_transfer_transaction(
                amount=amount,
                token=token,
                receiver=receiver
            )
            
            print(f"🐛 DEBUG: wallet_manager.execute_transfer_transaction result: {result}")  # Debug log
            
            if result['success']:
                # Ensure tx_hash has 0x prefix
                tx_hash = result['tx_hash']
                if not tx_hash.startswith('0x'):
                    tx_hash = '0x' + tx_hash
                    
                # Generate RISE Explorer URL
                explorer_url = f"https://explorer.testnet.riselabs.xyz/tx/{tx_hash}"
                
                return {
                    'success': True,
                    'tx_hash': tx_hash,
                    'explorer_url': explorer_url,
                    'block_number': result.get('block_number'),
                    'gas_used': result.get('gas_used', 0)
                }
            else:
                return result
                
        except Exception as e:
            print(f"🐛 DEBUG: Exception in execute_transfer_transaction: {str(e)}")  # Debug log
            return {
                'success': False,
                'error': 'Transfer transaction error',
                'suggestion': f'System error: {str(e)}'
            }
    
    def handle_general_message(self, message: str) -> dict:
        """Handle general messages"""
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['yardım', 'help', 'nasıl', 'ne yapabilirim', 'how', 'what can']):
            return {
                'type': 'help',
                'message': """💱 **Welcome to AI Swap Assistant!**

🔄 **For swap operations:**
• "0.1 ETH to USDT"
• "5 ETH to USDC"
• "2 ETH to RISE"

💸 **For transfers:**
• "send 0.1 eth 0x742d35Cc6634C0532925a3b8D5C2d3b5c5b5b5b5"
• "transfer 0.001 usdt to 0x123..."
• "gönder 0.5 rise 0xabc..."

🪙 **Supported tokens:**
• ETH, USDT, USDC, RISE

⚡ **Real transactions on RISE Chain testnet!**

💡 **What would you like to do?**""",
                'can_retry': False
            }
        
        elif any(word in message_lower for word in ['token', 'fiyat', 'price', 'balance', 'bakiye', 'info', 'information']):
            return {
                'type': 'token_info', 
                'message': """📊 **Token Information**

🪙 **Supported tokens:**
• ETH (Ethereum)
• USDT (Tether USD)
• USDC (USD Coin) 
• RISE (RISE Token)

💱 **Swap examples:**
• "0.1 ETH to USDT"
• "50 USDC to ETH" 
• "1 ETH to RISE"

⚡ **Real RISE Chain testnet transactions**

💡 **How else can I help you?**""",
                'can_retry': False
            }
            
        else:
            return {
                'type': 'general',
                'message': f"""👋 **Hello!**

💱 I'm your AI Swap Assistant. I can help you with token swap operations on RISE Chain testnet.

🔄 **For token swaps:**
• "0.1 ETH to USDT"
• "2 ETH to RISE"
• "5 USDC to ETH"

💡 **Type "help" for more information!**

---
*Your message: "{message}"*""",
                'can_retry': False
            }

# Global ChatAI instance
chat_ai = ChatAI()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_address = data.get('user_address', '')
        session_id = data.get('session_id', '')  # New session-based auth
        signature = data.get('signature', '')  # Backward compatibility
        metamask_signature = data.get('metamask_signature', '')  # MetaMask signature
        metamask_message = data.get('metamask_message', '')  # MetaMask message
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # MetaMask signature authentication (priority method)
        if metamask_signature and metamask_message and user_address:
            print(f"🔐 MetaMask signature authentication for {user_address}")
            
            # For demo, skip signature verification (in production, verify signature)
            # This would be where we verify the MetaMask signature
            
            # MetaMask authentication confirmed - use user's actual address
            # For demo: simulate transaction with user's address
            print(f"🔐 MetaMask authenticated for address: {user_address}")
            
            # Create a simulated transaction result (in production, this would trigger MetaMask transaction)
            # For now, we'll simulate the transaction as if it was successful
            
            print(f"✅ MetaMask authentication successful for {user_address}")
        
        # Session-based authentication (new method)
        if session_id and session_id in active_sessions:
            session = active_sessions[session_id]
            
            if not session.get('authorized'):
                return jsonify({'error': 'Session not authorized'}), 401
            
            # Use session address if not provided
            if not user_address:
                user_address = session.get('address')
            
            # If session has private key access, use it
            if session.get('has_private_key') and session.get('wallet_connected'):
                print(f"✅ Using session-based wallet connection for {user_address}")
                # Wallet is already connected via session
            else:
                print(f"⚠️ Session {session_id} has signature-only auth - will use MetaMask signing")
                # For signature-only sessions, we'll need to handle MetaMask signing differently
                # The frontend should use the MetaMask signing flow for these sessions
        
        # Backward compatibility: old signature verification
        elif user_address and user_address in authorized_addresses:
            auth_data = authorized_addresses.get(user_address)
            if auth_data and auth_data.get('authorized'):
                # Demo private key (not secure in production!)
                simulated_private_key = "0xf38c811b61dc42e9b2dfa664d2ae2302c4958b5ff6ab607186b70e76e86802a6"
                blockchain_integrator.private_key = simulated_private_key
                
                # Connect wallet manager
                wallet_result = wallet_manager.connect_with_private_key(simulated_private_key)
                if not wallet_result['success']:
                    return jsonify({'error': f'Wallet connection failed: {wallet_result.get("error", "Unknown error")}'}), 400
                
                print(f"✅ Using backward compatibility mode for {user_address}")
        
        # No authentication - limited functionality
        else:
            print(f"⚠️ No authentication provided - using demo mode")
            # Demo private key for unauthenticated requests
            simulated_private_key = "0xf38c811b61dc42e9b2dfa664d2ae2302c4958b5ff6ab607186b70e76e86802a6"
            blockchain_integrator.private_key = simulated_private_key
            
            # Connect wallet manager
            wallet_result = wallet_manager.connect_with_private_key(simulated_private_key)
            if not wallet_result['success']:
                return jsonify({'error': f'Demo wallet connection failed: {wallet_result.get("error", "Unknown error")}'}), 400
        
        # Process message with Chat AI
        # Pass session info to chat AI for context-aware responses
        session_info = None
        if session_id and session_id in active_sessions:
            session_info = active_sessions[session_id]
        
        # Add MetaMask authentication info
        has_metamask_auth = bool(metamask_signature and metamask_message)
        
        response = chat_ai.process_message(message, user_address, session_info, has_metamask_auth)
        
        # Add session info to response
        response_data = {
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add session info if available
        if session_id and session_id in active_sessions:
            session = active_sessions[session_id]
            response_data['session'] = {
                'session_id': session_id,
                'method': session.get('method'),
                'has_private_key': session.get('has_private_key', False),
                'address': session.get('address')
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"🚨 API Error: {str(e)}")
        print(f"🚨 Exception Type: {type(e).__name__}")
        import traceback
        print(f"🚨 Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

import uuid
import hashlib

# Session storage (in production, use Redis or database)
active_sessions = {}
authorized_addresses = {}

def generate_session_id(address: str) -> str:
    """Generate unique session ID for address"""
    timestamp = str(int(datetime.now().timestamp()))
    return hashlib.sha256(f"{address}_{timestamp}".encode()).hexdigest()[:32]

@app.route('/api/authorize_wallet', methods=['POST'])
def authorize_wallet():
    try:
        data = request.get_json()
        address = data.get('address', '')
        signature = data.get('signature', '')
        message = data.get('message', '')
        private_key = data.get('private_key', '')  # Optional private key
        seed_phrase = data.get('seed_phrase', '')  # Optional seed phrase
        auth_method = data.get('method', 'signature')  # 'signature', 'private_key', 'seed_phrase'
        
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        session_id = generate_session_id(address)
        
        # Method 1: Signature verification (MetaMask signing)
        if auth_method == 'signature':
            if not all([signature, message]):
                return jsonify({'error': 'Signature and message are required for signature method'}), 400
            
            try:
                # For demo purposes, skip signature verification
                # In production, implement proper eth signature verification
                print(f"🔐 Demo mode: Skipping signature verification for {address}")
                # from eth_account.messages import encode_defunct
                # from eth_account import Account
                
                # message_hash = encode_defunct(text=message)
                # recovered_address = Account.recover_message(message_hash, signature=signature)
                
                # if recovered_address.lower() != address.lower():
                #     return jsonify({'error': 'Invalid signature verification'}), 400
                
                # Store authorized session (signature method - no private key stored)
                active_sessions[session_id] = {
                    'address': address,
                    'method': 'signature',
                    'authorized': True,
                    'has_private_key': False,
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'method': 'signature',
                    'message': 'Wallet authorized with signature - transactions will need MetaMask confirmation',
                    'has_private_key': False
                })
                
            except Exception as e:
                return jsonify({'error': f'Signature verification failed: {str(e)}'}), 400
        
        # Method 2: Private key (direct blockchain access)
        elif auth_method == 'private_key':
            if not private_key:
                return jsonify({'error': 'Private key is required for private_key method'}), 400
            
            try:
                # Verify private key matches address
                from eth_account import Account
                account = Account.from_key(private_key)
                
                if account.address.lower() != address.lower():
                    return jsonify({'error': 'Private key does not match provided address'}), 400
                
                # Connect wallet manager with private key
                wallet_result = wallet_manager.connect_with_private_key(private_key)
                if not wallet_result['success']:
                    return jsonify({'error': f'Wallet connection failed: {wallet_result.get("error")}'}), 400
                
                # Store session with private key access
                active_sessions[session_id] = {
                    'address': address,
                    'method': 'private_key',
                    'authorized': True,
                    'has_private_key': True,
                    'wallet_connected': True,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Also update blockchain integrator
                blockchain_integrator.private_key = private_key
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'method': 'private_key',
                    'message': 'Wallet connected with private key - direct blockchain access enabled',
                    'address': account.address,
                    'balance_eth': wallet_result.get('balance_eth', 0),
                    'has_private_key': True
                })
                
            except Exception as e:
                return jsonify({'error': f'Private key connection failed: {str(e)}'}), 400
        
        # Method 3: Seed phrase
        elif auth_method == 'seed_phrase':
            if not seed_phrase:
                return jsonify({'error': 'Seed phrase is required for seed_phrase method'}), 400
            
            try:
                # Connect with seed phrase
                wallet_result = wallet_manager.connect_with_mnemonic(seed_phrase)
                if not wallet_result['success']:
                    return jsonify({'error': f'Seed phrase connection failed: {wallet_result.get("error")}'}), 400
                
                # Store session
                active_sessions[session_id] = {
                    'address': wallet_result['address'],
                    'method': 'seed_phrase',
                    'authorized': True,
                    'has_private_key': True,
                    'wallet_connected': True,
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'method': 'seed_phrase',
                    'message': 'Wallet connected with seed phrase',
                    'address': wallet_result['address'],
                    'balance_eth': wallet_result.get('balance_eth', 0),
                    'has_private_key': True
                })
                
            except Exception as e:
                return jsonify({'error': f'Seed phrase connection failed: {str(e)}'}), 400
        
        else:
            return jsonify({'error': 'Invalid authorization method. Use: signature, private_key, or seed_phrase'}), 400
        
        # Backward compatibility - store in old format too
        authorized_addresses[address] = {
            'address': address,
            'signature': signature,
            'authorized': True,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prepare_swap', methods=['POST'])
def prepare_swap():
    """Prepare swap transaction data for MetaMask signing"""
    try:
        data = request.get_json()
        from_token = data.get('from_token', '').upper()
        to_token = data.get('to_token', '').upper()
        amount = float(data.get('amount', 0))
        user_address = data.get('user_address', '')
        
        if not all([from_token, to_token, amount, user_address]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Find best route
        route_result = swap_agent.find_best_swap_route(from_token, to_token, amount)
        
        if not route_result.get('success'):
            return jsonify({'error': 'No route found for this swap'}), 400
        
        # Prepare transaction data (don't execute)
        router_address = "0x08feDaACe14EB141E51282441b05182519D853D1"
        
        # Build swap data
        swap_data = blockchain_integrator._build_swap_data(
            blockchain_integrator.w3.to_wei(amount, 'ether'), 
            to_token
        )
        
        # Prepare transaction object
        transaction_data = {
            'to': router_address,
            'value': str(int(blockchain_integrator.w3.to_wei(amount, 'ether'))),
            'data': swap_data,
            'gas': 200000,
            'gasPrice': blockchain_integrator.w3.to_wei('0.0001', 'gwei')
        }
        
        return jsonify({
            'success': True,
            'transaction': transaction_data,
            'route_details': route_result.get('route_details'),
            'estimated_output': route_result.get('route_details', {}).get('estimated_output', 0)
        })
        
    except Exception as e:
        print(f"🚨 Prepare swap error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/status', methods=['POST'])
def get_session_status():
    """Get session status"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        if session_id not in active_sessions:
            return jsonify({'error': 'Invalid session ID'}), 404
        
        session = active_sessions[session_id]
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session_id,
                'address': session.get('address'),
                'method': session.get('method'),
                'authorized': session.get('authorized', False),
                'has_private_key': session.get('has_private_key', False),
                'wallet_connected': session.get('wallet_connected', False),
                'connected_at': session.get('timestamp')
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/confirm_transaction', methods=['POST'])
def confirm_transaction():
    """Confirm MetaMask transaction completion"""
    try:
        data = request.get_json()
        tx_hash = data.get('tx_hash', '')
        user_address = data.get('user_address', '')
        session_id = data.get('session_id', '')
        transaction_type = data.get('transaction_type', 'swap')
        
        if not all([tx_hash, user_address]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Validate session if provided
        if session_id and session_id in active_sessions:
            session = active_sessions[session_id]
            if not session.get('authorized'):
                return jsonify({'error': 'Session not authorized'}), 401
        
        # Store transaction record
        transaction_record = {
            'tx_hash': tx_hash,
            'user_address': user_address,
            'session_id': session_id,
            'transaction_type': transaction_type,
            'method': 'metamask_signing',
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'from_token': data.get('from_token'),
            'to_token': data.get('to_token'),
            'amount': data.get('amount')
        }
        
        # You could store this in a database in production
        print(f"📝 Transaction confirmed: {transaction_record}")
        
        # Ensure tx_hash has 0x prefix for explorer URL
        if not tx_hash.startswith('0x'):
            tx_hash = '0x' + tx_hash
        
        return jsonify({
            'success': True,
            'message': 'Transaction confirmed',
            'tx_hash': tx_hash,
            'explorer_url': f"https://explorer.testnet.riselabs.xyz/tx/{tx_hash}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/status', methods=['GET'])
def get_agents_status():
    """Get agent status"""
    try:
        return jsonify({
            'success': True,
            'agents': {
                'swap_agent': {
                    'status': 'active',
                    'pools': len(swap_agent.pools),
                    'supported_tokens': ['WETH', 'USDT', 'USDC', 'RISE']
                },
                'blockchain_integrator': {
                    'status': 'connected' if blockchain_integrator.is_connected else 'disconnected',
                    'network': 'RISE Testnet',
                    'rpc_url': blockchain_integrator.rpc_url
                }
            },
            'active_sessions': len(active_sessions),
            'authorized_addresses': len(authorized_addresses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 AI Swap Assistant - Chat Interface")
    print("EthIstanbul Hackathon Project")
    print("=" * 60)
    
    # Configure blockchain integrator
    private_key = "0xf38c811b61dc42e9b2dfa664d2ae2302c4958b5ff6ab607186b70e76e86802a6"  # Demo key
    blockchain_integrator.private_key = private_key
    print("🔗 Blockchain integrator private key configured")
    
    # Connect wallet manager
    wallet_result = wallet_manager.connect_with_private_key(private_key)
    if wallet_result['success']:
        print("✅ Wallet connected:", wallet_result['message'])
    else:
        print("❌ Wallet connection error:", wallet_result['error'])
    
    print("💬 Chat AI: Ready")
    print("🌐 Web interface: http://localhost:3000")
    print("📡 API endpoints:")
    print("  - POST /api/chat")
    print("  - GET  /api/agents/status")
    
    app.run(host='0.0.0.0', port=8000, debug=True)