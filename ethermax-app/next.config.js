/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        domains: ['localhost'],
    },
    webpack: (config, { isServer }) => {
        if (isServer) {
            // Polyfill indexedDB for SSR
            config.resolve.fallback = {
                ...config.resolve.fallback,
                indexedDB: require.resolve('indexeddbshim'),
            };
        }
        return config;
    },
}

module.exports = nextConfig
