# AI Swap Assistant - RISE Chain Token Swaps

🚀 **EthIstanbul Hackathon Project**

An intelligent AI-powered swap assistant that executes real token swaps on RISE Chain (Ethereum L2):

**Core Features:**
- **AI Swap Agent** - Natural language token swap processing
- **Real Blockchain Integration** - Actual transactions on RISE Chain testnet
- **Modern Frontend** - React + RainbowKit wallet integration

## 📁 Project Structure

```
AgentX/
├── app.py                     # Flask backend API
├── swap_agent.py              # Swap Agent - Token swap optimization  
├── wallet_manager.py          # Wallet connection and transaction management
├── blockchain_integration.py  # Web3 blockchain integration
├── frontend/                 # Modern React + RainbowKit frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx    # Root layout with providers
│   │   │   ├── page.tsx      # Main chat interface
│   │   │   └── providers.tsx # Wagmi & RainbowKit setup
│   │   ├── components/
│   │   │   ├── Navbar.tsx    # Navigation with wallet connect
│   │   │   ├── RightSidebar.tsx # Available swaps display
│   │   │   └── WalletStatus.tsx # Wallet status display
│   │   └── hooks/
│   │       └── useSwap.ts    # Swap transaction hooks
│   ├── package.json          # Node.js dependencies
│   └── .env.local           # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🛠️ Installation

### 1. Requirements

- Python 3.7+
- pip (Python package manager)

### 2. Install Dependencies

```bash
# Go to project directory
cd AgentX

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Backend

```bash
# Flask backend API (Port 8000)
python app.py
```

### 4. Run Frontend (Recommended)

```bash
# In terminal 2
cd frontend

# Install Node.js dependencies
npm install

# Start development server (Port 3001)
PORT=3001 npm run dev
```

**Access the application:**
- Modern React frontend: http://localhost:3001
- Backend API: http://localhost:8000

## 💬 Chat Interface Usage

### Modern React Frontend (Recommended)

1. **Start backend:** `python app.py`
2. **Start frontend:** `cd frontend && PORT=3001 npm run dev`
3. **Open in browser:** http://localhost:3001
4. **Connect wallet:** RainbowKit with MetaMask/WalletConnect
5. **Make swap:** Type "0.1 USDT to ETH" in chat

### Legacy HTML Interface

1. **Start backend:** `python app.py`
2. **Open in browser:** http://localhost:8000
3. **Connect wallet:** Private key or MetaMask
4. **Make swap:** Type "0.1 USDT to ETH" in chat

### Wallet Connection Options

#### Modern Frontend (RainbowKit)
- **MetaMask:** Browser extension
- **WalletConnect:** Mobile wallets
- **Coinbase Wallet:** Coinbase integration
- **Rainbow Wallet:** Native mobile support
- **Trust Wallet:** Mobile wallet
- **Ledger:** Hardware wallet support
- **Argent:** Smart contract wallet

#### Legacy Interface
- **MetaMask:** Automatic connection with browser extension
- **Private Key:** Direct connection with private key  
- **Seed Phrase:** Connection with 12-24 word mnemonic

### 🎯 Supported Swaps

**✅ Active Swaps:**
- ETH → USDT, USDC, RISE
- USDT → USDC

### Example Chat Commands

```
"0.1 ETH to USDT"
"0.5 ETH to USDC"  
"1 ETH to RISE"
"10 USDT to USDC"
"Help"
```

### Real Transaction Flow

1. User writes swap request in chat
2. AI analyzes request with natural language processing
3. Swap Agent finds the optimal route
4. Wallet Manager executes real blockchain transaction
5. Result is shown in chat (TX hash + Explorer link)

## 🔧 Technical Details

### Backend API

**Main Endpoints:**
- `/api/chat` - AI chat interface
- `/api/authorize_wallet` - Wallet authorization
- `/api/agents/status` - System status

### Supported Tokens

- **ETH** - Native Ethereum
- **USDT** - Tether USD
- **USDC** - USD Coin  
- **RISE** - RISE Chain token

## 📊 Key Features

### AI Swap Assistant

- ✅ **Natural Language Processing**: Understands swap requests in chat
- ✅ **Real Blockchain Integration**: Actual transactions on RISE Chain
- ✅ **Multi-Token Support**: ETH, USDT, USDC, RISE
- ✅ **Two-Step Swaps**: Automatic approval + swap execution
- ✅ **Gas Optimization**: Efficient transaction processing
- ✅ **Error Handling**: User-friendly error messages with retry options
- ✅ **Transaction Tracking**: Explorer links for all transactions

### Modern Frontend

- ✅ **RainbowKit Integration**: Multiple wallet support
- ✅ **Real-time Chat**: Instant AI responses
- ✅ **Responsive Design**: Mobile-friendly interface
- ✅ **Transaction Status**: Live updates and confirmations

## 🔧 Error Handling

The system now includes comprehensive error handling for all swap operations:

### Error Types Covered

- **Insufficient Balance**: When wallet doesn't have enough tokens
- **Network Errors**: Connection issues with blockchain
- **High Slippage**: Price impact too high for trade
- **Unsupported Tokens**: Tokens not available on the platform
- **Gas Estimation Failures**: Unable to estimate transaction costs
- **Wallet Connection Issues**: Wallet not connected or authorized
- **Transaction Failures**: Blockchain transaction rejected
- **Route Not Found**: No trading path available
- **Approval Required**: Token spending approval needed
- **Timeout Errors**: Transaction taking too long

### User Experience Features

- **Retry Buttons**: All error messages include "Try Again" functionality
- **Clear Error Messages**: User-friendly explanations with solutions
- **Automatic Classification**: Errors are automatically categorized
- **Recovery Suggestions**: Specific steps to resolve each error type

## 🤝 Contributing

This project was developed for the EthIstanbul hackathon. To contribute:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

- **Developer**: EthIstanbul Hackathon Participant
- **Project**: AI Agent Marketplace
- **Blockchain**: RISE Chain (Ethereum L2)

## 📞 Contact

For questions:
- GitHub Issues
- EthIstanbul Discord
- Email: [your-email@example.com]

---

🎉 **Good luck at EthIstanbul!** 🚀