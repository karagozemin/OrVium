# AI Agent Marketplace - Swap & Phishing Detector Agents

🚀 **EthIstanbul Hackathon Project**

This project contains two core agents developed for the AI Agent Marketplace that will run on RISE Chain (Ethereum L2):

1. **Swap Agent** - Agent that finds the optimal route for token swaps
2. **Phishing Detector Agent** - Agent that performs security analysis of blockchain transactions

## 📁 Project Structure

```
AgentX/
├── app.py                     # Flask backend API
├── swap_agent.py              # Swap Agent - Token swap optimization
├── phishing_agent.py          # Phishing Detector - Security analysis
├── wallet_manager.py          # Wallet connection and transaction management
├── blockchain_integration.py  # Web3 blockchain integration
├── templates/
│   └── index.html            # Legacy HTML chat interface
├── frontend/                 # Modern React + RainbowKit frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx    # Root layout with providers
│   │   │   ├── page.tsx      # Main chat interface
│   │   │   └── providers.tsx # Wagmi & RainbowKit setup
│   │   ├── components/
│   │   │   ├── Navbar.tsx    # Navigation with wallet connect
│   │   │   └── WalletStatus.tsx # Wallet status display
│   │   └── hooks/
│   │       └── useSwap.ts    # Swap transaction hooks
│   ├── package.json          # Node.js dependencies
│   └── .env.local           # Environment variables
├── requirements.txt          # Python dependencies
├── test_cli.py              # CLI test script
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

Modern React frontend: http://localhost:3001
Legacy HTML interface: http://localhost:8000

#### Separate Agents (Optional)

```bash
# Swap Agent (Port 5001)
python swap_agent.py

# Phishing Detector Agent (Port 5002)  
python phishing_agent.py
```

#### CLI Test Script

```bash
python test_cli.py
```

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

### Example Chat Commands

```
"0.1 USDT to ETH"
"1 WETH to USDC"
"5 DAI to USDT"
"Show my wallet balance"
"What tokens are supported?"
"Security information"
"Help"
```

### Real Transaction Flow

1. User writes swap request in chat
2. AI analyzes request with natural language processing
3. Swap Agent finds the best route
4. Phishing Detector performs security analysis
5. Wallet Manager executes real blockchain transaction
6. Result is shown in chat (TX hash + Explorer link)

## 🔄 Swap Agent Usage

### API Endpoints

#### 1. Health Check
```
GET /health
```

#### 2. List Supported Tokens
```
GET /tokens
```

**Response:**
```json
{
  "tokens": ["WETH", "USDC", "USDT", "DAI"],
  "prices": {
    "WETH": 2000.0,
    "USDC": 1.0,
    "USDT": 1.0,
    "DAI": 1.0
  }
}
```

#### 3. Find Best Swap Route
```
POST /find_route
Content-Type: application/json

{
  "token_a": "WETH",
  "token_b": "USDC",
  "amount": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "input_token": "WETH",
  "output_token": "USDC",
  "input_amount": 1.0,
  "route_details": {
    "route": ["WETH", "USDC"],
    "pools": ["Uniswap"],
    "estimated_output": 1995.0,
    "gas_cost_usd": 30.0,
    "net_output": 1965.0,
    "total_fee_rate": 0.003,
    "price_impact": 0.1
  },
  "recommendation": "Direct route available with good liquidity."
}
```

#### 4. List Available Pools
```
GET /pools
```

### Direct Python Usage

```python
from swap_agent import find_best_swap_route

# Find best route
result = find_best_swap_route("WETH", "USDC", 1.0)
print(result)
```

### cURL Examples

```bash
# Token list
curl http://localhost:5001/tokens

# Find swap route
curl -X POST http://localhost:5001/find_route \
  -H "Content-Type: application/json" \
  -d '{
    "token_a": "WETH",
    "token_b": "USDC", 
    "amount": 1.0
  }'
