import type { Metadata } from "next";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import {
  PolaroidTile,
  polaroidTilts,
} from "@/components/RelatedPortfolio";
import { Reveal } from "@/components/Reveal";
import { portfolioWeddings } from "@/lib/portfolioData";
import {
  CONTACT_PATH,
  PORTFOLIO_PATH,
  VENUE_PATH,
} from "@/lib/siteConfig";

const title = "Wedding Portfolio & Real Galleries | Hidden Acres Marion, SC";
const description =
  "Browse real wedding weekends at Hidden Acres — chapel ceremonies, pondside vows, silo cocktail hours, and ballroom receptions in Marion, SC.";

export const metadata: Metadata = {
  title: { absolute: title },
  description,
  alternates: { canonical: PORTFOLIO_PATH },
  openGraph: {
    title,
    description,
    url: PORTFOLIO_PATH,
  },
};

export default function PortfolioIndexPage() {
  return (
    <>
      <section className="polaroid-scrapbook pb-16 pt-28">
        <div className="mx-auto max-w-6xl px-5 md:px-8">
          <Reveal>
            <p className="eyebrow text-champagne">Portfolio</p>
            <h1 className="mt-4 max-w-3xl font-script text-5xl text-forest md:text-6xl lg:text-7xl">
              Real weekends on the acres
            </h1>
            <p className="mt-5 max-w-2xl text-lg text-muted">
              Galleries from couples who celebrated Thursday through Sunday —
              chapel light, pondside promises, silo cocktails, and ballroom nights.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button href={CONTACT_PATH}>Start your weekend</Button>
              <Button href={VENUE_PATH} variant="secondary">
                Tour the venue
              </Button>
            </div>
          </Reveal>

          <ul className="mt-16 grid grid-cols-1 items-start gap-16 sm:grid-cols-2 sm:gap-x-14 sm:gap-y-[4.5rem] lg:grid-cols-3 lg:gap-x-16 lg:gap-y-24">
            {portfolioWeddings.map((wedding, i) => (
              <Reveal
                as="li"
                key={wedding.slug}
                className="flex justify-center px-5 py-6 sm:px-6 sm:py-7"
              >
                <PolaroidTile
                  wedding={wedding}
                  tilt={polaroidTilts[i % polaroidTilts.length]}
                  headingLevel="h2"
                />
              </Reveal>
            ))}
          </ul>
        </div>
      </section>

      <CtaBand
        headline="Your gallery could be next"
        supporting="Now booking 2027 — tell us your date and we’ll help you picture the weekend."
        buttonLabel="Inquire"
      />
    </>
  );
}
