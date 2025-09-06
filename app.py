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
    
    def process_message(self, message: str, user_address: str = None) -> dict:
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
            return self.handle_swap_request(swap_request, user_address)
        
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
    
    def handle_swap_request(self, swap_request: dict, user_address: str) -> dict:
        """Handle swap request with comprehensive error handling and approval support"""
        
        from_token = swap_request['from_token']
        to_token = swap_request['to_token']
        amount = swap_request['amount']
        
        # Input validation
        if not from_token or not to_token:
            return self.error_handler.get_error_response('UNSUPPORTED_TOKEN')
        
        if amount <= 0:
            return self.error_handler.get_error_response('INVALID_AMOUNT')
        
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
            
            # Generic error classification
            error_type = self.error_handler.classify_error(str(e), e)
            return self.error_handler.get_error_response(error_type)
    
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
        signature = data.get('signature', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Wallet signature verification
        if user_address and hasattr(authorize_wallet, 'authorized_addresses'):
            auth_data = authorize_wallet.authorized_addresses.get(user_address)
            if auth_data and auth_data.get('authorized'):
                # Demo private key (not secure in production!)
                simulated_private_key = "0xf38c811b61dc42e9b2dfa664d2ae2302c4958b5ff6ab607186b70e76e86802a6"
                blockchain_integrator.private_key = simulated_private_key
                
                # Connect wallet manager
                wallet_result = wallet_manager.connect_with_private_key(simulated_private_key)
                if not wallet_result['success']:
                    return jsonify({'error': f'Wallet connection failed: {wallet_result.get("error", "Unknown error")}'}), 400
        
        # Process message with Chat AI
        response = chat_ai.process_message(message, user_address)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/authorize_wallet', methods=['POST'])
def authorize_wallet():
    try:
        data = request.get_json()
        address = data.get('address', '')
        signature = data.get('signature', '')
        message = data.get('message', '')
        
        if not all([address, signature, message]):
            return jsonify({'error': 'Address, signature and message are required'}), 400
        
        # Authorized addresses storage
        if not hasattr(authorize_wallet, 'authorized_addresses'):
            authorize_wallet.authorized_addresses = {}
        
        authorize_wallet.authorized_addresses[address] = {
            'address': address,
            'signature': signature,
            'authorized': True,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Wallet successfully authorized',
            'address': address
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/status', methods=['GET'])
def get_agents_status():
    """Get agent status"""
    try:
        return jsonify({
            'success': True,
            'agents': {
                'swap_agent': {
                    'status': 'active',
                    'pools': len(swap_agent.liquidity_pools),
                    'supported_tokens': ['WETH', 'USDT', 'USDC', 'RISE']
                },
                'blockchain_integrator': {
                    'status': 'connected' if blockchain_integrator.is_connected else 'disconnected',
                    'network': 'RISE Testnet',
                    'rpc_url': blockchain_integrator.rpc_url
                }
            }
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
    
    app.run(host='0.0.0.0', port=8003, debug=True)