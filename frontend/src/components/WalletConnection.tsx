'use client';

import { useState } from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useWalletAuth } from '@/hooks/useWalletAuth';
import { WalletStatus } from './WalletStatus';
import { 
  ShieldCheckIcon, 
  KeyIcon, 
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

interface WalletConnectionProps {
  className?: string;
}

type AuthMethod = 'signature' | 'private_key' | 'seed_phrase';

export function WalletConnection({ className = '' }: WalletConnectionProps) {
  const {
    isConnected,
    address,
    isAuthorized,
    authMethod,
    sessionId,
    hasPrivateKey,
    isLoading,
    error,
    authorizeWallet,
    disconnectWallet,
    clearError
  } = useWalletAuth();

  const [selectedMethod, setSelectedMethod] = useState<AuthMethod>('signature');
  const [privateKey, setPrivateKey] = useState('');
  const [seedPhrase, setSeedPhrase] = useState('');
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [showSeedPhrase, setShowSeedPhrase] = useState(false);

  const handleAuthorize = async () => {
    clearError();
    
    try {
      await authorizeWallet({
        method: selectedMethod,
        privateKey: selectedMethod === 'private_key' ? privateKey : undefined,
        seedPhrase: selectedMethod === 'seed_phrase' ? seedPhrase : undefined
      });
      
      // Clear sensitive data after successful authorization
      if (selectedMethod === 'private_key') {
        setPrivateKey('');
      }
      if (selectedMethod === 'seed_phrase') {
        setSeedPhrase('');
      }
    } catch (error) {
      console.error('Authorization failed:', error);
    }
  };

  const getMethodIcon = (method: AuthMethod) => {
    switch (method) {
      case 'signature':
        return <ShieldCheckIcon className="h-5 w-5" />;
      case 'private_key':
        return <KeyIcon className="h-5 w-5" />;
      case 'seed_phrase':
        return <DocumentTextIcon className="h-5 w-5" />;
    }
  };

  const getMethodDescription = (method: AuthMethod) => {
    switch (method) {
      case 'signature':
        return 'MetaMask ile mesaj imzala (Güvenli - önerilen)';
      case 'private_key':
        return 'Private key ile direkt erişim (Riskli)';
      case 'seed_phrase':
        return 'Seed phrase ile bağlan (Riskli)';
    }
  };

  const getMethodDetails = (method: AuthMethod) => {
    switch (method) {
      case 'signature':
        return {
          security: 'Yüksek',
          functionality: 'Sınırlı - MetaMask onayı gerekli',
          risk: 'Düşük',
          color: 'text-green-400'
        };
      case 'private_key':
        return {
          security: 'Orta',
          functionality: 'Tam - Otomatik işlemler',
          risk: 'Yüksek',
          color: 'text-yellow-400'
        };
      case 'seed_phrase':
        return {
          security: 'Orta',
          functionality: 'Tam - Otomatik işlemler',
          risk: 'Yüksek',
          color: 'text-yellow-400'
        };
    }
  };

  if (!isConnected) {
    return (
      <div className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 ${className}`}>
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <ShieldCheckIcon className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Cüzdan Bağlantısı</h3>
          <p className="text-gray-400 mb-6">
            AI Swap Assistant kullanmak için cüzdanınızı bağlayın
          </p>
          <ConnectButton />
        </div>
      </div>
    );
  }

  if (isAuthorized) {
    return (
      <div className={`space-y-4 ${className}`}>
        {/* Authorization Status */}
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <CheckCircleIcon className="h-6 w-6 text-green-400" />
            <div>
              <h3 className="font-semibold text-green-400">Cüzdan Yetkilendirildi</h3>
              <p className="text-sm text-gray-300">
                Yöntem: {authMethod === 'signature' ? 'MetaMask İmza' : 
                        authMethod === 'private_key' ? 'Private Key' : 'Seed Phrase'}
                {hasPrivateKey && ' • Tam Erişim Aktif'}
              </p>
            </div>
          </div>
        </div>

        {/* Wallet Status */}
        <WalletStatus />

        {/* Disconnect Button */}
        <button
          onClick={disconnectWallet}
          className="w-full bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 font-medium py-2 px-4 rounded-lg transition-colors"
        >
          Oturumu Sonlandır
        </button>
      </div>
    );
  }

  return (
    <div className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <ExclamationTriangleIcon className="h-8 w-8 text-white" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Cüzdan Yetkilendirmesi</h3>
        <p className="text-gray-400">
          İşlem yapabilmek için cüzdanınızı yetkilendirin
        </p>
      </div>

      {/* Method Selection */}
      <div className="space-y-3">
        <h4 className="font-medium text-white">Yetkilendirme Yöntemi Seçin</h4>
        
        {(['signature', 'private_key', 'seed_phrase'] as AuthMethod[]).map((method) => {
          const details = getMethodDetails(method);
          return (
            <button
              key={method}
              onClick={() => setSelectedMethod(method)}
              className={`w-full p-4 rounded-lg border-2 transition-all ${
                selectedMethod === method
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-white/10 bg-white/5 hover:bg-white/10'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${selectedMethod === method ? 'bg-blue-500/20' : 'bg-white/10'}`}>
                  {getMethodIcon(method)}
                </div>
                <div className="flex-1 text-left">
                  <h5 className="font-medium text-white">{getMethodDescription(method)}</h5>
                  <div className="text-xs text-gray-400 mt-1 space-y-1">
                    <div>Güvenlik: <span className={details.color}>{details.security}</span></div>
                    <div>Fonksiyon: {details.functionality}</div>
                    <div>Risk: <span className={details.color}>{details.risk}</span></div>
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Method-specific inputs */}
      {selectedMethod === 'private_key' && (
        <div className="space-y-3">
          <label className="block text-sm font-medium text-white">Private Key</label>
          <div className="relative">
            <input
              type={showPrivateKey ? 'text' : 'password'}
              value={privateKey}
              onChange={(e) => setPrivateKey(e.target.value)}
              placeholder="0x..."
              className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 pr-12"
            />
            <button
              type="button"
              onClick={() => setShowPrivateKey(!showPrivateKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            >
              {showPrivateKey ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
            </button>
          </div>
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            <div className="flex space-x-2">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-300">
                <strong>Güvenlik Uyarısı:</strong> Private key'inizi sadece güvendiğiniz uygulamalarla paylaşın.
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedMethod === 'seed_phrase' && (
        <div className="space-y-3">
          <label className="block text-sm font-medium text-white">Seed Phrase (12 veya 24 kelime)</label>
          <div className="relative">
            <textarea
              value={seedPhrase}
              onChange={(e) => setSeedPhrase(e.target.value)}
              placeholder="word1 word2 word3 ..."
              rows={3}
              className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 resize-none"
            />
          </div>
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            <div className="flex space-x-2">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-300">
                <strong>Güvenlik Uyarısı:</strong> Seed phrase'inizi kimseyle paylaşmayın!
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedMethod === 'signature' && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
          <div className="flex space-x-3">
            <ShieldCheckIcon className="h-6 w-6 text-green-400 flex-shrink-0" />
            <div className="text-sm text-green-300">
              <strong>Güvenli Yöntem:</strong> MetaMask'ta bir mesaj imzalayacaksınız. 
              Private key'iniz paylaşılmayacak, ancak her işlem için MetaMask onayı gerekecek.
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <XMarkIcon className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <h5 className="font-medium text-red-400">Yetkilendirme Hatası</h5>
              <p className="text-sm text-red-300 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Authorize Button */}
      <button
        onClick={handleAuthorize}
        disabled={isLoading || 
          (selectedMethod === 'private_key' && !privateKey) ||
          (selectedMethod === 'seed_phrase' && !seedPhrase)
        }
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-lg transition-all"
      >
        {isLoading ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
            <span>Yetkilendiriliyor...</span>
          </div>
        ) : (
          'Cüzdanı Yetkilendir'
        )}
      </button>
    </div>
  );
}
