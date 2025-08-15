/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";

/** @type {import("next").NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/((?!_next/static|favicon.ico).*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
        ],
      },
    ];
  },
  reactStrictMode: true,

  // Use standalone build for better Docker production performance
  output: 'standalone',

  // Optimize for production
  compress: true,

  // Skip type checking during build (we can run it separately)
  typescript: {
    ignoreBuildErrors: true,
  },

  // Skip ESLint during build (we can run it separately)
  eslint: {
    ignoreDuringBuilds: true,
  },

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'placehold.co',
      },
      {
        protocol: 'https',
        hostname: 't3.ftcdn.net',
      },
      {
        protocol: 'https',
        hostname: 'st2.depositphotos.com'
      }
    ],
  },
};

export default nextConfig;
