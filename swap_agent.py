"""
Swap Agent - Token Swap Optimization
EthIstanbul Hackathon Project
"""

import json
import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Pool:
    """Liquidity pool information"""
    name: str
    token_a: str
    token_b: str
    reserve_a: float
    reserve_b: float
    fee: float  # Percentage (e.g. 0.3 = 0.3%)
    dex: str  # "uniswap", "sushiswap", "1inch"

@dataclass
class SwapRoute:
    """Swap route information"""
    path: List[str]
    pools: List[str]
    estimated_output: float
    price_impact: float
    gas_cost_usd: float
    total_fee: float

class SwapAgent:
    def __init__(self):
        """Initialize Swap Agent"""
        
        # Supported tokens (including ETH for user input) - USDT kaldırıldı
        self.supported_tokens = ['WETH', 'ETH', 'USDC', 'RISE']
        
        # Token prices (simulated) - USDT kaldırıldı
        self.token_prices = {
            'WETH': 2000.0,
            'ETH': 2000.0,  # Same as WETH
            'USDC': 1.0,
            'RISE': 0.05  # RISE token fiyatı
        }
        
        # Liquidity pools (simulated)
        self.pools = self._initialize_pools()
        
        print("🔄 Swap Agent initialized with", len(self.pools), "pools")
    
    def _initialize_pools(self) -> List[Pool]:
        """Initialize liquidity pools"""
        pools = []
        
        # Uniswap V2 style pools - USDT pool'ları kaldırıldı
        uniswap_pools = [
            Pool("WETH/USDC", "WETH", "USDC", 1000, 2000000, 0.3, "uniswap"),
            Pool("WETH/RISE", "WETH", "RISE", 100, 4000000, 0.3, "uniswap"),
            Pool("USDC/RISE", "USDC", "RISE", 50000, 1000000, 0.3, "uniswap"),
        ]
        
        # SushiSwap pools - USDT pool'ları kaldırıldı
        sushiswap_pools = [
            Pool("WETH/USDC", "WETH", "USDC", 800, 1600000, 0.25, "sushiswap"),
            Pool("RISE/USDC", "RISE", "USDC", 2000000, 100000, 0.25, "sushiswap"),
        ]
        
        # 1inch aggregator pools - USDT pool'ları kaldırıldı
        oneinch_pools = [
            Pool("WETH/USDC", "WETH", "USDC", 1200, 2400000, 0.1, "1inch"),
            Pool("RISE/WETH", "RISE", "WETH", 5000000, 125, 0.2, "1inch"),
        ]
        
        pools.extend(uniswap_pools)
        pools.extend(sushiswap_pools)
        pools.extend(oneinch_pools)
        
        return pools
    
    def get_all_tokens(self) -> List[str]:
        """Return all supported tokens"""
        return self.supported_tokens.copy()
    
    def find_best_swap_route(self, from_token: str, to_token: str, amount: float) -> Dict:
        """
        Find the best swap route
        
        Args:
            from_token: Source token
            to_token: Target token
            amount: Amount to swap
            
        Returns:
            Dict: Route details and results
        """
        
        # Convert ETH to WETH for routing (ETH and WETH are equivalent for swaps)
        routing_from_token = 'WETH' if from_token == 'ETH' else from_token
        routing_to_token = 'WETH' if to_token == 'ETH' else to_token
        
        if routing_from_token not in self.supported_tokens or routing_to_token not in self.supported_tokens:
            return {
                'success': False,
                'error': f'Unsupported token: {from_token} or {to_token}',
                'supported_tokens': self.supported_tokens
            }
        
        if routing_from_token == routing_to_token:
            return {
                'success': False,
                'error': 'Source and target token cannot be the same'
            }
        
        if amount <= 0:
            return {
                'success': False,
                'error': 'Amount must be greater than 0'
            }
        
        try:
            # Direkt swap rotalarını bul (routing tokens kullan)
            direct_routes = self._find_direct_routes(routing_from_token, routing_to_token, amount)
            
            # Multi-hop rotalarını bul (routing tokens kullan)
            multi_hop_routes = self._find_multi_hop_routes(routing_from_token, routing_to_token, amount)
            
            # Tüm rotaları birleştir
            all_routes = direct_routes + multi_hop_routes
            
            if not all_routes:
                return {
                    'success': False,
                    'error': 'Bu token çifti için rota bulunamadı',
                    'suggestion': 'Farklı tokenlar deneyin veya miktarı azaltın'
                }
            
            # En iyi rotayı seç (en yüksek output)
            best_route = max(all_routes, key=lambda r: r.estimated_output)
            
            return {
                'success': True,
                'route_details': {
                    'path': best_route.path,
                    'pools': best_route.pools,
                    'estimated_output': best_route.estimated_output,
                    'price_impact': best_route.price_impact,
                    'gas_cost_usd': best_route.gas_cost_usd,
                    'total_fee': best_route.total_fee,
                    'input_amount': amount,
                    'input_token': from_token,
                    'output_token': to_token,
                    'exchange_rate': best_route.estimated_output / amount,
                    'minimum_output': best_route.estimated_output * 0.995,  # %0.5 slippage
                    'route_type': 'direct' if len(best_route.path) == 2 else 'multi-hop'
                },
                'alternatives': [
                    {
                        'path': route.path,
                        'estimated_output': route.estimated_output,
                        'dex': route.pools[0] if route.pools else 'unknown'
                    } for route in sorted(all_routes, key=lambda r: r.estimated_output, reverse=True)[:3]
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Rota hesaplama hatası: {str(e)}',
                'suggestion': 'Lütfen tekrar deneyin'
            }
    
    def _find_direct_routes(self, from_token: str, to_token: str, amount: float) -> List[SwapRoute]:
        """Direkt swap rotalarını bul"""
        routes = []
        
        for pool in self.pools:
            if (pool.token_a == from_token and pool.token_b == to_token) or \
               (pool.token_a == to_token and pool.token_b == from_token):
                
                # Çıkış miktarını hesapla (constant product formula)
                if pool.token_a == from_token:
                    reserve_in, reserve_out = pool.reserve_a, pool.reserve_b
                else:
                    reserve_in, reserve_out = pool.reserve_b, pool.reserve_a
                
                # AMM formula: dy = (y * dx * 997) / (x * 1000 + dx * 997)
                # Fee'yi hesaba kat
                fee_multiplier = (10000 - pool.fee * 100) / 10000
                amount_with_fee = amount * fee_multiplier
                
                output_amount = (reserve_out * amount_with_fee) / (reserve_in + amount_with_fee)
                
                # Price impact hesapla
                price_impact = (amount / reserve_in) * 100
                
                # Gas cost (simüle edilmiş) - düşük maliyet
                gas_cost_usd = self._estimate_gas_cost('direct')
                
                route = SwapRoute(
                    path=[from_token, to_token],
                    pools=[f"{pool.dex}:{pool.name}"],
                    estimated_output=output_amount,
                    price_impact=price_impact,
                    gas_cost_usd=gas_cost_usd,
                    total_fee=pool.fee
                )
                
                routes.append(route)
        
        return routes
    
    def _find_multi_hop_routes(self, from_token: str, to_token: str, amount: float) -> List[SwapRoute]:
        """Multi-hop swap rotalarını bul (örn: WETH -> USDC -> DAI)"""
        routes = []
        
        # Yaygın intermediate token'lar
        intermediate_tokens = ['WETH', 'USDC', 'USDT']
        
        for intermediate in intermediate_tokens:
            if intermediate == from_token or intermediate == to_token:
                continue
            
            # İlk hop: from_token -> intermediate
            first_hop_routes = self._find_direct_routes(from_token, intermediate, amount)
            
            for first_route in first_hop_routes:
                if first_route.estimated_output <= 0:
                    continue
                
                # İkinci hop: intermediate -> to_token
                second_hop_routes = self._find_direct_routes(
                    intermediate, to_token, first_route.estimated_output
                )
                
                for second_route in second_hop_routes:
                    if second_route.estimated_output <= 0:
                        continue
                    
                    # Multi-hop rotasını oluştur
                    combined_route = SwapRoute(
                        path=[from_token, intermediate, to_token],
                        pools=first_route.pools + second_route.pools,
                        estimated_output=second_route.estimated_output,
                        price_impact=first_route.price_impact + second_route.price_impact,
                        gas_cost_usd=self._estimate_gas_cost('multi-hop'),
                        total_fee=first_route.total_fee + second_route.total_fee
                    )
                    
                    routes.append(combined_route)
        
        return routes
    
    def _estimate_gas_cost(self, route_type: str) -> float:
        """Estimate gas cost (USD) - low cost"""
        base_gas = {
            'direct': 50000,   # Low gas units
            'multi-hop': 100000
        }
        
        # Low gas price (5 gwei) and ETH price
        gas_price_gwei = 5
        eth_price = self.token_prices['WETH']
        
        gas_cost_eth = (base_gas[route_type] * gas_price_gwei) / 1e9
        gas_cost_usd = gas_cost_eth * eth_price
        
        return gas_cost_usd
    
    def get_token_price(self, token: str) -> float:
        """Return token price"""
        return self.token_prices.get(token, 0.0)
    
    def simulate_price_impact(self, from_token: str, to_token: str, amounts: List[float]) -> Dict:
        """Simulate price impact for different amounts"""
        results = []
        
        for amount in amounts:
            route_result = self.find_best_swap_route(from_token, to_token, amount)
            
            if route_result['success']:
                results.append({
                    'amount': amount,
                    'output': route_result['route_details']['estimated_output'],
                    'price_impact': route_result['route_details']['price_impact'],
                    'gas_cost': route_result['route_details']['gas_cost_usd']
                })
        
        return {
            'token_pair': f"{from_token}/{to_token}",
            'simulations': results,
            'recommendations': self._generate_amount_recommendations(results)
        }
    
    def _generate_amount_recommendations(self, simulations: List[Dict]) -> List[str]:
        """Generate amount recommendations"""
        recommendations = []
        
        for sim in simulations:
            if sim['price_impact'] > 5:
                recommendations.append(f"⚠️ Price impact too high for {sim['amount']} ({sim['price_impact']:.2f}%)")
            elif sim['price_impact'] < 1:
                recommendations.append(f"✅ Optimal price impact for {sim['amount']} ({sim['price_impact']:.2f}%)")
        
        return recommendations

# Test fonksiyonu
if __name__ == "__main__":
    agent = SwapAgent()
    
    # Test swap
    result = agent.find_best_swap_route("WETH", "USDC", 1.0)
    print(json.dumps(result, indent=2))
    
    # Price impact simülasyonu
    impact_result = agent.simulate_price_impact("WETH", "USDC", [0.1, 1.0, 10.0])
    print(json.dumps(impact_result, indent=2))
