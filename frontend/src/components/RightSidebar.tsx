'use client';

import { 
  ArrowPathIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
  CircleStackIcon,
  ShieldCheckIcon
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
    <div className="w-96 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden h-[calc(100vh-120px)] flex flex-col">
      {/* Header */}
      <div className="border-b border-white/10 p-4 bg-gradient-to-r from-blue-500/10 to-purple-600/10">
        <h3 className="text-lg font-semibold text-white">Available Operations</h3>
        <p className="text-xs text-gray-300">RISE Chain Testnet</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4 scrollbar-hide">
        {/* Available Swaps Section */}
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <ArrowPathIcon className="h-5 w-5 text-blue-400" />
            <h4 className="text-sm font-semibold text-white">Available Swaps</h4>
          </div>
              <div className="space-y-1">
            {swapPairs.map((pair, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
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
          <div className="mt-2 p-2 bg-blue-500/5 border border-blue-400/10 rounded-lg">
            <p className="text-xs text-blue-300 font-mono">&quot;0.5 ETH to USDC&quot;</p>
          </div>
        </div>

        {/* Transfer Information Section */}
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <BanknotesIcon className="h-5 w-5 text-green-400" />
            <h4 className="text-sm font-semibold text-white">All Transfers</h4>
          </div>
            <div className="p-2 bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-400/20 rounded-lg">
            <p className="text-xs text-gray-300 mb-2">
              with RISE Chain&apos;s tokens
            </p>
              <div className="space-y-1">
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
          <div className="mt-2 p-2 bg-green-500/5 border border-green-400/10 rounded-lg">
            <p className="text-xs text-green-300 font-mono">&quot;send 0.001 eth to 0x...&quot;</p>
          </div>
        </div>

        {/* Phishing Detector Section */}
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <ShieldCheckIcon className="h-5 w-5 text-orange-400" />
            <h4 className="text-sm font-semibold text-white">Phishing Detector</h4>
          </div>
            <div className="p-2 bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-400/20 rounded-lg">
            <p className="text-xs text-gray-300 mb-2">
              Check address safety before transactions
            </p>
              <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm">
                <ShieldCheckIcon className="h-4 w-4 text-orange-400" />
                <span className="text-white">GoPlus Security</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <ShieldCheckIcon className="h-4 w-4 text-orange-400" />
                <span className="text-white">EtherScamDB</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <ShieldCheckIcon className="h-4 w-4 text-orange-400" />
                <span className="text-white">Local Intelligence</span>
              </div>
            </div>
          </div>
          <div className="mt-2 p-2 bg-orange-500/5 border border-orange-400/10 rounded-lg">
            <p className="text-xs text-orange-300 font-mono">&quot;verify 0x...&quot;</p>
          </div>
        </div>

        {/* Multi Sender Section */}
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <BanknotesIcon className="h-5 w-5 text-cyan-400" />
            <h4 className="text-sm font-semibold text-white">Multi Sender</h4>
          </div>
            <div className="p-2 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-400/20 rounded-lg">
            <p className="text-xs text-gray-300 mb-2">
              Send tokens to multiple addresses at once
            </p>
              <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm">
                <BanknotesIcon className="h-4 w-4 text-cyan-400" />
                <span className="text-white">Bulk Transfers</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <BanknotesIcon className="h-4 w-4 text-cyan-400" />
                <span className="text-white">Gas Optimized</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <BanknotesIcon className="h-4 w-4 text-cyan-400" />
                <span className="text-white">Up to 20 Recipients</span>
              </div>
            </div>
          </div>
          <div className="mt-2 p-2 bg-cyan-500/5 border border-cyan-400/10 rounded-lg">
            <p className="text-xs text-cyan-300 font-mono">&quot;send 0.01 eth to 0x...,0x...,0x...&quot;</p>
          </div>
        </div>

      </div>
    </div>
  );
}
