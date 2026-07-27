export type FaqItem = {
  question: string;
  answer: string;
};

export type Vendor = {
  name: string;
  detail?: string;
  phone?: string;
  url?: string;
  email?: string;
};

export type VendorCategory = {
  slug: string;
  name: string;
  vendors: Vendor[];
};

export type DirectionRoute = {
  from: string;
  steps: string[];
};

export const aboutIntro = {
  eyebrow: "About Hidden Acres",
  headline: "Rustic charm & Southern hospitality",
  body: [
    "Hidden Acres is a secluded 37-acre wedding venue tucked into the Marion, South Carolina countryside — just 10 minutes from historic downtown, about 30 minutes from Florence, and roughly an hour from Myrtle Beach.",
    "Owner Donny Gerald and family are constantly improving the property and love surprising couples with new additions. When you’re here, you’ll experience rustic charm and Southern hospitality at its finest — Thursday through Sunday, with no rush and a built-in rain plan.",
  ],
};

export const faqs: FaqItem[] = [
  {
    question: "What's so special about Hidden Acres?",
    answer:
      "You get flexibility with a long rental window, table and chair rentals, use of the entire 37-acre property, and a built-in rain plan. If weather turns, move indoors. With The Chapel, The Ballroom, The Pavilion, and outdoor options, you can design the weekend your way.",
  },
  {
    question: "Do you require specific vendors?",
    answer:
      "No. You have complete flexibility to choose your own creative team. We maintain relationships with preferred vendors who are past-client approved if you’d like recommendations.",
  },
  {
    question: "How long does the rental period last?",
    answer:
      "Your rental begins Thursday morning at 8:30 AM and concludes Sunday afternoon whenever you (or your representatives) finish cleaning up. Take your time — enjoy the weekend.",
  },
  {
    question: "What wedding packages and pricing are available?",
    answer:
      "Package details and pricing depend on your date and needs. Contact us to schedule a tour — we’d love to walk the property with you and share current options.",
  },
  {
    question: "What are policies for The Inn?",
    answer:
      "The Inn is non-smoking (designated outdoor areas provided). Maximum four people per room. Rentals may not be transferred or sublet. No refunds for early checkout or weather issues. Nightly fees are separate from the venue rental.",
  },
  {
    question: "Is there a rain plan?",
    answer:
      "Yes. The Chapel, Ballroom, and Pavilion keep celebrations on track if the weather doesn’t cooperate — a true built-in rain plan for the whole weekend.",
  },
];

