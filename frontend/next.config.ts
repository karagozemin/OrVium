import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Fix external API calls
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8003/api/:path*',
      },
    ]
  },
  
  // Disable image optimization for development
  images: {
    unoptimized: true,
  },
  
  // Experimental features (Turbopack compatible)
  experimental: {
    disableOptimizedLoading: true,
  },
};

export default nextConfig;
