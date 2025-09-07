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

  const executeSwap = useCallback(async (params: SwapParams, sessionId?: string) => {
    if (!isConnected || !address) {
      setSwapState({
        isLoading: false,
        error: 'Wallet not connected',
        success: false,
      });
      return;
    }

    setSwapState({
      isLoading: true,
      error: null,
      success: false,
    });

    try {
      // Execute the swap via chat API with session support
      const requestBody: any = {
        message: `${params.amount} ${params.fromToken} to ${params.toToken}`,
        user_address: address,
      };

      // Add session ID if provided
      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      const chatResponse = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
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
      } else if (response.type === 'swap_error') {
        throw new Error(response.message || 'Swap failed');
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
