import { useState, useCallback, useEffect } from 'react';
import { useAccount, useSignMessage } from 'wagmi';

interface WalletAuthState {
  isAuthorized: boolean;
  authMethod: 'none' | 'signature' | 'private_key' | 'seed_phrase';
  sessionId: string | null;
  hasPrivateKey: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthorizeOptions {
  method: 'signature' | 'private_key' | 'seed_phrase';
  privateKey?: string;
  seedPhrase?: string;
}

export function useWalletAuth() {
  const [authState, setAuthState] = useState<WalletAuthState>({
    isAuthorized: false,
    authMethod: 'none',
    sessionId: null,
    hasPrivateKey: false,
    isLoading: false,
    error: null,
  });

  const { address, isConnected } = useAccount();
  const { signMessageAsync } = useSignMessage();

  // Session'ı localStorage'dan yükle
  useEffect(() => {
    const savedSessionId = localStorage.getItem('wallet_session_id');
    const savedAddress = localStorage.getItem('wallet_address');
    
    if (savedSessionId && savedAddress === address && address) {
      // Session durumunu kontrol et
      checkSessionStatus(savedSessionId);
    }
  }, [address]);

  const checkSessionStatus = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/session/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.session.authorized) {
          setAuthState({
            isAuthorized: true,
            authMethod: data.session.method,
            sessionId: sessionId,
            hasPrivateKey: data.session.has_private_key,
            isLoading: false,
            error: null,
          });
          return;
        }
      }
      
      // Session geçersiz, temizle
      localStorage.removeItem('wallet_session_id');
      localStorage.removeItem('wallet_address');
      
    } catch (error) {
      console.error('Session check failed:', error);
    }
  }, []);

  const authorizeWallet = useCallback(async (options: AuthorizeOptions) => {
    if (!isConnected || !address) {
      setAuthState(prev => ({
        ...prev,
        error: 'Wallet not connected',
        isLoading: false
      }));
      return;
    }

    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      let authPayload: any = {
        address: address,
        method: options.method
      };

      // Method'a göre farklı authorization
      switch (options.method) {
        case 'signature':
          // MetaMask ile message imzala
          const message = `AI Swap Assistant Authorization\nAddress: ${address}\nTimestamp: ${Date.now()}\nChain: RISE Testnet`;
          const signature = await signMessageAsync({ message });
          
          authPayload.signature = signature;
          authPayload.message = message;
          break;

        case 'private_key':
          if (!options.privateKey) {
            throw new Error('Private key is required for private_key method');
          }
          authPayload.private_key = options.privateKey;
          break;

        case 'seed_phrase':
          if (!options.seedPhrase) {
            throw new Error('Seed phrase is required for seed_phrase method');
          }
          authPayload.seed_phrase = options.seedPhrase;
          break;

        default:
          throw new Error('Invalid authorization method');
      }

      // Backend'e authorization gönder
      const response = await fetch('http://localhost:8000/api/authorize_wallet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(authPayload)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Session bilgilerini sakla
        localStorage.setItem('wallet_session_id', data.session_id);
        localStorage.setItem('wallet_address', address);
        
        setAuthState({
          isAuthorized: true,
          authMethod: data.method,
          sessionId: data.session_id,
          hasPrivateKey: data.has_private_key,
          isLoading: false,
          error: null,
        });

        console.log('✅ Wallet authorized:', {
          method: data.method,
          address: data.address || address,
          hasPrivateKey: data.has_private_key
        });

      } else {
        throw new Error(data.error || 'Authorization failed');
      }

    } catch (error: any) {
      console.error('Authorization error:', error);
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Authorization failed'
      }));
    }
  }, [isConnected, address, signMessageAsync]);

  const disconnectWallet = useCallback(() => {
    // Session bilgilerini temizle
    localStorage.removeItem('wallet_session_id');
    localStorage.removeItem('wallet_address');
    
    setAuthState({
      isAuthorized: false,
      authMethod: 'none',
      sessionId: null,
      hasPrivateKey: false,
      isLoading: false,
      error: null,
    });
  }, []);

  const clearError = useCallback(() => {
    setAuthState(prev => ({ ...prev, error: null }));
  }, []);

  // Wallet bağlantısı kesilince session'ı temizle
  useEffect(() => {
    if (!isConnected) {
      disconnectWallet();
    }
  }, [isConnected, disconnectWallet]);

  return {
    ...authState,
    authorizeWallet,
    disconnectWallet,
    clearError,
    isConnected,
    address
  };
}