export const vendorCategories: VendorCategory[] = [
  {
    slug: "coordination",
    name: "Wedding Coordination",
    vendors: [
      { name: "Jorgia Events", detail: "Jordan Johnson & Georgiana Wester", phone: "843-269-6798" },
      { name: "3 Generations Events", detail: "Madison Hughes", phone: "843-933-1954" },
      { name: "Tie The Knot with Alli", phone: "843-453-0771", url: "https://www.tietheknotwithalli.com" },
      { name: "Two Become One Wedding Planning", phone: "843-742-8840", url: "https://www.twobecomeoneweddings.com" },
      { name: "Ash Events", detail: "Ashley Newkirk", phone: "843-855-2627" },
      { name: "MEK Events", detail: "Marcie King", phone: "843-430-8780" },
      { name: "Covenant and Lace", detail: "Jenna-Marie Demers", phone: "518-817-2310", url: "https://covenantandlace.com" },
    ],
  },
  {
    slug: "catering",
    name: "Catering",
    vendors: [
      { name: "M.F. Scratch Catering", detail: "Myrtle Beach", phone: "843-798-8028", url: "https://www.mfscratch.com" },
      { name: "Hidden Treasures Catering", detail: "Hartsville, SC", phone: "843-498-6065" },
      { name: "Venus Catering", detail: "Florence, SC", phone: "843-669-9977" },
      { name: "Victor's Bistro Catering", detail: "Florence — ask for Rachel Dill", phone: "843-665-0846" },
      { name: "Shulers BBQ", detail: "Latta, SC", phone: "843-752-4700" },
      { name: "Jimmy B’s", detail: "Marion, SC", phone: "843-245-6587" },
    ],
  },
  {
    slug: "photography",
    name: "Photography & Video",
    vendors: [
      { name: "Joyful Entertainment Videography", phone: "843-910-0142", email: "info@joyfulentertainment.net" },
      { name: "Ashlyn Jordan", email: "hello@ashlynjordan.com" },
      { name: "Hannah Ruth Photography", phone: "843-333-6611", email: "hannah@hannahruthphotography.com" },
      { name: "Middle Child Photography", phone: "843-455-5495", email: "info@middlechildphotography.com" },
      { name: "Amber Rhodes Photography", email: "amber@amberrhodesphotography.com" },
      { name: "Lauren Bri Photography & Film", phone: "843-855-6465", email: "laurenbrithomp@gmail.com" },
    ],
  },
  {
    slug: "floral",
    name: "Floral Design",
    vendors: [
      { name: "A&B Florist", detail: "Florence, SC", phone: "843-669-0750" },
      { name: "Corey Jackson’s Petals & Stems", phone: "843-627-3349" },
      { name: "Nature’s Poetry Floral Design", email: "lexi@naturespoetryfloraldesign.com" },
    ],
  },
  {
    slug: "entertainment",
    name: "Entertainment / DJ",
    vendors: [
      { name: "Carolina Entertainment", phone: "843-602-3455" },
      { name: "Joyful Entertainment", url: "https://www.joyfulentertainment.net", email: "info@joyfulentertainment.net" },
      { name: "Happily Ever After Entertainment", phone: "843-251-6152", url: "https://www.heaedj.com" },
      { name: "Scotty G. Productions", phone: "843-229-5897", email: "scotty@scottygproductions.com" },
    ],
  },
  {
    slug: "bars-cakes",
    name: "Mobile Bars & Cakes",
    vendors: [
      { name: "The Sippin’ Palmetto", phone: "803-664-2503" },
      { name: "Lemon or Lime / We Set The Bar", phone: "843-944-3011", url: "https://www.lemonorlimebar.com" },
      { name: "Classic Cakes by Louise", phone: "910-740-1355" },
      { name: "Sweet A Boutique Bakery", detail: "Florence & Columbia", phone: "843-407-7071" },
      { name: "Fudge Shop of Marion", phone: "843-472-2377" },
    ],
  },
  {
    slug: "lodging",
    name: "Local Lodging",
    vendors: [
      { name: "The Loft at 109", phone: "843-430-0332" },
      { name: "The Asbury House", phone: "843-430-0332" },
      { name: "Holiday Inn Express & Suites", phone: "843-752-5690" },
      { name: "Abingdon Manor", phone: "843-752-5090" },
      { name: "Hideaway Haven", phone: "843-618-8523" },
    ],
  },
];

export const directionRoutes: DirectionRoute[] = [
  {
    from: "From Marion",
    steps: [
      "Turn left on 501 Bypass North towards Dillon (Super Walmart).",
      "Travel 2 miles and take Exit SC-41 ALT towards Marion on the right. At the stop sign turn right onto SC-41 ALT towards Lake View.",
      "Travel 2.5 miles and turn left on Sandhill Road.",
      "Travel 2 miles to the stop sign and turn left on Dew Road.",
      "Travel ½ mile — Hidden Acres Gate will be on your left.",
    ],
  },
  {
    from: "From I-95",
    steps: [
      "Take Exit 181-A (SC-38 East) Marion–Myrtle Beach. Travel SC-38 for 7.1 miles.",
      "SC-38 E becomes US-501 S towards Marion & Myrtle Beach.",
      "Travel US-501 S towards Conway for 6.7 miles to the SC-41 ALT exit.",
      "Take SC-41 ALT on the right; at the stop sign turn right towards Lake View.",
      "Travel 3 miles and turn left on Sandhill Road, then 2 miles to Dew Road — turn left.",
      "Travel ½ mile — Hidden Acres Gate will be on your left.",
    ],
  },
  {
    from: "From Conway",
    steps: [
      "Travel Highway 501 towards Marion.",
      "Take Exit 501 on the right towards Dillon–Bennetsville.",
      "Travel 6 miles and take Exit SC-41 ALT on the right towards Marion.",
      "At the stop sign turn right onto SC-41 ALT towards Lake View.",
      "Travel 2.5 miles and turn left on Sandhill Road.",
      "Travel 2 miles to the stop sign, turn left on Dew Road, then ½ mile to the gate on your left.",
    ],
  },
];

export const mapsQuery = "6701+Ella+Grace+Court,+Marion,+SC+29571";
