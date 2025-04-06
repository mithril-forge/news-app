/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";

/** @type {import("next").NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
      remotePatterns: [
        {
          protocol: 'https',
          hostname: 'placehold.co',
        },
        // Add this if you are using the wikimedia link
        {
           protocol: 'https',
           hostname: 't3.ftcdn.net',
        },
        // Add any other domains you might be using
      ],
    },
  };

export default nextConfig;
