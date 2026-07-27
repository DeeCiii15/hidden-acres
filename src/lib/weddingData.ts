import { media } from "./media";
import { VENUE_PATH } from "./siteConfig";

export type WeddingAmenity = {
  title: string;
  detail: string;
  image: string;
  imageAlt: string;
};

export type WeddingSection = {
  title: string;
  body: string[];
  image: string;
  imageAlt: string;
  secondaryImage?: string;
  secondaryImageAlt?: string;
  links?: { label: string; href: string }[];
};

/** Content from Pricing & Amenities + Your Wedding on hiddenacresweddings.com */
export const weddingPage = {
  eyebrow: "Your wedding weekend",
  headline: "Pricing, amenities & how the weekend works",
  intro:
    "Hidden Acres is built for a full celebration weekend — ceremony, reception, getting-ready spaces, and room for the people closest to you. Package pricing is shared when you tour; everything below is included with the venue rental unless noted.",
  pricingNote:
    "Please call us to book a tour and inquire about Wedding Package pricing. We’re happy to walk the property with you and talk through dates.",
  included: [
    {
      title: "Entire 37-acre property",
      detail:
        "Use of the full estate for your celebration weekend — ceremony sites, reception spaces, and outdoor grounds.",
      image: media.wedding.img9556,
      imageAlt: "Overhead view of the Hidden Acres property grounds",
    },
    {
      title: "Weekend rental window",
      detail:
        "Your rental begins Thursday morning at 8:30 AM and ends Sunday whenever you (or your representatives) finish cleaning up.",
      image: media.wedding.lawn2,
      imageAlt: "Hidden Acres grounds during a wedding weekend",
    },
    {
      title: "Chairs",
      detail:
        "Chiavari chairs, brown wood folding chairs, white Lifetime folding chairs, and X-back chairs.",
      image: media.chapel.primary,
      imageAlt: "Seating inside The Chapel at Hidden Acres",
    },
    {
      title: "Tables",
      detail:
        '12 farm tables & 8 cocktail tables in reclaimed wood; 14–60" round tables; 5–36" round cocktail tables; 5–6\' banquet tables.',
      image: media.ballroom.primary,
      imageAlt: "Reception tables in The Ballroom at Hidden Acres",
    },
    {
      title: "Built-in rain plan",
      detail:
        "If weather turns, move indoors — The Chapel, Ballroom, and Pavilion keep the weekend on track.",
      image: media.ballroom.secondary,
      imageAlt: "Indoor reception space ready for a weather plan",
    },
    {
      title: "Vendor freedom",
      detail:
        "Choose your own creative team. Preferred vendors are available if you’d like past-client approved recommendations.",
      image: media.wedding.detail,
      imageAlt: "Wedding day details at Hidden Acres",
    },
  ] satisfies WeddingAmenity[],
  /** Order: accommodations → catering → ceremony → reception */
  sections: [
    {
      title: "Accommodations & getting ready",
      body: [
        "The Inn keeps family and friends close for the weekend. The Cabin includes a full kitchen, 2 bedrooms, and a pull-out queen sofa.",
        "The Salon has salon-quality chairs and mirrors so hair and makeup artists come to you. The Groom’s Cave offers a TV, poker table, seating, outdoor mini golf, a fire pit, and more before the ceremony.",
        "Nightly fees for The Inn are not included in the venue rental.",
      ],
      image: media.bridal.primary,
      imageAlt: media.bridal.alt,
      secondaryImage: media.grooms.primary,
      secondaryImageAlt: media.grooms.alt,
      links: [
        { label: "See The Inn", href: `${VENUE_PATH}#the-inn` },
        {
          label: "Bridal Suite & Salon",
          href: `${VENUE_PATH}#bridal-suite-salon`,
        },
        { label: "Groom’s Quarters", href: `${VENUE_PATH}#grooms-quarters` },
      ],
    },
    {
      title: "Catering setup",
      body: [
        "A full catering kitchen includes 2 fridges, a commercial sink, stainless prep table, 2 stoves, commercial ice machine, microwave, deep freezer, and commercial trash disposal.",
        "The covered grilling area has sink and counter space near The Pavilion and Ballroom, with vendor parking for load-in and load-out.",
      ],
      image: media.kitchen.primary,
      imageAlt: media.kitchen.alt,
      secondaryImage: media.courtyard.secondary,
      secondaryImageAlt: "Outdoor dining and pavilion area at Hidden Acres",
    },
    {
      title: "Ceremony",
      body: [
        "The Chapel features 24 reclaimed wood pews along with 2 Mother pews, rustic chandeliers, and a built-in AV system.",
        "Outdoor ceremonies usually happen at The Ceremony Pond or The Waterfall, where you and your guests are surrounded by nature.",
      ],
      image: media.chapel.primary,
      imageAlt: media.chapel.alt,
      secondaryImage: media.pond.primary,
      secondaryImageAlt: media.pond.alt,
      links: [
        { label: "See The Chapel", href: `${VENUE_PATH}#the-chapel` },
        {
          label: "See The Ceremony Pond",
          href: `${VENUE_PATH}#ceremony-pond`,
        },
      ],
    },
    {
      title: "Reception",
      body: [
        "The Courtyard is perfect for intimate al fresco dining or cocktail hour. The Pavilion offers a DJ area and mobile bar — together they can host about 350 guests.",
        "The Ballroom is the jewel at the heart of Hidden Acres, with over 4,000 square feet of reception space. Depending on seating, up to about 450 guests can fit comfortably.",
      ],
      image: media.courtyard.primary,
      imageAlt: media.courtyard.alt,
      secondaryImage: media.ballroom.primary,
      secondaryImageAlt: media.ballroom.alt,
      links: [
        { label: "See The Ballroom", href: `${VENUE_PATH}#the-ballroom` },
        {
          label: "See Courtyard & Pavilion",
          href: `${VENUE_PATH}#courtyard-pavilion`,
        },
        { label: "See The Rusted Silo", href: `${VENUE_PATH}#rusted-silo` },
      ],
    },
  ] satisfies WeddingSection[],
  goodToKnow: [
    "Complete freedom to choose your own wedding vendors.",
    "Rental starts Thursday at 8:30 AM and ends Sunday after cleanup — no rush.",
    "Tables and chairs included as listed above.",
    "Built-in rain plan for the entire weekend.",
    "All buildings are smoke-free; designated outdoor smoking areas are provided.",
  ],
};
