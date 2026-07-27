import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import { Reveal } from "@/components/Reveal";
import { portfolioPath, portfolioWeddings } from "@/lib/portfolioData";
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
      <section className="mx-auto max-w-7xl px-5 pb-16 pt-28 md:px-8">
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

        <ul className="mt-14 grid gap-10 sm:grid-cols-2">
          {portfolioWeddings.map((wedding) => (
            <Reveal as="li" key={wedding.slug}>
              <Link
                href={portfolioPath(wedding.slug)}
                className="group block"
              >
                <div className="relative aspect-[5/4] overflow-hidden">
                  <Image
                    src={wedding.coverImage}
                    alt={wedding.coverAlt}
                    fill
                    sizes="(max-width: 768px) 100vw, 50vw"
                    className="object-cover transition duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-forest-deep/70 via-transparent to-transparent" />
                  <div className="absolute inset-x-0 bottom-0 p-6">
                    <p className="eyebrow text-champagne-soft">
                      {wedding.dateLabel}
                    </p>
                    <h2 className="mt-2 font-display text-3xl text-cream">
                      {wedding.couple}
                    </h2>
                    <p className="mt-2 text-sm text-cream/75">
                      {wedding.summary}
                    </p>
                  </div>
                </div>
              </Link>
            </Reveal>
          ))}
        </ul>
      </section>

      <CtaBand
        headline="Your gallery could be next"
        supporting="Now booking 2027 — tell us your date and we’ll help you picture the weekend."
        buttonLabel="Inquire"
      />
    </>
  );
}
