'use client';

import { 
  ArrowPathIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
  CircleStackIcon
} from '@heroicons/react/24/outline';

interface SwapPair {
  from: string;
  to: string;
  icon: React.ReactNode;
}

interface TokenInfo {
  symbol: string;
  name: string;
  icon: React.ReactNode;
}

const swapPairs: SwapPair[] = [
  {
    from: 'ETH',
    to: 'USDC',
    icon: <ArrowPathIcon className="h-4 w-4 text-blue-400" />
  },
  {
    from: 'ETH',
    to: 'RISE',
    icon: <ArrowPathIcon className="h-4 w-4 text-blue-400" />
  }
];

const supportedTokens: TokenInfo[] = [
  {
    symbol: 'ETH',
    name: 'Ethereum',
    icon: <CircleStackIcon className="h-5 w-5 text-blue-400" />
  },
  {
    symbol: 'USDC',
    name: 'USD Coin',
    icon: <BanknotesIcon className="h-5 w-5 text-blue-500" />
  },
  {
    symbol: 'RISE',
    name: 'RISE Token',
    icon: <CircleStackIcon className="h-5 w-5 text-purple-400" />
  }
];

export default function RightSidebar() {
  return (
    <div className="w-80 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden h-[640px] flex flex-col">
      {/* Header */}
      <div className="border-b border-white/10 p-4 bg-gradient-to-r from-blue-500/10 to-purple-600/10">
        <h3 className="text-lg font-semibold text-white">Available Operations</h3>
        <p className="text-xs text-gray-300">RISE Chain Testnet</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
        {/* Available Swaps Section */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <ArrowPathIcon className="h-5 w-5 text-blue-400" />
            <h4 className="text-sm font-semibold text-white">Available Swaps</h4>
          </div>
          <div className="space-y-2">
            {swapPairs.map((pair, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  {pair.icon}
                  <span className="text-sm text-white">
                    {pair.from} → {pair.to}
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  Active
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Transfer Information Section */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <BanknotesIcon className="h-5 w-5 text-green-400" />
            <h4 className="text-sm font-semibold text-white">All Transfers</h4>
          </div>
          <div className="p-3 bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-400/20 rounded-lg">
            <p className="text-xs text-gray-300 mb-2">
              with RISE Chain&apos;s tokens
            </p>
            <div className="space-y-2">
              {supportedTokens.map((token, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-2 text-sm"
                >
                  {token.icon}
                  <span className="text-white">{token.symbol}</span>
                  <span className="text-gray-400">({token.name})</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Usage Examples */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <CircleStackIcon className="h-5 w-5 text-purple-400" />
            <h4 className="text-sm font-semibold text-white">Examples</h4>
          </div>
          <div className="space-y-2">
            <div className="p-3 bg-white/5 border border-white/10 rounded-lg">
              <p className="text-xs text-gray-300 mb-1">Swap Examples:</p>
              <p className="text-sm text-white font-mono">&quot;0.5 ETH to USDC&quot;</p>
              <p className="text-sm text-white font-mono">&quot;1 ETH to RISE&quot;</p>
            </div>
            <div className="p-3 bg-white/5 border border-white/10 rounded-lg">
              <p className="text-xs text-gray-300 mb-1">Transfer:</p>
              <p className="text-sm text-white font-mono">&quot;send 0.0001 eth to 0x...&quot;</p>
            </div>
            <div className="p-3 bg-white/5 border border-white/10 rounded-lg">
              <p className="text-xs text-gray-300 mb-1">Bulk Transfer:</p>
              <p className="text-sm text-white font-mono">&quot;send 0.003 eth to 0x...,0x...,0x...&quot;</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
