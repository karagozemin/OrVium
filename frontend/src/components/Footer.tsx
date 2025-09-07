'use client';

import React from 'react';
import OrviumLogo from './OrviumLogo';

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-black/20 backdrop-blur-sm animate-fade-in">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-3">
            <OrviumLogo size="sm" />
            <span className="text-sm font-semibold text-white">Orvium Rise Tool</span>
            <span className="text-xs text-gray-400">•</span>
            <span className="text-xs text-gray-400">RISE Chain Testnet</span>
          </div>
          
          <div className="flex items-center space-x-6">
            <a
              href="https://x.com/0xorvium"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition-all duration-200 group hover:scale-105"
            >
              <svg 
                className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" 
                fill="currentColor" 
                viewBox="0 0 24 24"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
              <span className="text-sm">@0xorvium</span>
            </a>
            
            <div className="text-xs text-gray-500">
              © 2024 Orvium Labs
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
