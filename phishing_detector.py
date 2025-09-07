"""
Phishing Detector - Free & Reliable
EthIstanbul Hackathon Project
Multi-source threat intelligence with GoPlus + EtherScamDB
"""

import asyncio
import aiohttp
import json
import os
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

class FreePhishingDetector:
    """
    Ücretsiz ve güvenilir phishing detector
    GoPlus Security API + EtherScamDB + Local Intelligence
    """
    
    def __init__(self):
        # API endpoints (ücretsiz)
        self.goplus_api = "https://api.gopluslabs.io/api/v1/address_security"
        self.etherscamdb_api = "https://api.etherscamdb.info/v1/scams"
        
        # Cache system
        self._cache = {}
        self._cache_ttl = 300  # 5 dakika cache
        
        # Rate limiting (ücretsiz tier limits)
        self._last_request = {}
        self._min_interval = 1  # 1 saniye minimum interval
        
        # Local blacklist (bilinen scam adresleri)
        self.local_blacklist = {
            # Bilinen phishing adresleri (örnekler)
            '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',  # Fake Uniswap
            '0x514910771af9ca656af840dff83e8264ecf986ca',  # Suspicious contract
        }
        
        # EtherScamDB cache
        self.scam_database = None
        self.scam_db_last_update = 0
        
        print("🛡️ Free Phishing Detector initialized")
        print("📡 Sources: GoPlus Security + EtherScamDB + Local Intelligence")
    
    async def verify_address(self, address: str) -> Dict:
        """
        Ana verify fonksiyonu - chat'ten çağrılacak
        """
        try:
            # Address format kontrolü
            if not self._validate_address_format(address):
                return {
                    'address': address,
                    'is_safe': False,
                    'risk_level': 'invalid',
                    'risk_score': 100,
                    'warnings': ['Invalid Ethereum address format'],
                    'recommendations': ['Please check the address format (0x + 40 hex characters)'],
                    'sources_checked': ['format_validation'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Cache kontrolü
            cache_key = f"verify_{address.lower()}"
            if self._check_cache(cache_key):
                cached_result = self._cache[cache_key]['data']
                cached_result['from_cache'] = True
                return cached_result
            
            print(f"🔍 Verifying address: {address}")
            
            # Paralel kontroller
            tasks = [
                self._check_local_blacklist(address),
                self._check_goplus_security(address),
                self._check_etherscamdb(address)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sonuçları birleştir
            analysis = self._combine_results(address, results)
            
            # Cache'e kaydet
            self._cache[cache_key] = {
                'data': analysis,
                'timestamp': time.time()
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Verification error: {str(e)}")
            return {
                'address': address,
                'is_safe': False,
                'risk_level': 'error',
                'risk_score': 50,
                'warnings': [f'Verification failed: {str(e)}'],
                'recommendations': ['Manual verification recommended'],
                'sources_checked': ['error'],
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def _check_local_blacklist(self, address: str) -> Dict:
        """Local blacklist kontrolü"""
        try:
            result = {
                'source': 'local_blacklist',
                'risk_score': 0,
                'warnings': [],
                'details': {}
            }
            
            if address.lower() in [addr.lower() for addr in self.local_blacklist]:
                result['risk_score'] = 100
                result['warnings'].append('Address found in local blacklist')
                result['details']['blacklist_reason'] = 'Known phishing/scam address'
            
            # Pattern analizi
            if self._analyze_suspicious_patterns(address):
                result['risk_score'] += 30
                result['warnings'].append('Suspicious address pattern detected')
            
            return result
            
        except Exception as e:
            return {'source': 'local_blacklist', 'error': str(e), 'risk_score': 0}
    
    async def _check_goplus_security(self, address: str) -> Dict:
        """GoPlus Security API kontrolü"""
        try:
            # Rate limiting
            if not self._check_rate_limit('goplus'):
                await asyncio.sleep(1)
            
            params = {
                'chain_id': '1',  # Ethereum mainnet
                'addresses': address
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.goplus_api, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                    else:
                        raise Exception(f"GoPlus API error: {response.status}")
            
            result = {
                'source': 'goplus_security',
                'risk_score': 0,
                'warnings': [],
                'details': {}
            }
            
            if data.get('code') == 1 and address in data.get('result', {}):
                addr_data = data['result'][address]
                
                # Phishing kontrolü
                if addr_data.get('is_phishing') == 1:
                    result['risk_score'] = 95
                    result['warnings'].append('PHISHING ADDRESS detected by GoPlus')
                
                # Honeypot kontrolü
                if addr_data.get('is_honeypot') == 1:
                    result['risk_score'] += 80
                    result['warnings'].append('Honeypot contract detected')
                
                # Malicious behavior kontrolü
                malicious_behaviors = addr_data.get('malicious_behavior', [])
                if malicious_behaviors:
                    result['risk_score'] += len(malicious_behaviors) * 20
                    for behavior in malicious_behaviors:
                        result['warnings'].append(f'Malicious behavior: {behavior}')
                
                # Contract analizi
                if addr_data.get('is_contract') == 1:
                    result['details']['is_contract'] = True
                    if addr_data.get('is_proxy') == 1:
                        result['risk_score'] += 15
                        result['warnings'].append('Proxy contract detected')
                    
                    # Trust list kontrolü
                    trust_list = addr_data.get('trust_list', 0)
                    if trust_list == 1:
                        result['risk_score'] = max(0, result['risk_score'] - 30)
                        result['warnings'].append('Contract in GoPlus trust list')
                
                result['details']['goplus_data'] = addr_data
            
            self._update_rate_limit('goplus')
            return result
            
        except Exception as e:
            print(f"⚠️ GoPlus API error: {str(e)}")
            return {'source': 'goplus_security', 'error': str(e), 'risk_score': 10}
    
    async def _check_etherscamdb(self, address: str) -> Dict:
        """EtherScamDB kontrolü"""
        try:
            # Scam database'i güncelle (24 saatte bir)
            if not self.scam_database or (time.time() - self.scam_db_last_update) > 86400:
                await self._update_scam_database()
            
            result = {
                'source': 'etherscamdb',
                'risk_score': 0,
                'warnings': [],
                'details': {}
            }
            
            if self.scam_database:
                # Adres kontrolü
                for scam in self.scam_database.get('result', []):
                    if scam.get('addresses'):
                        for scam_addr in scam['addresses']:
                            if scam_addr.lower() == address.lower():
                                result['risk_score'] = 100
                                result['warnings'].append(f'SCAM detected: {scam.get("name", "Unknown")}')
                                result['details']['scam_type'] = scam.get('category', 'Unknown')
                                result['details']['scam_name'] = scam.get('name', 'Unknown')
                                break
                    
                    if result['risk_score'] > 0:
                        break
            
            return result
            
        except Exception as e:
            print(f"⚠️ EtherScamDB error: {str(e)}")
            return {'source': 'etherscamdb', 'error': str(e), 'risk_score': 5}
    
    async def _update_scam_database(self):
        """EtherScamDB database'ini güncelle"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.etherscamdb_api, timeout=30) as response:
                    if response.status == 200:
                        self.scam_database = await response.json()
                        self.scam_db_last_update = time.time()
                        print("✅ EtherScamDB updated successfully")
                    else:
                        print(f"⚠️ EtherScamDB update failed: {response.status}")
        except Exception as e:
            print(f"❌ EtherScamDB update error: {str(e)}")
    
    def _combine_results(self, address: str, results: List) -> Dict:
        """Tüm kaynaklardan gelen sonuçları birleştir"""
        analysis = {
            'address': address,
            'timestamp': datetime.now().isoformat(),
            'overall_risk_score': 0,
            'risk_level': 'low',
            'is_safe': True,
            'warnings': [],
            'recommendations': [],
            'sources_checked': [],
            'source_details': {},
            'confidence': 0.0
        }
        
        total_risk = 0
        active_sources = 0
        
        for result in results:
            if isinstance(result, Exception):
                continue
            
            if isinstance(result, dict) and 'source' in result:
                source = result['source']
                analysis['sources_checked'].append(source)
                
                if 'error' not in result:
                    risk_score = result.get('risk_score', 0)
                    total_risk += risk_score
                    active_sources += 1
                    
                    # Warnings'leri topla
                    if 'warnings' in result:
                        analysis['warnings'].extend(result['warnings'])
                    
                    # Source details'i kaydet
                    analysis['source_details'][source] = result
        
        # Overall risk score hesapla
        if active_sources > 0:
            analysis['overall_risk_score'] = min(100, total_risk / active_sources)
            analysis['confidence'] = min(1.0, active_sources / 3)  # 3 source var
        
        # Risk level belirle
        if analysis['overall_risk_score'] >= 80:
            analysis['risk_level'] = 'critical'
            analysis['is_safe'] = False
        elif analysis['overall_risk_score'] >= 60:
            analysis['risk_level'] = 'high'
            analysis['is_safe'] = False
        elif analysis['overall_risk_score'] >= 30:
            analysis['risk_level'] = 'medium'
            analysis['is_safe'] = False
        else:
            analysis['risk_level'] = 'low'
            analysis['is_safe'] = True
        
        # Recommendations oluştur
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Risk seviyesine göre öneriler oluştur"""
        recommendations = []
        risk_score = analysis['overall_risk_score']
        
        if risk_score >= 80:
            recommendations.extend([
                "DO NOT INTERACT with this address",
                "Block this address in your wallet",
                "Report to security team if you received tokens from this address",
                "Check if you have any pending transactions with this address"
            ])
        elif risk_score >= 60:
            recommendations.extend([
                "HIGH RISK - Avoid transactions with this address",
                "Verify the address through official channels",
                "Never send large amounts to this address",
                "Document any interactions for security review"
            ])
        elif risk_score >= 30:
            recommendations.extend([
                "MEDIUM RISK - Exercise caution",
                "Double-check address with the recipient",
                "Consider using smaller amounts for testing",
                "Monitor transactions closely"
            ])
        else:
            recommendations.extend([
                "Address appears safe based on available data",
                "Continue with normal security practices",
                "Regular monitoring is still recommended"
            ])
        
        # Source-specific recommendations
        if len(analysis['sources_checked']) < 2:
            recommendations.append("Limited data sources - consider additional verification")
        
        return recommendations
    
    def _validate_address_format(self, address: str) -> bool:
        """Ethereum address format kontrolü"""
        if not address:
            return False
        
        # 0x ile başlamalı ve 42 karakter olmalı
        if not address.startswith('0x') or len(address) != 42:
            return False
        
        # Hex karakterler kontrolü
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False
    
    def _analyze_suspicious_patterns(self, address: str) -> bool:
        """Şüpheli adres pattern'lerini analiz et"""
        # Çok fazla sıfır (vanity address attack)
        if address.count('0') > 35:
            return True
        
        # Tekrarlayan karakterler
        for char in '0123456789abcdef':
            if address.lower().count(char) > 30:
                return True
        
        return False
    
    def _check_rate_limit(self, source: str) -> bool:
        """Rate limit kontrolü"""
        now = time.time()
        if source in self._last_request:
            return (now - self._last_request[source]) >= self._min_interval
        return True
    
    def _update_rate_limit(self, source: str):
        """Rate limit güncelle"""
        self._last_request[source] = time.time()
    
    def _check_cache(self, key: str) -> bool:
        """Cache kontrolü"""
        if key in self._cache:
            cache_time = self._cache[key]['timestamp']
            return (time.time() - cache_time) < self._cache_ttl
        return False

# Global instance
phishing_detector = FreePhishingDetector()

# Test function
async def test_detector():
    """Test function"""
    test_addresses = [
        '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',  # Uniswap token (safe)
        '0x0000000000000000000000000000000000000000',  # Null address
        '0x742d35Cc6634C0532925a3b8D5C2d3b5c5b5b5b5',  # Random address
    ]
    
    for addr in test_addresses:
        print(f"\n🔍 Testing: {addr}")
        result = await phishing_detector.verify_address(addr)
        print(f"✅ Result: {result['risk_level']} risk, Score: {result['overall_risk_score']}")
        for warning in result['warnings'][:2]:  # İlk 2 warning'i göster
            print(f"⚠️ {warning}")

if __name__ == "__main__":
    # Test çalıştır
    asyncio.run(test_detector())
