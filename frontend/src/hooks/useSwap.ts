import { useState, useCallback } from 'react';
import { useAccount, useBalance, useChainId } from 'wagmi';

interface SwapState {
  isLoading: boolean;
  error: string | null;
  success: boolean;
  txHash?: string;
  explorerUrl?: string;
}

interface SwapParams {
  fromToken: string;
  toToken: string;
  amount: number;
  slippage?: number;
}

export function useSwap() {
  const [swapState, setSwapState] = useState<SwapState>({
    isLoading: false,
    error: null,
    success: false,
  });

  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { data: balance } = useBalance({ address });

  const executeSwap = useCallback(async (params: SwapParams) => {
    if (!isConnected || !address) {
      setSwapState({
        isLoading: false,
        error: 'Wallet not connected',
        success: false,
      });
      return;
    }

    // Wallet should already be authorized via signature

    setSwapState({
      isLoading: true,
      error: null,
      success: false,
    });

    try {
      // First, get the best swap route
      const routeResponse = await fetch('/api/find_route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from_token: params.fromToken,
          to_token: params.toToken,
          amount: params.amount,
        }),
      });

      if (!routeResponse.ok) {
        throw new Error('Failed to find swap route');
      }

      const routeData = await routeResponse.json();

      if (!routeData.success) {
        throw new Error(routeData.error || 'No route found');
      }

      // Security check with phishing detector
      const securityResponse = await fetch('/api/analyze_transaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to_address: routeData.route_details.contract_address,
          from_address: address,
          value: params.amount,
          data: '0x', // Swap data would go here
          gas_limit: routeData.route_details.estimated_gas,
        }),
      });

      if (!securityResponse.ok) {
        throw new Error('Security check failed');
      }

      const securityData = await securityResponse.json();

      if (securityData.risk_score > 70) {
        throw new Error(`High risk transaction detected: ${securityData.description}`);
      }

      // Execute the swap via chat API
      const chatResponse = await fetch('http://localhost:8003/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `${params.amount} ${params.fromToken} to ${params.toToken}`,
          user_address: address,
        }),
      });

      if (!chatResponse.ok) {
        throw new Error('Swap execution failed');
      }

      const chatData = await chatResponse.json();

      if (!chatData.success) {
        throw new Error(chatData.error || 'Swap failed');
      }

      const response = chatData.response;

      if (response.type === 'swap_success') {
        setSwapState({
          isLoading: false,
          error: null,
          success: true,
          txHash: response.tx_hash,
          explorerUrl: response.explorer_url,
        });
      } else {
        throw new Error(response.message || 'Swap failed');
      }

    } catch (error) {
      setSwapState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        success: false,
      });
    }
  }, [isConnected, address]);

  const estimateGas = useCallback(async (params: SwapParams) => {
    try {
      const response = await fetch('/api/estimate_gas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from_token: params.fromToken,
          to_token: params.toToken,
          amount: params.amount,
          from_address: address,
        }),
      });

      if (!response.ok) {
        throw new Error('Gas estimation failed');
      }

      const data = await response.json();
      return data;

    } catch (error) {
      console.error('Gas estimation error:', error);
      return null;
    }
  }, [address]);

  const resetSwapState = useCallback(() => {
    setSwapState({
      isLoading: false,
      error: null,
      success: false,
    });
  }, []);

  return {
    swapState,
    executeSwap,
    estimateGas,
    resetSwapState,
    isConnected,
    address,
    balance: balance?.formatted,
    chainId,
  };
}
