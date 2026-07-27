import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    qualities: [75, 90, 92, 95],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "images.squarespace-cdn.com",
      },
    ],
  },
  async redirects() {
    return [
      // New IA destinations
      { source: "/faqs", destination: "/about#faq", permanent: true },
      { source: "/directions", destination: "/about#directions", permanent: true },
      { source: "/preferred-vendors", destination: "/about#vendors", permanent: true },
      { source: "/your-wedding", destination: "/wedding", permanent: true },
      {
        source: "/pricing-amenities",
        destination: "/wedding",
        permanent: true,
      },
      { source: "/contact-us", destination: "/contact", permanent: true },

      // Space pages → venue tour anchors
      { source: "/the-chapel", destination: "/venue#the-chapel", permanent: true },
      {
        source: "/the-ceremony-pond",
        destination: "/venue#ceremony-pond",
        permanent: true,
      },
      { source: "/the-ballroom", destination: "/venue#the-ballroom", permanent: true },
      {
        source: "/the-courtyard-pavilion",
        destination: "/venue#courtyard-pavilion",
        permanent: true,
      },
      {
        source: "/the-rusted-silo",
        destination: "/venue#rusted-silo",
        permanent: true,
      },
      { source: "/the-inn", destination: "/venue#the-inn", permanent: true },
      {
        source: "/the-bridalsuite",
        destination: "/venue#bridal-suite-salon",
        permanent: true,
      },
      {
        source: "/the-cabin-grooms-cave",
        destination: "/venue#grooms-quarters",
        permanent: true,
      },
      {
        source: "/venue-video",
        destination: "/venue#video-tour",
        permanent: true,
      },

      // Retired service / gallery routes
      { source: "/services", destination: "/venue", permanent: true },
      { source: "/services/:slug*", destination: "/venue", permanent: true },
      { source: "/gallery", destination: "/portfolio", permanent: true },
      { source: "/gallery/:path*", destination: "/portfolio", permanent: true },

      // Retired placeholder portfolio slugs
      {
        source: "/portfolio/krista-colton",
        destination: "/portfolio",
        permanent: true,
      },
      {
        source: "/portfolio/ak-weekend",
        destination: "/portfolio",
        permanent: true,
      },
      {
        source: "/portfolio/lights-on-the-lawn",
        destination: "/portfolio",
        permanent: true,
      },
      {
        source: "/portfolio/classic-hidden-acres",
        destination: "/portfolio",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
