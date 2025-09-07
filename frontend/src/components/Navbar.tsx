'use client';

import React from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import OrviumLogo from './OrviumLogo';

export default function Navbar() {
  return (
    <div className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-black/30 bg-black/30 border-b border-white/10">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <div className="flex items-center space-x-3 group cursor-pointer">
          <OrviumLogo size="md" className="group-hover:scale-110 transition-transform duration-200" />
          <span className="text-sm font-semibold text-white group-hover:text-purple-200 transition-colors duration-200">Orvium Rise Tool</span>
        </div>
        <div className="flex items-center">
          <ConnectButton showBalance={false} chainStatus="icon" accountStatus={{ smallScreen: 'avatar', largeScreen: 'full' }} />
        </div>
      </div>
    </div>
  );
}
