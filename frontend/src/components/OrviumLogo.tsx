'use client';

import React from 'react';

interface OrviumLogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export default function OrviumLogo({ className = '', size = 'md' }: OrviumLogoProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div className={`${sizeClasses[size]} ${className} relative group`}>
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full drop-shadow-lg"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Background Circle */}
        <circle
          cx="50"
          cy="50"
          r="48"
          fill="url(#gradient1)"
          className="group-hover:scale-105 transition-transform duration-300"
        />
        
        {/* Tool Handle */}
        <rect
          x="45"
          y="15"
          width="10"
          height="25"
          rx="5"
          fill="white"
          className="animate-pulse"
        />
        
        {/* Tool Head - Hexagonal Shape */}
        <path
          d="M35 40 L50 35 L65 40 L65 60 L50 65 L35 60 Z"
          fill="white"
          stroke="rgba(255,255,255,0.8)"
          strokeWidth="2"
          className="group-hover:rotate-12 transition-transform duration-500"
        />
        
        {/* Inner Tool Pattern */}
        <circle
          cx="50"
          cy="50"
          r="8"
          fill="url(#gradient2)"
          className="animate-pulse"
        />
        
        {/* Tool Details - Gear teeth */}
        <path
          d="M50 42 L52 38 L48 38 Z"
          fill="rgba(255,255,255,0.6)"
        />
        <path
          d="M58 50 L62 52 L62 48 Z"
          fill="rgba(255,255,255,0.6)"
        />
        <path
          d="M50 58 L48 62 L52 62 Z"
          fill="rgba(255,255,255,0.6)"
        />
        <path
          d="M42 50 L38 48 L38 52 Z"
          fill="rgba(255,255,255,0.6)"
        />
        
        {/* Rise Elements - Ascending Lines */}
        <path
          d="M25 70 L30 65 L35 68 L40 63"
          stroke="rgba(255,255,255,0.7)"
          strokeWidth="2"
          strokeLinecap="round"
          className="animate-pulse"
        />
        <path
          d="M60 63 L65 68 L70 65 L75 70"
          stroke="rgba(255,255,255,0.7)"
          strokeWidth="2"
          strokeLinecap="round"
          className="animate-pulse"
        />
        
        {/* Tech Dots */}
        <circle cx="30" cy="30" r="2" fill="rgba(255,255,255,0.6)" />
        <circle cx="70" cy="30" r="2" fill="rgba(255,255,255,0.6)" />
        <circle cx="25" cy="50" r="2" fill="rgba(255,255,255,0.6)" />
        <circle cx="75" cy="50" r="2" fill="rgba(255,255,255,0.6)" />
        
        {/* Gradients */}
        <defs>
          <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#374151" />
            <stop offset="50%" stopColor="#6B46C1" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#9333EA" stopOpacity="0.6" />
          </linearGradient>
          <radialGradient id="gradient2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#A855F7" />
            <stop offset="100%" stopColor="#6B46C1" />
          </radialGradient>
        </defs>
      </svg>
      
      {/* Glow Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-full blur-sm -z-10 group-hover:blur-md transition-all duration-300"></div>
    </div>
  );
}