```

## 🛡️ Phishing Detector Agent Usage

### API Endpoints

#### 1. Health Check
```
GET /health
```

#### 2. Transaction Analysis (Main Function)
```
POST /analyze
Content-Type: application/json

{
  "to": "0x1234567890123456789012345678901234567890",
  "from": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
  "value": "0x0",
  "data": "0x095ea7b3000000000000000000000000abcdefabcdefabcdefabcdefabcdefabcdefabcdffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "gas": "0x5208",
  "gasPrice": "0x4a817c800"
}
```

**Response:**
```json
{
  "success": true,
  "risk_score": 75,
  "risk_level": "HIGH",
  "recommendation": "⚠️ HIGH RISK: Carefully review all details before proceeding.",
  "warnings": [
    "DANGER: Known phishing contract",
    "approve: Token approval - check spender and amount",
    "⚠️ CRITICAL: This grants unlimited access to ALL your tokens!"
  ],
  "risk_factors": [
    "Address risk: 90",
    "Function risk: 90"
  ],
  "analysis_timestamp": "2024-01-15T10:30:00.123456",
  "transaction_summary": {
    "to": "0x1234567890123456789012345678901234567890",
    "value_eth": 0.0,
    "function_called": "approve",
    "is_contract_interaction": true
  }
}
```

#### 3. Address Check Only
```
POST /check_address
Content-Type: application/json

{
  "address": "0x1234567890123456789012345678901234567890"
}
```

#### 4. Security Tips
```
GET /security_tips
```

### Direct Python Usage

```python
from phishing_agent import detect_phishing

# Transaction data
transaction_data = {
    "to": "0x1234567890123456789012345678901234567890",
    "value": "0x0",
    "data": "0x095ea7b3...",
    "gas": "0x5208"
}

# Perform analysis
result = detect_phishing(transaction_data)
print(f"Risk Score: {result['risk_score']}")
print(f"Risk Level: {result['risk_level']}")
```

### cURL Examples

```bash
# Transaction analysis
curl -X POST http://localhost:5002/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0x1234567890123456789012345678901234567890",
    "value": "0x0",
    "data": "0x095ea7b3000000000000000000000000abcdefabcdefabcdefabcdefabcdefabcdefabcdffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
  }'

# Address check
curl -X POST http://localhost:5002/check_address \
  -H "Content-Type: application/json" \
  -d '{"address": "0x1234567890123456789012345678901234567890"}'

# Security tips
curl http://localhost:5002/security_tips
```

## 🔗 Main Project Integration

### Backend Integration (Node.js/Express Example)

```javascript
// Call agents in your backend
const axios = require('axios');

// Swap Agent usage
async function findBestRoute(tokenA, tokenB, amount) {
  try {
    const response = await axios.post('http://localhost:5001/find_route', {
      token_a: tokenA,
      token_b: tokenB,
      amount: amount
    });
    return response.data;
  } catch (error) {
    console.error('Swap Agent error:', error.message);
    return null;
  }
}

// Phishing Detector usage
async function analyzeTransaction(txData) {
  try {
    const response = await axios.post('http://localhost:5002/analyze', txData);
    return response.data;
  } catch (error) {
    console.error('Phishing Detector error:', error.message);
    return null;
  }
}

// Usage example
app.post('/api/check-swap', async (req, res) => {
  const { tokenA, tokenB, amount } = req.body;
  const route = await findBestRoute(tokenA, tokenB, amount);
  res.json(route);
});

app.post('/api/analyze-transaction', async (req, res) => {
  const analysis = await analyzeTransaction(req.body);
  res.json(analysis);
});
```

### Frontend Integration (React/JavaScript Example)

```javascript
// Use agents in frontend
class AgentService {
  static async findSwapRoute(tokenA, tokenB, amount) {
    const response = await fetch('/api/check-swap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tokenA, tokenB, amount })
    });
    return response.json();
  }

  static async analyzeTransaction(txData) {
    const response = await fetch('/api/analyze-transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(txData)
    });
    return response.json();
  }
}

