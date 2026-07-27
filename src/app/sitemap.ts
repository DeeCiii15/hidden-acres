import type { MetadataRoute } from "next";
import {
  getAllWeddingSlugs,
  portfolioPath,
} from "@/lib/portfolioData";
import { getLiveLocations } from "@/lib/locations";
import {
  ABOUT_PATH,
  CONTACT_PATH,
  getSiteUrl,
  PORTFOLIO_PATH,
  VENUE_PATH,
  WEDDING_PATH,
} from "@/lib/siteConfig";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = getSiteUrl();
  const now = new Date();

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${base}/`, lastModified: now, changeFrequency: "weekly", priority: 1 },
    {
      url: `${base}${VENUE_PATH}`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.95,
    },
    {
      url: `${base}${WEDDING_PATH}`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${base}${PORTFOLIO_PATH}`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.85,
    },
    {
      url: `${base}${ABOUT_PATH}`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${base}${CONTACT_PATH}`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.9,
    },
  ];

  const portfolio = getAllWeddingSlugs().map((slug) => ({
    url: `${base}${portfolioPath(slug)}`,
    lastModified: now,
    changeFrequency: "monthly" as const,
    priority: 0.7,
  }));

  const locations = getLiveLocations().map((loc) => ({
    url: `${base}${loc.path}`,
    lastModified: now,
    changeFrequency: "monthly" as const,
    priority: 0.85,
  }));

  return [...staticRoutes, ...portfolio, ...locations];
}
