import { useCallback } from 'react';
import { useAccount, useSignMessage, useSendTransaction } from 'wagmi';

interface MetaMaskSigningState {
  isLoading: boolean;
  error: string | null;
  txHash: string | null;
}

interface SwapTransactionParams {
  fromToken: string;
  toToken: string;
  amount: number;
  sessionId?: string;
}

export function useMetaMaskSigning() {
  const { address, isConnected } = useAccount();
  const { signMessageAsync } = useSignMessage();
  const { sendTransactionAsync } = useSendTransaction();

  const executeSwapWithMetaMask = useCallback(async (params: SwapTransactionParams) => {
    if (!isConnected || !address) {
      throw new Error('Wallet not connected');
    }

    try {
      // 1. Backend'den transaction data hazırla
      const response = await fetch('/api/prepare_swap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from_token: params.fromToken,
          to_token: params.toToken,
          amount: params.amount,
          user_address: address
        })
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Transaction preparation failed');
      }

      const txData = data.transaction;

      // 2. MetaMask ile raw transaction gönder
      const txHash = await sendTransactionAsync({
        to: txData.to as `0x${string}`,
        data: txData.data as `0x${string}`,
        value: BigInt(txData.value),
        gas: BigInt(txData.gas || 200000)
      });

      // 3. Transaction receipt bekle
      return {
        success: true,
        txHash: txHash,
        explorerUrl: `https://explorer.testnet.riselabs.xyz/tx/${txHash}`,
        realTransaction: true
      };

    } catch (error: any) {
      console.error('MetaMask swap error:', error);
      throw new Error(error.message || 'MetaMask transaction failed');
    }
  }, [isConnected, address, sendTransactionAsync]);

  const signAuthorizationMessage = useCallback(async () => {
    if (!isConnected || !address) {
      throw new Error('Wallet not connected');
    }

    try {
      const message = `AI Swap Assistant Authorization\nAddress: ${address}\nTimestamp: ${Date.now()}\nChain: RISE Testnet\n\nThis signature authorizes your wallet for swap operations.`;
      
      const signature = await signMessageAsync({ message });
      
      return {
        message,
        signature,
        address
      };
    } catch (error: any) {
      console.error('MetaMask signing error:', error);
      throw new Error(error.message || 'Message signing failed');
    }
  }, [isConnected, address, signMessageAsync]);

  return {
    executeSwapWithMetaMask,
    signAuthorizationMessage,
    isConnected,
    address
  };
}
