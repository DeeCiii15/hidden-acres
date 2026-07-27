export const SITE_NAME = "Hidden Acres";
export const SITE_TAGLINE = "Rustic charm & Southern hospitality";
export const SITE_MOOD =
  "Soft evenings, open acres, warmth that feels like home.";
export const CANONICAL_SITE_URL = "https://www.hiddenacresweddings.com";

export const PRIMARY_CITY = "Marion";
export const PRIMARY_REGION = "SC";
export const PRIMARY_STATE = "South Carolina";
export const PRIMARY_STATE_ABBR = "SC";

export const ADDRESS = {
  street: "6701 Ella Grace Court",
  city: "Marion",
  state: "SC",
  zip: "29571",
  full: "6701 Ella Grace Court, Marion, SC 29571",
  gateNote: "Hidden Acres Gate on Dew Road",
};

export const CONTACT = {
  email: "info@hiddenacresweddings.com",
  phoneDisplay: "(843) 430-0332",
  phoneHref: "tel:+18434300332",
};

export const SOCIAL = {
  instagram: "https://www.instagram.com/hiddenacresmarionsc/",
  facebook:
    "https://www.facebook.com/Hidden-Acres-Marion-SC-113791305421192/",
  pinterest: "https://www.pinterest.com/hiddenacressc/",
};

/** Shared prompt for the Love Letters review / award logo group */
export const REVIEWS_CAPTION = "Check out what people say about us";

/** Review / award destinations shown under Love Letters */
export const REVIEWS = {
  theKnot: {
    href: "https://www.theknot.com/marketplace/hidden-acres-marion-sc-1025516",
    label: "The Knot — Hidden Acres reviews & listing",
    logo: "/brand/the-knot.svg",
  },
  google: {
    // Search deep-link that opens the venue’s Google reviews panel (#lrd=…)
    href: "https://www.google.com/search?q=hidden+acres+google+reveiws&rlz=1C1GCEJ_enUS874US874&oq=hidden+acres+google+reveiws&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIJCAEQIRgKGKABMgkIAhAhGAoYoAEyCQgDECEYChigATIJCAQQIRgKGKABMgkIBRAhGAoYoAEyBwgGECEYqwIyBwgHECEYnwUyBwgIECEYnwUyBwgJECEYjwLSAQgzMzI2ajBqNKgCALACAQ&sourceid=chrome&source=chrome.ob&ie=UTF-8#lrd=0x89aab31a8792f40b:0x6e4e46a5a6775bd1,1,,,,",
    label: "Google Reviews — Hidden Acres",
    logo: "/brand/google-reviews.svg",
  },
  bestOfPeeDee: {
    href: "https://scnow.com/contests/",
    label: "Best of the Pee Dee 2025",
    logo: "/brand/best-of-pee-dee-2025-badge.png",
  },
} as const;

/** Venue tour film from hiddenacresweddings.com/venue-video */
export const VENUE_TOUR_VIDEO = {
  youtubeId: "-Ti2LT0XOeE",
  embedUrl: "https://www.youtube.com/embed/-Ti2LT0XOeE",
  watchUrl: "https://www.youtube.com/watch?v=-Ti2LT0XOeE",
  title: "Hidden Acres venue tour",
  credit:
    "Joyful Entertainment and the Adventure Film Company give you a look at Hidden Acres in Marion, SC.",
};

export const SERVICE_AREAS = [
  "Marion",
  "Florence",
  "Myrtle Beach",
  "Mullins",
  "Dillon",
  "Conway",
  "Darlington",
] as const;

/** Work / proof path */
export const PORTFOLIO_PATH = "/portfolio";
export const VENUE_PATH = "/venue";
export const WEDDING_PATH = "/wedding";
export const ABOUT_PATH = "/about";
export const CONTACT_PATH = "/contact";

/** Main offering that drives location hubs */
export const MAIN_OFFERING_PATH = VENUE_PATH;

export const MARION_HUB_PATH = "/marion-sc-wedding-venue";
export const MARION_HUB_TITLE = "Marion, SC Wedding Venue | Hidden Acres";
export const MARION_HUB_TITLE_SHORT = "Marion Wedding Venue";

export const DEFAULT_OG_IMAGE = {
  url: "/og-default.jpg",
  alt: "Hidden Acres wedding venue in Marion, South Carolina — pastoral grounds at dusk",
};

export function getSiteUrl(): string {
  if (process.env.NEXT_PUBLIC_SITE_URL) {
    return process.env.NEXT_PUBLIC_SITE_URL.replace(/\/$/, "");
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return CANONICAL_SITE_URL;
}

export const HOME_TITLE =
  "Wedding Venue in Marion, SC — Weekend Packages on 37 Acres | Hidden Acres";

export const HOME_DESCRIPTION =
  "Hidden Acres is a secluded 37-acre wedding venue in Marion, South Carolina — chapel, ballroom, pond, silo, and on-site stays. Thursday–Sunday packages. Now booking 2027.";
