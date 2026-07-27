import Image from "next/image";
import Link from "next/link";
import {
  portfolioPath,
  type PortfolioWedding,
} from "@/lib/portfolioData";
import { PORTFOLIO_PATH } from "@/lib/siteConfig";
import { Reveal } from "./Reveal";

const layouts = [
  // larger — still scrapbook, a bit taller
  "col-span-2 md:col-span-7 md:-rotate-1",
  // small
  "col-span-1 md:col-span-5 md:translate-y-4 md:rotate-2",
  // medium
  "col-span-1 md:col-span-4 md:-translate-y-1 md:-rotate-[1deg]",
  // small
  "col-span-1 md:col-span-4 md:translate-y-5 md:rotate-[1.5deg]",
  // medium
  "col-span-1 md:col-span-4 md:translate-y-2 md:-rotate-1",
] as const;

const frameHeights = [
  "aspect-[4/5] md:aspect-auto md:h-72 lg:h-80",
  "aspect-[3/4] md:aspect-auto md:h-52 lg:h-56",
  "aspect-[4/5] md:aspect-auto md:h-60 lg:h-64",
  "aspect-[3/4] md:aspect-auto md:h-52 lg:h-56",
  "aspect-[4/5] md:aspect-auto md:h-60 lg:h-64",
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

  const tiles = weddings.slice(0, layouts.length);

  return (
    <section className="mx-auto max-w-5xl px-5 py-12 md:px-8 md:py-16">
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

      <div className="mt-8 grid grid-cols-2 items-start gap-3 md:grid-cols-12 md:gap-4">
        {tiles.map((wedding, i) => (
          <Reveal key={wedding.slug} className={layouts[i]}>
            <WeddingTile
              wedding={wedding}
              imageClass={frameHeights[i]}
              featured={i === 0}
            />
          </Reveal>
        ))}
      </div>
    </section>
  );
}

function WeddingTile({
  wedding,
  imageClass,
  featured,
}: {
  wedding: PortfolioWedding;
  imageClass: string;
  featured?: boolean;
}) {
  return (
    <Link href={portfolioPath(wedding.slug)} className="group block h-full">
      <figure className="relative h-full border border-[#cfc4b0] bg-[#faf6ee] p-2 pb-9 shadow-[0_14px_32px_-18px_rgba(26,38,32,0.55),0_2px_0_rgba(255,255,255,0.65)_inset] transition duration-300 group-hover:-translate-y-1 group-hover:shadow-[0_22px_40px_-18px_rgba(26,38,32,0.5)] md:p-2.5 md:pb-10">
        {/* soft tape accent */}
        <span
          aria-hidden
          className={`pointer-events-none absolute -top-2 left-1/2 z-10 h-4 w-14 -translate-x-1/2 bg-[#d4c4a8]/75 shadow-sm ${
            featured ? "w-16 rotate-[-2deg]" : "rotate-[3deg]"
          }`}
        />
        <div
          className={`relative overflow-hidden border border-[#e4dccb] bg-forest-deep/5 ${imageClass}`}
        >
          <Image
            src={wedding.coverImage}
            alt={wedding.coverAlt}
            fill
            sizes={
              featured
                ? "(max-width: 768px) 100vw, 55vw"
                : "(max-width: 768px) 50vw, 28vw"
            }
            className="object-cover transition duration-700 group-hover:scale-[1.04]"
          />
        </div>
        <figcaption className="absolute inset-x-0 bottom-0 px-2 py-2 text-center md:py-2.5">
          <h3
            className={`font-script leading-none text-forest ${
              featured ? "text-xl md:text-2xl" : "text-lg md:text-xl"
            }`}
          >
            {wedding.couple}
          </h3>
        </figcaption>
      </figure>
    </Link>
  );
}
