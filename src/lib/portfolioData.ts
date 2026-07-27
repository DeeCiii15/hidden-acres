import { PORTFOLIO_PATH } from "./siteConfig";

const SQ = "https://images.squarespace-cdn.com/content/v1/55e50cb1e4b0a22db861bfd6";

function photo(idPath: string, width = 1600): string {
  return `${SQ}/${idPath}?format=${width}w`;
}

export type PortfolioPhoto = {
  src: string;
  alt: string;
};

export type PortfolioWedding = {
  slug: string;
  couple: string;
  title: string;
  dateLabel: string;
  season: string;
  cityId: string;
  summary: string;
  story: string;
  coverImage: string;
  coverAlt: string;
  spacesUsed: string[];
  photos: PortfolioPhoto[];
};

/** Real Weddings copy + galleries from hiddenacresweddings.com/real-weddings */
export const portfolioWeddings: PortfolioWedding[] = [
  {
    slug: "brittany-nicholas",
    couple: "Brittany & Nicholas",
    title: "Brooch bouquet & cowgirl boots",
    dateLabel: "Real wedding",
    season: "Spring",
    cityId: "marion",
    summary:
      "Snazzy hats for the groomsmen, cowgirl boots for the ladies, and a stunning brooch bouquet.",
    story:
      "We could go on forever about all the things we love about this wedding but we'll just stop at those snazzy hats Nicholas' groomsmen are wearing and the fun cowgirl boots Brittany's ladies are sporting. Be sure to check out that stunning brooch bouquet! Photography by Caitlin Moore Photography.",
    coverImage: photo(
      "1473613662102-ACZSBRPDESTJ2SJVWYHZ/Brittany+Petty+Nicholas+Brown+4+23+16+Wedding-Brittany+Petty+Nicholas+-0043.jpg",
      2000,
    ),
    coverAlt: "Brittany and Nicholas wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "the-ballroom", "courtyard-pavilion"],
    photos: [
      {
        src: photo(
          "1473613662102-ACZSBRPDESTJ2SJVWYHZ/Brittany+Petty+Nicholas+Brown+4+23+16+Wedding-Brittany+Petty+Nicholas+-0043.jpg",
        ),
        alt: "Brittany and Nicholas at Hidden Acres",
      },
      {
        src: photo(
          "1473613625543-ACZFRETHG701CUSU6JBZ/Brittany+Petty+Nicholas+Brown+4+23+16+Wedding-Brittany+Petty+Nicholas+-0002.jpg",
        ),
        alt: "Brittany and Nicholas wedding portrait",
      },
      {
        src: photo(
          "1473613642367-8FMSDQY1HGTGQSVHK25S/Brittany+Petty+Nicholas+Brown+4+23+16+Wedding-Brittany+Petty+Nicholas+-0039.jpg",
        ),
        alt: "Wedding party at Hidden Acres",
      },
      {
        src: photo(
          "1473613663203-1L6E3K3EKUJYFXU56FBT/Brittany+Petty+Nicholas+Brown+4+23+16+Wedding-Brittany+Petty+Nicholas+-0041.jpg",
        ),
        alt: "Celebration details from Brittany and Nicholas",
      },
      {
        src: photo(
          "1473613676306-V7ET7BLTT7ZB5C3S94S9/Brittany+Petty+Nicholas+Brown+4+23+16+Wedding-Brittany+Petty+Nicholas+-0062.jpg",
        ),
        alt: "Reception moment at Hidden Acres",
      },
      {
        src: photo(
          "1473613679894-E39NZ4CFFAIVTICBGB6E/Brittany+Petty+Nicholas+Brown+4+23+16+Wedding-Brittany+Petty+Nicholas+-0063.jpg",
        ),
        alt: "Brittany and Nicholas wedding day",
      },
    ],
  },
  {
    slug: "carolina-david",
    couple: "Carolina & David",
    title: "Christmas wedding",
    dateLabel: "Real wedding",
    season: "Winter",
    cityId: "marion",
    summary:
      "A stunning Christmas wedding full of vintage details and a one-of-a-kind groom's cake.",
    story:
      "We are IN. LOVE. with Carolina & David's stunning Christmas wedding! Their mix of vintage details and their quirky sense of humor made for a celebration that was uniquely them — check out the great groom's cake! Photography by Caitlin Moore Photography.",
    coverImage: photo(
      "1473612667592-R8S7K8AVCKGQ6HC6NH9O/Carolina+Smith.+David+Doughty+12.19.15+Wedding-0003.jpg",
      2000,
    ),
    coverAlt: "Carolina and David Christmas wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "the-ballroom", "the-inn"],
    photos: [
      {
        src: photo(
          "1473612667592-R8S7K8AVCKGQ6HC6NH9O/Carolina+Smith.+David+Doughty+12.19.15+Wedding-0003.jpg",
        ),
        alt: "Carolina and David at Hidden Acres",
      },
      {
        src: photo(
          "1473612676413-FDZW96ARSNU2BBB1EIHJ/Carolina+Smith.+David+Doughty+12.19.15+Wedding-0002.jpg",
        ),
        alt: "Christmas wedding portrait",
      },
      {
        src: photo(
          "1473612686900-ZNZSEM4VGJDLB7L3QHBQ/Carolina+Smith.+David+Doughty+12.19.15+Wedding-0004.jpg",
        ),
        alt: "Vintage details from Carolina and David's wedding",
      },
      {
        src: photo(
          "1473612711160-S2OWH1SW9U5K77FN569U/Carolina+Smith.+David+Doughty+12.19.15+Wedding-0008.jpg",
        ),
        alt: "Celebration at Hidden Acres",
      },
      {
        src: photo(
          "1473612933944-M18PVCRT2NF05NGI361X/Carolina+Smith.+David+Doughty+12.19.15+Wedding-0074.jpg",
        ),
        alt: "Reception moment for Carolina and David",
      },
      {
        src: photo(
          "1473612968703-WP1IVQUQCD4SZW730RH7/Carolina+Smith.+David+Doughty+12.19.15+Wedding-0099.jpg",
        ),
        alt: "Christmas wedding details",
      },
    ],
  },
  {
    slug: "bryan-rachel",
    couple: "Bryan & Rachel",
    title: "Lilacs, pinks & a winning cake",
    dateLabel: "Real wedding",
    season: "Summer",
    cityId: "marion",
    summary:
      "A gorgeous August day with a soft palette of lilacs and pinks — and a groom's cake worth celebrating.",
    story:
      "Bryan and Rachel got married on a gorgeous summer day in August. We love their soft palette of lilacs and pinks — and check out that groom's cake, it's a real winner! Photography from Photographs by Andrea.",
    coverImage: photo(
      "1473536019635-QQZWB66WVRPDY8HBPAZ1/Stewart+Wedding-1.jpg",
      2000,
    ),
    coverAlt: "Bryan and Rachel wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "ceremony-pond", "the-ballroom"],
    photos: [
      {
        src: photo(
          "1473536019635-QQZWB66WVRPDY8HBPAZ1/Stewart+Wedding-1.jpg",
        ),
        alt: "Bryan and Rachel at Hidden Acres",
      },
      {
        src: photo(
          "1473535961798-M4USLBFO5KLY80P2ZGOM/Stewart+Wedding-7.jpg",
        ),
        alt: "Wedding portrait for Bryan and Rachel",
      },
      {
        src: photo(
          "1473536181420-YM7OHMVU310NFKC379B0/Stewart+Wedding-9.jpg",
        ),
        alt: "Ceremony moment at Hidden Acres",
      },
      {
        src: photo(
          "1473536345266-VAE6SQXU2IXUG1A9O8T2/Stewart+Wedding-42.jpg",
        ),
        alt: "Wedding party details",
      },
      {
        src: photo(
          "1473536921088-0KQ5572DJWEDQT89ESI2/Stewart+Wedding-311.jpg",
        ),
        alt: "Reception celebration",
      },
      {
        src: photo(
          "1473538218117-8MWXLVOO1URO2PYZ2SUN/Stewart+Wedding-794.jpg",
        ),
        alt: "Evening moments from Bryan and Rachel's wedding",
      },
    ],
  },
  {
    slug: "nicole-johnathan",
    couple: "Nicole & Johnathan",
    title: "Rustic country chic",
    dateLabel: "Real wedding",
    season: "Fall",
    cityId: "marion",
    summary:
      "A rustic, country chic November wedding — don't miss the antler details.",
    story:
      "Nicole & Johnathan had a rustic, country chic wedding on a lovely fall day in November. Check out the antler details! Photography by Ricki Ford.",
    coverImage: photo(
      "1454975080053-FSZGGPRL59PU3B97UBVJ/dcd9cc00fdd7ccc82685aea461b7bef2.jpg",
      2000,
    ),
    coverAlt: "Nicole and Johnathan wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "courtyard-pavilion", "rusted-silo"],
    photos: [
      {
        src: photo(
          "1454975080053-FSZGGPRL59PU3B97UBVJ/dcd9cc00fdd7ccc82685aea461b7bef2.jpg",
        ),
        alt: "Nicole and Johnathan at Hidden Acres",
      },
      {
        src: photo(
          "1454975062877-D4EMQZRLHVF6HA63XC7Q/2901d491b769579e4071c9da1da97ff6.jpg",
        ),
        alt: "Country chic wedding details",
      },
      {
        src: photo(
          "1454975058768-2RZ7PYURL1Q7KJAGTIY2/3f4577e4e765b046aabaf1af892cabfe.jpg",
        ),
        alt: "Fall wedding at Hidden Acres",
      },
      {
        src: photo(
          "1454975076473-JU4AH62Y5XK5F85YQJIY/cdc56afa767d179eb43cf809a3dcca70.jpg",
        ),
        alt: "Antler and rustic décor details",
      },
      {
        src: photo(
          "1454975081892-H5RZF405TO079TCU07PH/ebb2a5e85cd43f74b6b144f99b2ef743.jpg",
        ),
        alt: "Reception at Hidden Acres",
      },
      {
        src: photo(
          "1454975085740-MPVOGFANYCYN8HEB909B/f375fd839c54b817a79ccc9191d92519.jpg",
        ),
        alt: "Nicole and Johnathan celebration",
      },
    ],
  },
  {
    slug: "hannah-josh",
    couple: "Hannah & Josh",
    title: "Vintage rustic summer",
    dateLabel: "Real wedding",
    season: "Summer",
    cityId: "marion",
    summary:
      "A vintage, rustic vibe that feels perfectly at home with Hidden Acres décor.",
    story:
      "Hannah & Josh got married on a beautiful summer day in August. Their vintage, rustic vibe is such a perfect match for the decor at Hidden Acres. Photography by White Bridge Photography, florals by Grace Designs, and catering by Hidden Treasures.",
    coverImage: photo(
      "1441840087705-2PEXM2M57BBLWV1ATVF5/11856246_1029010037139576_2053078168493957897_o.jpg",
      2000,
    ),
    coverAlt: "Hannah and Josh wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "the-ballroom", "bridal-suite-salon"],
    photos: [
      {
        src: photo(
          "1441840087705-2PEXM2M57BBLWV1ATVF5/11856246_1029010037139576_2053078168493957897_o.jpg",
        ),
        alt: "Hannah and Josh at Hidden Acres",
      },
      {
        src: photo(
          "1441840134878-408TW62M2XXQ474JEQ9P/11922949_1029011283806118_3336762110342378878_o.jpg",
        ),
        alt: "Summer wedding portrait",
      },
      {
        src: photo(
          "1441840098614-YLQE221DKDMFB93E60HM/11872256_1029010373806209_2671118383710428239_o.jpg",
        ),
        alt: "Vintage rustic wedding details",
      },
      {
        src: photo(
          "1441840078994-FPQ055CB6IIUUITTJKT3/10927828_1029011213806125_1134012168616304574_o.jpg",
        ),
        alt: "Ceremony at Hidden Acres",
      },
      {
        src: photo(
          "1441840120739-57IRVMX823FCMNRYOJGX/11892321_1029010367139543_4856321893111244616_o.jpg",
        ),
        alt: "Wedding party on the grounds",
      },
      {
        src: photo(
          "1441840121676-A86YUMY2IDUNEMTZBYFV/11893958_1029010180472895_1670070042103912282_o.jpg",
        ),
        alt: "Reception celebration for Hannah and Josh",
      },
    ],
  },
  {
    slug: "lauren-bryce",
    couple: "Lauren & Bryce",
    title: "Old-Hollywood summer",
    dateLabel: "Real wedding",
    season: "Summer",
    cityId: "marion",
    summary:
      "Lauren's Old-Hollywood vibe and floral crown — the stuff of legend.",
    story:
      "Lauren & Bryce got married on a beautiful summer day in June. Lauren's Old-Hollywood vibe and floral crown are the stuff of legend, and we are in LOVE! Photography by Gillian Claire.",
    coverImage: photo(
      "1441151834744-OJMIFZ0ARI4JAXL5Z7A2/IMG_9433.jpg",
      2000,
    ),
    coverAlt: "Lauren and Bryce wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "ceremony-pond", "courtyard-pavilion"],
    photos: [
      {
        src: photo(
          "1441151834744-OJMIFZ0ARI4JAXL5Z7A2/IMG_9433.jpg",
        ),
        alt: "Lauren and Bryce at Hidden Acres",
      },
      {
        src: photo(
          "1441150592640-AV5IJHKEASBFKVBXBZ5Y/2J8A5516.jpg",
        ),
        alt: "Old-Hollywood wedding portrait",
      },
      {
        src: photo(
          "1441150582098-IGZLZP1YSY0SQTP76NYX/2J8A5492.jpg",
        ),
        alt: "Floral crown and summer details",
      },
      {
        src: photo(
          "1441150749084-088P2MSBLKBL06CT0UVY/IMG_3690.jpg",
        ),
        alt: "Ceremony moment for Lauren and Bryce",
      },
      {
        src: photo(
          "1441151828517-FKORUZG0Y6LBG2251BSL/IMG_9605.jpg",
        ),
        alt: "Reception at Hidden Acres",
      },
      {
        src: photo(
          "1441140274847-T6F9TM0O7XG2AJ5ASDEC/2184.jpg",
        ),
        alt: "Wedding day details",
      },
    ],
  },
  {
    slug: "meredith-jason",
    couple: "Meredith & Jason",
    title: "Early spring in the Carolinas",
    dateLabel: "Real wedding",
    season: "Spring",
    cityId: "marion",
    summary:
      "Friends and family from all around the Carolinas — and yes, the Toms shoes.",
    story:
      "Meredith & Jason had a beautiful early spring wedding surrounded by their friends & family from all around the Carolinas. And how fun are the Toms shoes everyone is wearing? Photography by Taken By Sarah.",
    coverImage: photo(
      "1441334501264-LKSTX8CJBGS3ZBAG8ZMB/001.jpg",
      2000,
    ),
    coverAlt: "Meredith and Jason wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "the-ballroom", "the-inn"],
    photos: [
      {
        src: photo("1441334501264-LKSTX8CJBGS3ZBAG8ZMB/001.jpg"),
        alt: "Meredith and Jason at Hidden Acres",
      },
      {
        src: photo("1441334450574-881O6FXDPDPMQWSTJXVQ/002.jpg"),
        alt: "Early spring wedding portrait",
      },
      {
        src: photo("1441334548190-3MVGY1JIW6VHGL3QG2S5/004.jpg"),
        alt: "Wedding party gathering",
      },
      {
        src: photo("1441336071566-1LLE0O6T2RXTABE48OFI/066.jpg"),
        alt: "Celebration details",
      },
      {
        src: photo("1441153099982-LLDM1C9TU0MIXMSAVWFV/102.jpg"),
        alt: "Reception at Hidden Acres",
      },
      {
        src: photo("1441153040711-4VQY6PESIGEV4D33I21U/010.jpg"),
        alt: "Meredith and Jason wedding day",
      },
    ],
  },
  {
    slug: "kristin-tyler",
    couple: "Kristin & Tyler",
    title: "Spring day in May",
    dateLabel: "Real wedding",
    season: "Spring",
    cityId: "marion",
    summary:
      "Closest friends and family, plus a ribbon backdrop behind the cake we still love.",
    story:
      "Kristin and Tyler got married on a lovely spring day in May surrounded by their closest friends and family. We are loving the ribbon backdrop behind the cake! Photography by Fred Salley Photography.",
    coverImage: photo(
      "1441306118459-LDTOIKHJMXXHLHI5RQVO/0030a.jpg",
      2000,
    ),
    coverAlt: "Kristin and Tyler wedding at Hidden Acres",
    spacesUsed: ["the-chapel", "the-ballroom", "courtyard-pavilion"],
    photos: [
      {
        src: photo("1441306118459-LDTOIKHJMXXHLHI5RQVO/0030a.jpg"),
        alt: "Kristin and Tyler at Hidden Acres",
      },
      {
        src: photo("1441303946058-92Q66593T1L3Y6V8KRTB/0002.jpg"),
        alt: "Spring wedding portrait",
      },
      {
        src: photo("1441303975614-M4LLW11IT3QDIXAAWC1B/0003.jpg"),
        alt: "Ceremony details",
      },
      {
        src: photo("1441304012315-IHV9Y3L1XUAI4M6AN42K/0005.jpg"),
        alt: "Wedding party at Hidden Acres",
      },
      {
        src: photo("1441304060879-VB4BKRDKZKM086316MU7/0007.jpg"),
        alt: "Reception celebration",
      },
      {
        src: photo("1441304107000-CPIZPF7FH3G83XWH4B63/0010.jpg"),
        alt: "Cake and ribbon backdrop details",
      },
    ],
  },
];

export function getWedding(slug: string): PortfolioWedding | undefined {
  return portfolioWeddings.find((w) => w.slug === slug);
}

export function getAllWeddingSlugs(): string[] {
  return portfolioWeddings.map((w) => w.slug);
}

export function getFeaturedWeddings(limit = 4): PortfolioWedding[] {
  return portfolioWeddings.slice(0, limit);
}

export function getWeddingsUsingSpace(spaceSlug: string): PortfolioWedding[] {
  return portfolioWeddings.filter((w) => w.spacesUsed.includes(spaceSlug));
}

export function portfolioPath(slug?: string): string {
  return slug ? `${PORTFOLIO_PATH}/${slug}` : PORTFOLIO_PATH;
}
