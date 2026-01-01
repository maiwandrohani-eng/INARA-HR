const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  experimental: {
    serverActions: true,
  },
  webpack: (config) => {
    const rootPath = path.resolve(__dirname)
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': rootPath,
      '@/lib': path.join(rootPath, 'lib'),
      '@/components': path.join(rootPath, 'components'),
      '@/services': path.join(rootPath, 'services'),
      '@/hooks': path.join(rootPath, 'hooks'),
      '@/state': path.join(rootPath, 'state'),
    }
    return config
  },
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'https',
        hostname: 'nyc3.digitaloceanspaces.com',
      },
      {
        protocol: 'https',
        hostname: 'hrmis.inara.ngo', // Cloudflare R2
      },
      {
        protocol: 'https',
        hostname: '*.r2.cloudflarestorage.com', // Cloudflare R2 endpoints
      },
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
}

module.exports = nextConfig
