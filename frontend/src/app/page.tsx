'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAccount, useSignMessage } from 'wagmi';
import { 
  PaperAirplaneIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import RightSidebar from '@/components/RightSidebar';
import OrviumLogo from '@/components/OrviumLogo';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  type?: 'normal' | 'success' | 'error' | 'warning' | 'swap_error';
  txHash?: string;
  showExplorer?: boolean;
  canRetry?: boolean;
  originalMessage?: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [walletSignature, setWalletSignature] = useState<string>('');
  const [isWalletAuthorized, setIsWalletAuthorized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { isConnected, address } = useAccount();
  
  // Load authorization state from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined' && address) {
      const savedAuth = localStorage.getItem('wallet_auth');
      const savedSignature = localStorage.getItem('wallet_signature');
      
      if (savedAuth && savedSignature) {
        try {
          const authData = JSON.parse(savedAuth);
          // Check if the saved auth is for the same address and not expired
          if (authData.address === address && Date.now() - authData.timestamp < 24 * 60 * 60 * 1000) { // 24 hours
            setIsWalletAuthorized(true);
            setWalletSignature(savedSignature);
          } else {
            // Clean up expired or different address auth
            localStorage.removeItem('wallet_auth');
            localStorage.removeItem('wallet_signature');
          }
        } catch {
          // Clean up corrupted localStorage data
          localStorage.removeItem('wallet_auth');
          localStorage.removeItem('wallet_signature');
        }
      }
    } else if (typeof window !== 'undefined' && !address) {
      // Clean up if no address (wallet disconnected)
      localStorage.removeItem('wallet_auth');
      localStorage.removeItem('wallet_signature');
    }
  }, [address]);
  const { signMessageAsync } = useSignMessage();

  const requestWalletAuthorization = React.useCallback(async () => {
    if (!isConnected || !address) {
      return;
    }
    
    try {
      const message = `Welcome to Orvium Rise Tool!\n\nThis signature is to authorize your wallet for DeFi operations.\n\nAddress: ${address}\nTime: ${new Date().toISOString()}`;
      
      const signature = await signMessageAsync({ message });
      
      if (signature) {
        setWalletSignature(signature);
        setIsWalletAuthorized(true);
        
        // Save to localStorage
        if (typeof window !== 'undefined') {
          localStorage.setItem('wallet_signature', signature);
          localStorage.setItem('wallet_auth', JSON.stringify({
            address,
            timestamp: Date.now()
          }));
        }
        
        // Backend'e signature'ı gönder
        try {
          await fetch('/api/authorize_wallet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              address,
              signature,
              message
            })
          });
        } catch {
          // Backend error shouldn't prevent frontend authorization
          console.warn('Backend authorization failed, but continuing with frontend auth');
        }
      }
    } catch (error: unknown) {
      // Only log if it's not a user rejection
      const errorObj = error as { name?: string; message?: string };
      if (errorObj.name !== 'UserRejectedRequestError' && !errorObj.message?.includes('rejected')) {
        console.error('Wallet authorization error:', error);
      }
    }
  }, [isConnected, address, signMessageAsync]);

  useEffect(() => {
    setMounted(true);
  }, []);
  
  useEffect(() => {
    if (isConnected && address && !isWalletAuthorized) {
      // Small delay to ensure wallet is fully connected
      const timer = setTimeout(() => {
        requestWalletAuthorization();
      }, 500);
      return () => clearTimeout(timer);
    }

    if (!isConnected) {
      setIsWalletAuthorized(false);
      setWalletSignature('');
      // Clear localStorage when wallet disconnected
      if (typeof window !== 'undefined') {
        localStorage.removeItem('wallet_auth');
        localStorage.removeItem('wallet_signature');
      }
    }
  }, [isConnected, address, isWalletAuthorized, requestWalletAuthorization]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isConnected && isWalletAuthorized && messages.length === 0) {
      addMessage('👋 **Hello! Welcome to Orvium Rise Tool!**\n\n🚀 **Available operations:**\n\n🟡 **ETH → Others:**\n• "0.1 ETH to USDT" - Active\n• "0.5 ETH to USDC" - Active\n• "1 ETH to RISE" - Active\n\n🔄 **Token ↔ Token:**\n• "10 USDT to USDC" - Active\n\n💡 **What would you like to do?**', false, 'normal');
    }
  }, [isConnected, isWalletAuthorized, messages.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (content: string, isUser: boolean, type: Message['type'] = 'normal', txHash?: string, canRetry?: boolean, originalMessage?: string) => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`, // Unique ID with timestamp + random string
      content,
      isUser,
      timestamp: new Date(),
      type,
      txHash,
      showExplorer: !!txHash,
      canRetry,
      originalMessage
    };
    
    setMessages(prev => [...prev, newMessage]);
  };

  const handleRetryMessage = (message: Message) => {
    if (message.originalMessage) {
      // Re-send the original message
      handleSendMessage(message.originalMessage);
    }
  };

  const addTypingIndicator = () => {
    setIsTyping(true);
  };

  const removeTypingIndicator = () => {
    setIsTyping(false);
  };

  const handleSendMessage = async (retryMessage?: string) => {
    const message = retryMessage || inputMessage.trim();
    if (!message) return;
    if (!mounted) return;

    if (!retryMessage) {
      setInputMessage('');
      // Add user message (only if not retrying)
      addMessage(message, true);
    }
    
    // Add typing indicator
    addTypingIndicator();

    try {
      // Send to backend chat API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          user_address: address || null,
          signature: walletSignature
        })
      });

      const data = await response.json();
      console.log('Backend response:', data); // Debug log
      
      removeTypingIndicator();

      if (data.success) {
        const messageType = data.response.type === 'swap_success' || data.response.type === 'transfer_success' ? 'success' :
                          data.response.type === 'error' || data.response.type === 'swap_error' ? 'swap_error' : 
                          data.response.type === 'help' ? 'normal' :
                          'normal';
        
        addMessage(
          data.response.message, 
          false, 
          messageType,
          data.response.tx_hash,
          data.response.can_retry,
          data.response.can_retry ? message : undefined
        );

        // Show additional info for successful swaps
        if (data.response.type === 'swap_success' && data.response.route_details) {
          const details = data.response.route_details;
          let detailsMessage = `📊 **Transaction Details:**
• **Route:** ${details.pools.join(' → ')}
• **Estimated Output:** ${details.estimated_output.toFixed(4)}
• **Gas Cost:** $${details.gas_cost_usd.toFixed(2)}
• **Price Impact:** ${(details.price_impact * 100).toFixed(2)}%`;

          // Add approval info for two-step swaps
          if (data.response.approval_tx_hash) {
            detailsMessage += `\n\n🔐 **Approval Transaction:**
• **Hash:** \`${data.response.approval_tx_hash}\`
• **Explorer:** [View Approval](${data.response.approval_explorer_url})`;
          }
          
          addMessage(detailsMessage, false, 'normal');
        }
      } else {
        addMessage(`❌ An error occurred: ${data.error || 'Unknown error'}`, false, 'error');
      }

    } catch (error: unknown) {
      removeTypingIndicator();
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      addMessage(`❌ Connection error: ${errorMessage}`, false, 'error');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (type: Message['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />;
      default:
        return <CpuChipIcon className="h-5 w-5 text-blue-400" />;
    }
  };

  const getMessageBorderColor = (type: Message['type']) => {
    switch (type) {
      case 'success':
        return 'border-green-400/30 bg-green-400/10';
      case 'error':
        return 'border-red-400/30 bg-red-400/10';
      case 'warning':
        return 'border-yellow-400/30 bg-yellow-400/10';
      default:
        return 'border-white/10 bg-white/5';
    }
  };

  const formatMessageContent = (content: string) => {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="text-gray-300">$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-white/10 px-2 py-1 rounded text-sm font-mono">$1</code>')
      .replace(/\n/g, '<br>');
  };

  if (!mounted) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-purple-900/30">
      <div className="max-w-7xl mx-auto pl-8 pr-4 sm:pl-10 sm:pr-6 lg:pl-12 lg:pr-8 py-4">
        {!isConnected || !isWalletAuthorized ? (
          <div className="text-center py-20 animate-fade-in">
            <div className="mx-auto mb-8">
              <OrviumLogo size="xl" className="animate-pulse-glow hover:scale-110 transition-transform duration-300" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">Orvium Rise Tool</h1>
            <p className="text-xl text-gray-300 mb-8">Advanced DeFi operations on RISE Chain testnet</p>
            <p className="text-gray-400">Connect your wallet to continue</p>
          </div>
        ) : (
          <div className="flex space-x-4 h-[calc(100vh-120px)]">
            {/* Main Chat Interface */}
            <div className="flex-1 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-slide-up hover:shadow-3xl transition-all duration-500">
              <div className="flex items-center justify-center border-b border-white/10 p-4 bg-gradient-to-r from-black/50 to-purple-600/10">
                <div className="flex items-center space-x-3 animate-fade-in-delay">
                  <OrviumLogo size="lg" className="animate-spin-slow hover:animate-pulse" />
                  <div>
                    <h2 className="text-lg font-semibold text-white">Orvium Rise Tool</h2>
                    <p className="text-xs text-gray-300">RISE Chain Testnet</p>
                  </div>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-hide">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-message-appear`}
                  >
                    <div className={`flex items-start space-x-3 max-w-[80%] ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.isUser 
                          ? 'bg-gradient-to-r from-gray-700 to-purple-600/80 shadow-lg border border-purple-500/20' 
                          : `border ${getMessageBorderColor(message.type)}`
                      }`}>
                        {message.isUser ? (
                          <div className="w-4 h-4 bg-white rounded-full" />
                        ) : (
                          getMessageIcon(message.type)
                        )}
                      </div>

                      <div className={`px-4 py-3 rounded-2xl border ${
                        message.isUser 
                          ? 'bg-gradient-to-r from-gray-700 to-purple-600/80 text-white border-purple-500/20 shadow-lg' 
                          : `${getMessageBorderColor(message.type)} text-white`
                      } ${message.isUser ? 'rounded-br-md' : 'rounded-bl-md'}`}>
                        <div 
                          className="text-sm leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
                        />
                        {/* Retry Button for Error Messages */}
                        {message.type === 'swap_error' && message.canRetry && (
                          <div className="mt-3 pt-3 border-t border-white/20">
                            <button
                              onClick={() => handleRetryMessage(message)}
                              className="inline-flex items-center space-x-2 text-xs bg-red-500/20 hover:bg-red-500/30 px-3 py-1.5 rounded-lg transition-colors border border-red-400/30"
                            >
                              <ArrowPathIcon className="w-3 h-3" />
                              <span>Try Again</span>
                            </button>
                          </div>
                        )}
                        
                        {/* Explorer Link */}
                        {message.showExplorer && message.txHash && (
                          <div className="mt-3 pt-3 border-t border-white/20">
                            <a
                              href={`https://explorer.testnet.riselabs.xyz/tx/${message.txHash.startsWith('0x') ? message.txHash : '0x' + message.txHash}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center space-x-2 text-xs bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg transition-colors"
                            >
                              <span>View on Explorer</span>
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                            </a>
                          </div>
                        )}
                        <div className="mt-2 text-xs opacity-60">
                          {message.timestamp.toLocaleTimeString('tr-TR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-3 max-w-[80%]">
                      <div className="w-8 h-8 rounded-full border border-blue-400/30 bg-blue-400/10 flex items-center justify-center">
                        <CpuChipIcon className="h-4 w-4 text-blue-400 animate-pulse" />
                      </div>
                      <div className="px-4 py-3 rounded-2xl rounded-bl-md border border-blue-400/20 bg-gradient-to-r from-blue-400/5 to-purple-400/5 backdrop-blur-sm">
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                          <span className="text-xs text-blue-300/80 animate-pulse ml-2">AI is thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <div className="border-t border-white/10 p-4">
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={isConnected ? "Type your message... (e.g. 0.1 ETH to USDT)" : "Connect your wallet first..."}
                    disabled={!isConnected}
                    className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputMessage.trim() || !isConnected || isTyping}
                    className="bg-gradient-to-r from-gray-700 to-purple-600/80 hover:from-gray-600 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg border border-purple-500/20"
                  >
                    <PaperAirplaneIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
            
            {/* Right Sidebar */}
            <RightSidebar />
          </div>
        )}
      </div>
    </div>
  );
}