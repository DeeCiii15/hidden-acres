import { media } from "./media";

export type VenueSpace = {
  slug: string;
  name: string;
  navLabel: string;
  category: "ceremony" | "reception" | "stay" | "prep" | "amenity";
  eyebrow: string;
  summary: string;
  body: string;
  highlights: string[];
  image: string;
  imageAlt: string;
  secondaryImage?: string;
  secondaryImageAlt?: string;
};

export const venueSpaces: VenueSpace[] = [
  {
    slug: "the-chapel",
    name: "The Chapel",
    navLabel: "Chapel",
    category: "ceremony",
    eyebrow: "Ceremony",
    summary:
      "Weathered clapboard, stained glass, and late-afternoon light made for vows.",
    body: "The Chapel at Hidden Acres is clad in weathered clapboard siding from buildings in Mullins, SC, and North Carolina. At 2,300 square feet it features stained glass windows, a tin roof, handmade doors, iron chandeliers, 24 reclaimed-wood pews plus two Mother pews, and tongue-and-groove walls, ceiling, and floors. A built-in audio system and eight chandeliers set the ambiance, and a handicap-accessible ramp welcomes every guest.",
    highlights: [
      "2,300 SF rustic chapel",
      "24 pews + 2 Mother pews",
      "Built-in AV system",
      "Accessible ramp",
    ],
    image: media.chapel.primary,
    imageAlt: media.chapel.alt,
    secondaryImage: media.chapel.secondary,
    secondaryImageAlt: "Inside The Chapel at Hidden Acres",
  },
  {
    slug: "ceremony-pond",
    name: "The Ceremony Pond",
    navLabel: "Pond",
    category: "ceremony",
    eyebrow: "Outdoor ceremony",
    summary:
      "An outdoor aisle beside the Chapel — simple, graceful, and beautiful at dusk.",
    body: "The Ceremony Pond is perfect for couples who want vows wrapped in nature. Nestled next to The Chapel, it wows guests with simplicity and grace. After dark, stroll the island in the middle of the pond when the trees are lit. Nearby, The Waterfall (by The Courtyard) offers another outdoor option soothed by falling water — and a floating dock makes a lovely private dining spot for two.",
    highlights: [
      "Outdoor ceremony beside The Chapel",
      "Lit island for evening walks",
      "Waterfall ceremony option nearby",
      "Private floating dock",
    ],
    image: media.pond.primary,
    imageAlt: media.pond.alt,
    secondaryImage: media.pond.secondary,
    secondaryImageAlt: "Ceremony Pond grounds at Hidden Acres",
  },
  {
    slug: "the-ballroom",
    name: "The Ballroom",
    navLabel: "Ballroom",
    category: "reception",
    eyebrow: "Reception",
    summary:
      "4,000 square feet of whitewashed pine, cathedral ceiling, and chandelier glow.",
    body: "The Ballroom is the gem of Hidden Acres — whitewashed pine walls, a stained cathedral ceiling, and stained concrete floors that blend with every décor palette. At 74' × 52' (about 4,000 SF) it holds up to ~450 guests depending on seating, lit by eight iron chandeliers plus color-wash wall lighting. Combined with The Pavilion you get over 6,000 SF of climate-controlled celebration space, backed by a 15-ton HVAC system. A 1,000 SF covered courtyard addition is perfect for cocktail hour or overflow dancing — so vendors rarely need to flip a room on Saturday.",
    highlights: [
      "Up to ~450 guests",
      "8 iron chandeliers + color washes",
      "1,000 SF covered courtyard addition",
      "Farm tables, Chiavari & more included",
    ],
    image: media.ballroom.primary,
    imageAlt: media.ballroom.alt,
    secondaryImage: media.ballroom.secondary,
    secondaryImageAlt: "Ballroom details at Hidden Acres",
  },
  {
    slug: "courtyard-pavilion",
    name: "The Courtyard & Pavilion",
    navLabel: "Courtyard",
    category: "reception",
    eyebrow: "Cocktail hour & dancing",
    summary:
      "Fountain courtyard under bistro lights, plus an enclosed Pavilion ready to dance.",
    body: "The Courtyard is an open-air 40' × 60' paved space anchored by a fountain and bistro lighting — tucked between The Cabin and The Groom's Cave. Most couples host cocktail hour here. The Pavilion looks out across the property with a bank of windows, built-in DJ area, mobile bar, and terracotta tile floor. Together they comfortably host around 350 guests.",
    highlights: [
      "40' × 60' fountain courtyard",
      "Enclosed Pavilion with DJ area",
      "~350 guests combined",
      "Ideal cocktail-to-dance flow",
    ],
    image: media.courtyard.primary,
    imageAlt: media.courtyard.alt,
    secondaryImage: media.courtyard.secondary,
    secondaryImageAlt: "Pavilion and courtyard at Hidden Acres",
  },
  {
    slug: "rusted-silo",
    name: "The Rusted Silo",
    navLabel: "Silo",
    category: "reception",
    eyebrow: "Signature space",
    summary:
      "A farm silo reimagined for cocktails, appetizers, and rehearsal dinners.",
    body: "This unique silo served its farm well over the years — and now calls Hidden Acres home. Adjacent to The Courtyard and customized for celebrations, The Rusted Silo is a distinct backdrop for cocktail hour, appetizers, rehearsal dinners, and more. Another way the property makes weekend memories feel one-of-a-kind.",
    highlights: [
      "Adjacent to The Courtyard",
      "Cocktail hour & appetizers",
      "Rehearsal dinner option",
      "Unforgettable photo backdrop",
    ],
    image: media.silo.primary,
    imageAlt: media.silo.alt,
    secondaryImage: media.silo.secondary,
    secondaryImageAlt: "Rusted Silo exterior at Hidden Acres",
  },
  {
    slug: "the-inn",
    name: "The Inn",
    navLabel: "Inn",
    category: "stay",
    eyebrow: "On-site lodging",
    summary:
      "Four private cottages on the quiet north end — stay close all weekend.",
    body: "The Inn’s cozy cottages sit on the north end of the property for privacy away from reception areas. Built with rustic wood and tin roofs, each cottage offers porch rocking chairs, two queen beds, private baths, flat-screen TVs, and AC. Skip hotel shuttles and spend the whole weekend on site — Sunday checkout whenever you’re ready. Nightly fees are not included in the venue rental.",
    highlights: [
      "Four private cottages",
      "2 queen beds per cottage",
      "Porch rocking chairs",
      "Separate from party zones",
    ],
    image: media.inn.primary,
    imageAlt: media.inn.alt,
    secondaryImage: media.inn.secondary,
    secondaryImageAlt: "Inn cottage interior at Hidden Acres",
  },
  {
    slug: "bridal-suite-salon",
    name: "Bridal Suite & Salon",
    navLabel: "Bridal Suite",
    category: "prep",
    eyebrow: "Getting ready",
    summary:
      "Natural light, private retreat, and salon chairs so beauty comes to you.",
    body: "The Bridal Suite and Salon are designed for a stress-free Thursday-through-Sunday. Sip champagne with your favorite people in a suite with private entrance, bedroom, and bath — then let your beauty team work on site in The Salon’s salon-quality chairs and mirrors. Photographer-ready light for getting-ready frames, and a peaceful place for the couple to unwind after the celebration.",
    highlights: [
      "Private suite with bath",
      "On-site salon stations",
      "Photographer-ready light",
      "Weekend-long access",
    ],
    image: media.bridal.primary,
    imageAlt: media.bridal.alt,
    secondaryImage: media.bridal.secondary,
    secondaryImageAlt: "Getting-ready space at Hidden Acres",
  },
  {
    slug: "grooms-quarters",
    name: "Groom’s Quarters",
    navLabel: "Groom’s Quarters",
    category: "prep",
    eyebrow: "Wedding party stay",
    summary:
      "Beds, kitchen, screened porch — hang with the guys, then stay Sunday without rushing.",
    body: "The Groom’s Quarters is where you and your guys prepare for the big day. Three bedrooms with four queen beds, two full baths, a full kitchen, living area with TV, and a screened-in porch. Stay the night before, then use it as a wedding-night suite. Outside, mini golf, a fire pit, and space to unwind keep the energy easy. Leave Sunday when you’re ready.",
    highlights: [
      "4 queen beds, 2 baths",
      "Full kitchen & screened porch",
      "Fire pit & outdoor hangouts",
      "Doubles as wedding suite",
    ],
    image: media.grooms.primary,
    imageAlt: media.grooms.alt,
    secondaryImage: media.grooms.secondary,
    secondaryImageAlt: "Groom’s Quarters at Hidden Acres",
  },
];

export function getSpace(slug: string): VenueSpace | undefined {
  return venueSpaces.find((s) => s.slug === slug);
}

export function venueSpacePath(slug: string): string {
  return `/venue#${slug}`;
}

export function getSpacesByCategory(
  category: VenueSpace["category"],
): VenueSpace[] {
  return venueSpaces.filter((s) => s.category === category);
}