// Usage in React component
function SwapComponent() {
  const [route, setRoute] = useState(null);
  
  const handleFindRoute = async () => {
    const result = await AgentService.findSwapRoute('WETH', 'USDC', 1.0);
    setRoute(result);
  };

  return (
    <div>
      <button onClick={handleFindRoute}>Find Best Route</button>
      {route && (
        <div>
          <p>Best Route: {route.route_details.pools.join(' → ')}</p>
          <p>Output: {route.route_details.estimated_output} USDC</p>
          <p>Gas Cost: ${route.route_details.gas_cost_usd}</p>
        </div>
      )}
    </div>
  );
}
```

### Smart Contract Integration

Using agent results in smart contracts:

```solidity
// Example: Automatic swap using Swap Agent result
contract AutoSwap {
    function executeSwap(
        address tokenA,
        address tokenB,
        uint256 amount,
        string memory bestDex
    ) external {
        // Use best DEX info from agent
        if (keccak256(bytes(bestDex)) == keccak256(bytes("Uniswap"))) {
            // Execute swap on Uniswap
            executeUniswapSwap(tokenA, tokenB, amount);
        } else if (keccak256(bytes(bestDex)) == keccak256(bytes("SushiSwap"))) {
            // Execute swap on SushiSwap
            executeSushiSwap(tokenA, tokenB, amount);
        }
    }
}
```

## 📊 Agent Features

### Swap Agent

- ✅ **Multi-DEX Support**: Uniswap, SushiSwap, 1inch
- ✅ **Dijkstra Algorithm**: Optimal route finding
- ✅ **Gas Optimization**: Takes gas costs into account
- ✅ **Price Impact Analysis**: Slippage calculation
- ✅ **Multi-hop Routes**: Up to 3 hops support
- ✅ **Real-time Prices**: Simulated DEX data
- ✅ **Comprehensive Error Handling**: User-friendly error messages with retry options
- ✅ **Network Error Recovery**: Automatic retry mechanisms

### Phishing Detector Agent

- ✅ **Address Analysis**: Malicious address detection
- ✅ **Function Analysis**: Risky function call detection
- ✅ **Approval Control**: Unlimited approval detection
- ✅ **Gas Analysis**: Abnormal gas usage detection
- ✅ **Risk Scoring**: 0-100 risk score
- ✅ **Security Recommendations**: User-friendly warnings

## 🧪 Testing

### Swagger/OpenAPI Documentation

You can use Postman collection or Swagger UI to test agents:

```bash
# Run test scripts
python -m pytest tests/ -v  # (if test files are added)
```

### Manual Testing

```bash
# Terminal 1: Swap Agent
python swap_agent.py

# Terminal 2: Phishing Detector
python phishing_agent.py

# Terminal 3: Test requests
curl http://localhost:5001/health
curl http://localhost:5002/health
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001 5002

# Run both agents
CMD ["bash", "-c", "python swap_agent.py & python phishing_agent.py & wait"]
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agents
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-agents
  template:
    metadata:
      labels:
        app: ai-agents
    spec:
      containers:
      - name: swap-agent
        image: ai-agents:latest
        ports:
        - containerPort: 5001
      - name: phishing-agent
        image: ai-agents:latest
        ports:
        - containerPort: 5002
```

## 📈 Advanced Features (Future Versions)

### Swap Agent Improvements

- [ ] Real DEX API integrations
- [ ] MEV protection
- [ ] Arbitrage opportunity detection
- [ ] Limit order support
- [ ] Cross-chain swaps

### Phishing Detector Improvements

- [ ] Machine Learning model integration
- [ ] Real-time threat intelligence
- [ ] NFT metadata analysis
- [ ] Social engineering pattern detection
- [ ] Community-based reporting

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