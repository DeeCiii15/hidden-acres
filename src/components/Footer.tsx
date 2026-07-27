import Link from "next/link";
import { SiteLogo } from "@/components/SiteLogo";
import {
  ABOUT_PATH,
  ADDRESS,
  CONTACT_PATH,
  PORTFOLIO_PATH,
  SITE_NAME,
  SOCIAL,
  VENUE_PATH,
  WEDDING_PATH,
} from "@/lib/siteConfig";
import { venueSpaces } from "@/lib/venueData";

const groundsLinks = venueSpaces.map((space) => ({
  href: `${VENUE_PATH}#${space.slug}`,
  label: space.navLabel,
}));

const exploreLinks = [
  { href: WEDDING_PATH, label: "Your wedding" },
  { href: PORTFOLIO_PATH, label: "Portfolio" },
  { href: `${ABOUT_PATH}#vendors`, label: "Preferred vendors" },
  { href: `${ABOUT_PATH}#faq`, label: "FAQs" },
  { href: `${ABOUT_PATH}#directions`, label: "Directions" },
  { href: CONTACT_PATH, label: "Contact" },
];

const socialLinks = [
  { href: SOCIAL.instagram, label: "Instagram", Icon: InstagramIcon },
  { href: SOCIAL.facebook, label: "Facebook", Icon: FacebookIcon },
  { href: SOCIAL.pinterest, label: "Pinterest", Icon: PinterestIcon },
] as const;

function FacebookIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden
    >
      <path d="M22 12.07C22 6.48 17.52 2 11.93 2S1.86 6.48 1.86 12.07c0 5.02 3.66 9.18 8.44 9.93v-7.03H7.9v-2.9h2.4V9.86c0-2.37 1.4-3.68 3.56-3.68 1.03 0 2.12.18 2.12.18v2.34h-1.2c-1.18 0-1.55.74-1.55 1.5v1.8h2.64l-.42 2.9h-2.22V22c4.78-.75 8.44-4.91 8.44-9.93z" />
    </svg>
  );
}

function InstagramIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden
    >
      <path d="M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2m-.2 2A3.6 3.6 0 0 0 4 7.6v8.8C4 18.39 5.61 20 7.6 20h8.8a3.6 3.6 0 0 0 3.6-3.6V7.6C20 5.61 18.39 4 16.4 4H7.6m9.65 1.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5M12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10m0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6z" />
    </svg>
  );
}

function PinterestIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden
    >
      <path d="M12 2C6.48 2 2 6.48 2 12c0 4.19 2.58 7.78 6.23 9.27-.09-.79-.16-2 .04-2.86.18-.78 1.17-4.97 1.17-4.97s-.3-.6-.3-1.48c0-1.39.81-2.43 1.81-2.43.85 0 1.27.64 1.27 1.41 0 .86-.55 2.14-.83 3.33-.24.99.5 1.8 1.48 1.8 1.77 0 3.13-1.87 3.13-4.56 0-2.38-1.71-4.05-4.16-4.05-2.83 0-4.5 2.12-4.5 4.32 0 .86.33 1.78.74 2.28a.3.3 0 0 1 .07.29c-.08.32-.25 1-.28 1.14-.05.18-.15.22-.35.13-1.3-.61-2.12-2.51-2.12-4.04 0-3.3 2.4-6.32 6.91-6.32 3.63 0 6.45 2.59 6.45 6.04 0 3.61-2.27 6.51-5.43 6.51-1.06 0-2.06-.55-2.4-1.2l-.65 2.49c-.24.91-.88 2.05-1.31 2.75A10 10 0 0 0 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2z" />
    </svg>
  );
}

export function Footer() {
  return (
    <footer className="overflow-hidden border-t border-stroke bg-forest-deep text-cream pb-16 md:pb-[4.25rem]">
      <div className="mx-auto grid max-w-5xl items-start gap-10 px-8 pt-4 pb-6 md:grid-cols-3 md:gap-12 md:px-10 md:pb-7">
        <div className="mt-3 text-left leading-none md:mt-4">
          <p className="font-ui text-[10px] uppercase leading-none tracking-[0.2em] text-champagne-soft">
            On the grounds
          </p>
          <ul className="mt-3 space-y-2.5">
            {groundsLinks.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="text-sm leading-snug text-cream/75 transition hover:text-cream"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex flex-col items-center gap-0 text-center leading-none">
          <Link
            href="/"
            aria-label={SITE_NAME}
            className="block leading-none"
          >
            {/* Crop ~28.9% transparent PNG padding so the mark shares a top edge with nav headings */}
            <span className="relative mx-auto block h-[4.225rem] w-[12.5rem] overflow-hidden leading-none md:h-[5.514rem] md:w-[16.3125rem]">
              <SiteLogo
                tone="light"
                className="absolute left-1/2 top-0 h-40 w-auto max-w-none -translate-x-1/2 -translate-y-[28.9%] contrast-150 drop-shadow-md md:h-[13.05rem]"
              />
            </span>
          </Link>
          <p className="mt-3 text-sm leading-snug text-cream/65">
            {ADDRESS.full}
          </p>
          <div className="mt-2 flex items-center justify-center gap-1">
            {socialLinks.map(({ href, label, Icon }) => (
              <a
                key={label}
                href={href}
                target="_blank"
                rel="noreferrer"
                aria-label={label}
                className="inline-flex h-8 w-8 items-center justify-center rounded-full text-cream/70 transition hover:bg-cream/10 hover:text-cream"
              >
                <Icon className="h-4 w-4" />
              </a>
            ))}
          </div>
          <p className="mt-2.5 text-xs leading-none text-cream/45">
            © {new Date().getFullYear()} {SITE_NAME}. All rights reserved.
          </p>
        </div>

        <div className="mt-3 text-left leading-none md:mt-4 md:text-right">
          <p className="font-ui text-[10px] uppercase leading-none tracking-[0.2em] text-champagne-soft">
            Explore
          </p>
          <ul className="mt-3 space-y-2.5">
            {exploreLinks.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="text-sm leading-snug text-cream/75 transition hover:text-cream"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </footer>
  );
}
