import type { NextConfig } from "next";

type RemotePattern = NonNullable<NonNullable<NextConfig["images"]>["remotePatterns"]>[number]

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5050/api";
const apiOrigin = apiUrl.replace(/\/api\/?$/, "");

const remotePatterns = (() => {
  try {
    const url = new URL(apiOrigin);

    return [
      {
        protocol: url.protocol.replace(":", ""),
        hostname: url.hostname,
        port: url.port,
        pathname: "/**",
      } as RemotePattern,
    ];
  } catch {
    return [];
  }
})();

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      ...remotePatterns,
      {
        protocol: "http",
        hostname: "localhost",
        port: "5050",
        pathname: "/**",
      } as RemotePattern,
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "5050",
        pathname: "/**",
      } as RemotePattern,
    ],
  },
};

export default nextConfig;
