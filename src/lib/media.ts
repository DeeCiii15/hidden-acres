/** Real photography from hiddenacresweddings.com (Squarespace CDN). */

const SQ = "https://images.squarespace-cdn.com/content/v1/55e50cb1e4b0a22db861bfd6";

function sq(idPath: string, width = 2000): string {
  return `${SQ}/${idPath}?format=${width}w`;
}

export const media = {
  hero: "/images/hero-couple-bridge.jpg",
  heroAlt:
    "Bride and groom laughing on the wooden bridge at Hidden Acres in Marion, SC",

  welcome: "/images/welcome-couple.jpg",
  welcomeAlt:
    "Bride and groom kissing under a brick arch overlooking the pond at Hidden Acres",

  grounds: sq(
    "1441135615881-O9ER12PNAL5U1AR9CJDH/Hidden+Acres+General+Store+1+-+no+sig.jpg",
  ),
  groundsAlt: "Hidden Acres grounds in Marion, South Carolina",

  chapel: {
    primary: sq(
      "1441250689866-VV72MY42U7OQWEZ8SELO/Hidden+Acres+Chapel+1+-+no+sig.jpg",
    ),
    secondary: sq("1441250575111-5VFYL3FP3CJ4UBMTGX3V/2218.jpg"),
    alt: "The Chapel at Hidden Acres",
  },

  pond: {
    primary: "/images/venue/ceremony-pond.jpg",
    secondary: sq(
      "1441255173259-C7D0ADAGCUFVYNVDHWQX/891892_10202009779079509_1882032221_o.jpg",
      2500,
    ),
    alt: "The Ceremony Pond at Hidden Acres",
  },

  ballroom: {
    primary: sq("1441159821306-QOWDBX44G3UD8SWOMQ0P/IMG_9352.jpg"),
    secondary: sq("1441159984026-85WT7MZU9VX8WRV0ABU5/IMG_9356.jpg"),
    alt: "The Ballroom at Hidden Acres",
  },

  courtyard: {
    primary: sq("1536090052645-PHHJCXIXJAU7YSZKSGBG/image_6483441-6.JPG"),
    secondary: sq("1536090072462-X8EBBSMV7OMIFMIJL8M1/image_6483441-11.JPG"),
    alt: "The Courtyard and Pavilion at Hidden Acres",
  },

  silo: {
    primary: "/images/venue/rusted-silo.jpg",
    secondary: sq("1572398912090-N45UPHW1U3X0352B2A4T/IMG_1330.jpeg", 2500),
    alt: "The Rusted Silo at Hidden Acres",
  },

  inn: {
    primary: "/images/venue/the-inn.jpg",
    secondary: sq(
      "1711719781803-9PCFW77IO39G4NZHTO72/IMG_0856.jpg",
      2500,
    ),
    alt: "The Inn cottages at Hidden Acres",
  },

  bridal: {
    primary: sq("1760461192255-P18EOJ09RS7BMK5EG90X/285A7099.jpg"),
    secondary: sq("1760461208772-MLSOFV9J1EC0B5ICR9HJ/285A7120.jpg"),
    alt: "The Bridal Suite and Salon at Hidden Acres",
  },

  grooms: {
    primary: "/images/venue/grooms-quarters.jpg",
    secondary: sq("1712256615607-AN3S36PXZNV5M4H0646R/IMG_0781.jpg", 2500),
    alt: "Groom’s Quarters at Hidden Acres",
  },

  kitchen: {
    primary: sq("1760461254939-JXSTZ83LGOMEA8UYF6DE/285A7146.jpg"),
    alt: "Full kitchen available for catering setup at Hidden Acres",
  },

  wedding: {
    hero: sq(
      "1441150592640-AV5IJHKEASBFKVBXBZ5Y/2J8A5516.jpg",
      2500,
    ),
    heroAlt:
      "Bride and groom sharing a kiss on the grounds at Hidden Acres in Marion, SC",
    kristaColton: sq(
      "1721908576493-3TRUW09PW6EF1A9DIHWR/Krista%26ColtonWedding-611.jpg",
    ),
    ak320: sq("1721907849385-XTYL9LTIK8OHKVZ9Q79C/AKWedding-320.jpg"),
    ak69: sq("1721907857292-OUGAKP8VNW9J5BEF9DFJ/AKWedding-69.jpg"),
    night1: sq(
      "1721907431646-B2E6WN7E46VY0MBHY8YM/440450336_860926579397034_3950913877281499024_n.jpg",
    ),
    night2: sq(
      "1710850918574-ZQU2S7KNPQUDLVREUTB2/433652794_831755788980780_1749074009660082504_n.jpg",
    ),
    night3: sq(
      "1710850918665-2KRSSOCVBPA1L2EO9O3N/433610830_831755762314116_2377613983334964234_n.jpg",
    ),
    lawn1: sq(
      "1721907259228-5AVQ9FQVQ7ILECSQOCWH/451217798_910022921154066_8143981610577953912_n.jpg",
    ),
    lawn2: sq(
      "1721907247035-CD3MENSLTON4OSL09GK4/434385639_839973191492373_8874448182426253895_n.jpg",
    ),
    dance: sq(
      "1721907292508-0UT6J263RLDJFBP17AL1/431484276_825710279585331_3608119509838792786_n.jpg",
    ),
    portrait: sq(
      "1721907312340-9X4ZII7MZZPAEH84C9BK/450872325_908166131339745_2979450545657604501_n.jpg",
    ),
    detail: sq(
      "1721907328029-RXRX1PXR2T2DAMVZD7SR/447015747_883628090460216_5615647865426680469_n.jpg",
    ),
    couple: sq(
      "1721907336431-JAXFDN0KI3OW163OGSX8/442438562_875938407895851_8207393608338933834_n.jpg",
    ),
    classic1: sq(
      "1441135710587-VQ9RIN3IE3G58KEFJTPP/11061169_10207629586046972_5023333829032298243_n.jpg",
    ),
    classic2: sq(
      "1441135713125-BIUM75L9YUIDDRE4P2ZZ/10010214_651417611614291_7270522721847898991_o.jpg",
    ),
    img9556: sq("1706192229927-FB96VII8Z8K4W2XSVSF4/IMG_9556.jpg"),
    img9531: sq("1706192230963-TO5BR3IJ1RE9E14GMOCB/IMG_9531.jpg"),
    img9188: sq("1700618962840-3OBBVVF8U6ERZP097FQA/IMG_9188.jpg"),
    img9211: sq("1700619083118-T32R48UZ6FEM5AE3CWFW/IMG_9211.jpg"),
  },
} as const;
