'use client';

import { useAccount, useBalance, useChainId, useEnsName } from 'wagmi';
import { useEffect, useState } from 'react';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationTriangleIcon,
  ClockIcon,
  LinkIcon
} from '@heroicons/react/24/outline';

interface WalletStatusProps {
  className?: string;
}

export function WalletStatus({ className = '' }: WalletStatusProps) {
  const [mounted, setMounted] = useState(false);
  const { address, isConnected, isConnecting, isDisconnected } = useAccount();
  const { data: balance, isLoading: balanceLoading } = useBalance({ address });
  const chainId = useChainId();
  const { data: ensName } = useEnsName({ address });

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className={`animate-pulse bg-white/5 rounded-xl p-4 ${className}`}>
        <div className="h-4 bg-white/10 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-white/10 rounded w-1/2"></div>
      </div>
    );
  }

  const getStatusIcon = () => {
    if (isConnecting) {
      return <ClockIcon className="h-5 w-5 text-yellow-400 animate-spin" />;
    }
    if (isConnected) {
      return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
    }
    if (isDisconnected) {
      return <XCircleIcon className="h-5 w-5 text-red-400" />;
    }
    return <ExclamationTriangleIcon className="h-5 w-5 text-orange-400" />;
  };

  const getStatusText = () => {
    if (isConnecting) return 'Connecting...';
    if (isConnected) return 'Connected';
    if (isDisconnected) return 'Disconnected';
    return 'Unknown';
  };

  const getStatusColor = () => {
    if (isConnecting) return 'border-yellow-400/30 bg-yellow-400/10';
    if (isConnected) return 'border-green-400/30 bg-green-400/10';
    if (isDisconnected) return 'border-red-400/30 bg-red-400/10';
    return 'border-orange-400/30 bg-orange-400/10';
  };

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const formatBalance = (bal: any) => {
    if (!bal) return '0.0000';
    const num = parseFloat(bal.formatted);
    return num.toFixed(4);
  };

  return (
    <div className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 space-y-3 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Wallet Status</h3>
        {getStatusIcon()}
      </div>

      {/* Status Badge */}
      <div className={`inline-flex items-center space-x-2 px-3 py-1.5 rounded-lg border ${getStatusColor()}`}>
        <div className={`w-2 h-2 rounded-full ${
          isConnected ? 'bg-green-400 animate-pulse' : 
          isConnecting ? 'bg-yellow-400 animate-pulse' : 
          'bg-red-400'
        }`} />
        <span className="text-sm font-medium text-white">{getStatusText()}</span>
      </div>

      {/* Connection Details */}
      {isConnected && address && (
        <div className="space-y-2">
          {/* Address */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Address:</span>
            <div className="flex items-center space-x-2">
              <code className="text-sm font-mono text-white bg-white/10 px-2 py-1 rounded">
                {ensName || formatAddress(address)}
              </code>
              <button
                onClick={() => navigator.clipboard.writeText(address)}
                className="p-1 hover:bg-white/10 rounded transition-colors"
                title="Copy address"
              >
                <LinkIcon className="h-4 w-4 text-gray-400 hover:text-white" />
              </button>
            </div>
          </div>

          {/* Balance */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Balance:</span>
            <span className="text-sm font-semibold text-white">
              {balanceLoading ? (
                <div className="animate-pulse bg-white/10 h-4 w-16 rounded"></div>
              ) : (
                `${formatBalance(balance)} ${balance?.symbol || 'ETH'}`
              )}
            </span>
          </div>

          {/* Network */}
          {chainId && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Network:</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-white">
                  {chainId === 1 ? 'Ethereum' : 
                   chainId === 137 ? 'Polygon' :
                   chainId === 11155931 ? 'RISE Testnet' :
                   `Chain ${chainId}`}
                </span>
              </div>
            </div>
          )}

          {/* Chain ID */}
          {chainId && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Chain ID:</span>
              <span className="text-sm font-mono text-white">{chainId}</span>
            </div>
          )}
        </div>
      )}

      {/* Not Connected State */}
      {!isConnected && !isConnecting && (
        <div className="text-center py-4">
          <XCircleIcon className="h-12 w-12 text-gray-500 mx-auto mb-2" />
          <p className="text-gray-400 text-sm">No wallet connected</p>
          <p className="text-gray-500 text-xs mt-1">
            Connect your wallet to start using AI agents
          </p>
        </div>
      )}

      {/* Connecting State */}
      {isConnecting && (
        <div className="text-center py-4">
          <ClockIcon className="h-12 w-12 text-yellow-400 mx-auto mb-2 animate-spin" />
          <p className="text-yellow-400 text-sm">Connecting wallet...</p>
          <p className="text-gray-500 text-xs mt-1">
            Please approve the connection in your wallet
          </p>
        </div>
      )}
    </div>
  );
}
