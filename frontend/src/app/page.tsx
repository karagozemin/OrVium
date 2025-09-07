'use client';

import { useState, useEffect, useRef } from 'react';
import { useAccount, useSignMessage } from 'wagmi';
import { 
  PaperAirplaneIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import RightSidebar from '@/components/RightSidebar';
import { WalletConnection } from '@/components/WalletConnection';
import { useWalletAuth } from '@/hooks/useWalletAuth';
import { useMetaMaskSigning } from '@/hooks/useMetaMaskSigning';

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
  swapDetails?: {
    from_token: string;
    to_token: string;
    amount: number;
  };
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [mounted, setMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { isConnected, address, chainId } = useAccount();
  const { 
    isAuthorized, 
    sessionId, 
    hasPrivateKey, 
    authMethod 
  } = useWalletAuth();
  
  const { executeSwapWithMetaMask } = useMetaMaskSigning();
  
  const { signMessageAsync, error: signError } = useSignMessage();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isConnected && isAuthorized && messages.length === 0) {
      const welcomeMessage = `👋 **Hello! Welcome to AI Swap Assistant!**\n\n💱 **Available swaps:**\n\n🟡 **ETH → Others:**\n• "0.1 ETH to USDT" - Active\n• "0.5 ETH to USDC" - Active\n• "1 ETH to RISE" - Active\n\n🔄 **Token ↔ Token:**\n• "10 USDT to USDC" - Active\n\n🔐 **Connection Status:**\n• Method: ${authMethod === 'signature' ? 'MetaMask Signature' : authMethod === 'private_key' ? 'Private Key' : 'Seed Phrase'}\n• Full Access: ${hasPrivateKey ? 'Yes' : 'No (MetaMask confirmation required)'}\n\n💡 **What would you like to do?**`;
      
      addMessage(welcomeMessage, false, 'normal');
    }
  }, [isConnected, isAuthorized, messages.length, authMethod, hasPrivateKey]);

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

  const handleMetaMaskSwap = async (swapDetails: any) => {
    try {
      addTypingIndicator();
      addMessage('🔐 MetaMask işlemi başlatılıyor...', false, 'normal');

      const result = await executeSwapWithMetaMask({
        fromToken: swapDetails.from_token,
        toToken: swapDetails.to_token,
        amount: swapDetails.amount,
        sessionId: sessionId || undefined
      });

      removeTypingIndicator();

      if (result.success) {
        addMessage(
          `✅ **MetaMask Swap Başarılı!**\n\n💰 **İşlem:** ${swapDetails.amount} ${swapDetails.from_token} → ${swapDetails.to_token}\n\n🔗 **Transaction Hash:** \`${result.txHash}\`\n\n📊 **Explorer:** [View Transaction](${result.explorerUrl})`,
          false,
          'success',
          result.txHash
        );
      }
    } catch (error: any) {
      removeTypingIndicator();
      addMessage(
        `❌ **MetaMask İşlem Hatası**\n\n🚫 ${error.message}\n\n💡 **Çözümler:**\n• MetaMask'ta işlemi onaylayın\n• Yeterli bakiye olduğundan emin olun\n• Gas ücretlerini kontrol edin`,
        false,
        'error'
      );
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
      // Send to backend chat API with session support
      const requestBody: any = {
        message,
        user_address: address || null
      };

      // Add session ID if available
      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      console.log('Backend response:', data); // Debug log
      
      removeTypingIndicator();

      if (data.success) {
        const response = data.response;
        
        // Handle MetaMask signing required
        if (response.type === 'metamask_signing_required') {
          addMessage(response.message, false, 'warning');
          
          // Add MetaMask action button
          addMessage(
            '🚀 **MetaMask ile İşlem Yap**\n\nAşağıdaki butona tıklayarak MetaMask ile işlemi gerçekleştirin.',
            false,
            'normal'
          );
          
          // We'll add a special message with MetaMask button
          const metamaskMessage: Message = {
            id: `${Date.now()}-metamask-action`,
            content: 'MetaMask Action Required',
            isUser: false,
            timestamp: new Date(),
            type: 'normal',
            // Store swap details for the button
            swapDetails: response.swap_details
          };
          setMessages(prev => [...prev, metamaskMessage]);
          return;
        }
        
        const messageType = response.type === 'swap_success' || response.type === 'transfer_success' ? 'success' :
                          response.type === 'error' || response.type === 'swap_error' ? 'swap_error' : 
                          response.type === 'help' ? 'normal' :
                          'normal';
        
        addMessage(
          response.message, 
          false, 
          messageType,
          response.tx_hash,
          response.can_retry,
          response.can_retry ? message : undefined
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

    } catch (error: any) {
      removeTypingIndicator();
      addMessage(`❌ Connection error: ${error.message}`, false, 'error');
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!isConnected || !isAuthorized ? (
          <div className="flex items-center justify-center min-h-[80vh]">
            <div className="max-w-md w-full">
              <div className="text-center mb-8">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center mx-auto mb-6">
                  <CpuChipIcon className="h-10 w-10 text-white" />
                </div>
                <h1 className="text-4xl font-bold text-white mb-4">AI Swap Assistant</h1>
                <p className="text-xl text-gray-300 mb-2">Token swap operations on RISE Chain testnet</p>
                <p className="text-gray-400">Connect and authorize your wallet to continue</p>
              </div>
              
              <WalletConnection />
            </div>
          </div>
        ) : (
          <div className="flex space-x-6">
            {/* Main Chat Interface */}
            <div className="flex-1 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden h-[640px] flex flex-col">
              <div className="flex items-center justify-center border-b border-white/10 p-4 bg-gradient-to-r from-blue-500/10 to-purple-600/10">
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <CpuChipIcon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">AI Swap Assistant</h2>
                    <p className="text-xs text-gray-300">RISE Chain Testnet</p>
                  </div>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start space-x-3 max-w-[80%] ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.isUser 
                          ? 'bg-gradient-to-r from-blue-500 to-purple-600' 
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
                          ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white border-transparent' 
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

                        {/* MetaMask Action Button */}
                        {message.swapDetails && (
                          <div className="mt-3 pt-3 border-t border-white/20">
                            <button
                              onClick={() => handleMetaMaskSwap(message.swapDetails)}
                              className="inline-flex items-center space-x-2 text-sm bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-4 py-2 rounded-lg transition-all transform hover:scale-105 font-medium"
                            >
                              <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
                                <span className="text-orange-600 text-xs font-bold">M</span>
                              </div>
                              <span>MetaMask ile İşlem Yap</span>
                            </button>
                            <div className="mt-2 text-xs text-gray-400">
                              {message.swapDetails.amount} {message.swapDetails.from_token} → {message.swapDetails.to_token}
                            </div>
                          </div>
                        )}
                        
                        {/* Explorer Link */}
                        {message.showExplorer && message.txHash && (
                          <div className="mt-3 pt-3 border-t border-white/20">
                            <a
                              href={`https://explorer.testnet.riselabs.xyz/tx/${message.txHash}`}
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
                    placeholder={isConnected && isAuthorized ? "Type your message... (e.g. 0.1 ETH to USDT)" : isConnected ? "Authorize your wallet first..." : "Connect your wallet first..."}
                    disabled={!isConnected || !isAuthorized}
                    className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputMessage.trim() || !isConnected || !isAuthorized || isTyping}
                    className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all duration-200 transform hover:scale-105"
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