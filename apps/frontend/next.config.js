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
  webpack: (config) => {
    // Resolve @ alias to current directory
    // When rootDirectory is set to apps/frontend, __dirname points to apps/frontend
    const rootPath = path.resolve(__dirname)
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': rootPath,
    }
    // Debug logging (will show in build logs)
    console.log('Webpack alias configured:', {
      '@': rootPath,
      libExists: require('fs').existsSync(path.join(rootPath, 'lib', 'api-client.ts')),
      utilsExists: require('fs').existsSync(path.join(rootPath, 'lib', 'utils.ts')),
    })
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
