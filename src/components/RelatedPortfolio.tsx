import Image from "next/image";
import Link from "next/link";
import {
  portfolioPath,
  type PortfolioWedding,
} from "@/lib/portfolioData";
import { PORTFOLIO_PATH } from "@/lib/siteConfig";
import { Reveal } from "./Reveal";

/** Gentle scrapbook tilts — alternating left/right */
export const polaroidTilts = [
  "-rotate-[1.6deg]",
  "rotate-[1.8deg]",
  "-rotate-[0.9deg]",
  "rotate-[1.2deg]",
  "-rotate-[1.4deg]",
  "rotate-[0.8deg]",
  "-rotate-[1.1deg]",
  "rotate-[1.5deg]",
] as const;

export function RelatedPortfolio({
  weddings,
  heading = "Weddings at Hidden Acres",
  ctaLabel = "Browse portfolio",
}: {
  weddings: PortfolioWedding[];
  heading?: string;
  ctaLabel?: string;
}) {
  if (!weddings.length) return null;

  const tiles = weddings.slice(0, 6);

  return (
    <section
      id="portfolio"
      className="polaroid-scrapbook border-y border-stroke/60 py-14 md:py-20"
    >
      <div className="mx-auto max-w-6xl px-5 md:px-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="eyebrow text-champagne">Portfolio</p>
            <h2 className="mt-2 font-script text-3xl text-forest md:text-4xl lg:text-5xl">
              {heading}
            </h2>
          </div>
          <Link
            href={PORTFOLIO_PATH}
            className="font-ui text-sm uppercase tracking-[0.16em] text-champagne transition hover:text-forest"
          >
            {ctaLabel} →
          </Link>
        </div>

        <ul className="mt-12 grid grid-cols-1 items-start gap-16 sm:grid-cols-2 sm:gap-x-14 sm:gap-y-[4.5rem] lg:grid-cols-3 lg:gap-x-16 lg:gap-y-24">
          {tiles.map((wedding, i) => (
            <Reveal
              as="li"
              key={wedding.slug}
              className="flex justify-center px-5 py-6 sm:px-6 sm:py-7"
            >
              <PolaroidTile
                wedding={wedding}
                tilt={polaroidTilts[i % polaroidTilts.length]}
                showSeal
              />
            </Reveal>
          ))}
        </ul>
      </div>
    </section>
  );
}

export function PolaroidTile({
  wedding,
  tilt,
  showSeal = true,
  headingLevel = "h3",
}: {
  wedding: PortfolioWedding;
  tilt: string;
  showSeal?: boolean;
  headingLevel?: "h2" | "h3";
}) {
  const CaptionTag = headingLevel;

  return (
    <Link
      href={portfolioPath(wedding.slug)}
      className={`polaroid-card group relative block w-full max-w-[17.5rem] md:max-w-[18.5rem] ${tilt} hover:-translate-y-2`}
    >
      <figure className="polaroid-stack relative">
        {/* White fibrous torn core peeks past cream cardstock */}
        <span
          aria-hidden
          className="polaroid-fiber polaroid-deckle-fiber absolute -inset-[3.4%]"
        />
        <div className="polaroid-frame polaroid-deckle relative">
          {/*
            Inspiration proportions (measured from polaroid-style-ref.png):
            ~7% side / ~5% top cream margins; ~19% bottom chin for names.
          */}
          <div className="polaroid-mat relative">
            <div className="polaroid-photo relative aspect-[4/5] overflow-hidden">
              <Image
                src={wedding.coverImage}
                alt={wedding.coverAlt}
                fill
                sizes="(max-width: 640px) 90vw, (max-width: 1024px) 42vw, 28vw"
                className="object-cover transition duration-700 group-hover:scale-[1.035]"
              />
            </div>
            <figcaption className="polaroid-caption-slot pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-center">
              <CaptionTag className="polaroid-caption font-script leading-none">
                {wedding.couple}
              </CaptionTag>
            </figcaption>
          </div>
        </div>

        {/* Outside the deckle mask so seal/twine can overhang the torn edge */}
        {showSeal ? <SealTwineAccent /> : null}
      </figure>
    </Link>
  );
}

/** Photoreal twine bow under green HA wax seal — top-left, overlapping paper + photo. */
function SealTwineAccent() {
  return (
    <span aria-hidden className="pointer-events-none absolute inset-0 z-30 overflow-visible">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/brand/twine-wrap.png"
        alt=""
        className="polaroid-twine absolute drop-shadow-[0_2px_3px_rgba(42,28,20,0.28)]"
      />
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/brand/wax-seal-ha.png"
        alt=""
        className="polaroid-seal absolute drop-shadow-[0_6px_12px_rgba(26,38,32,0.45)]"
      />
    </span>
  );
}
