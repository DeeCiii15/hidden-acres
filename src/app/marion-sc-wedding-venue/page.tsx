import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import { JsonLd } from "@/components/JsonLd";
import { RelatedPortfolio } from "@/components/RelatedPortfolio";
import { Reveal } from "@/components/Reveal";
import { getFeaturedWeddings, portfolioPath } from "@/lib/portfolioData";
import {
  ABOUT_PATH,
  ADDRESS,
  CONTACT_PATH,
  getSiteUrl,
  MARION_HUB_PATH,
  MARION_HUB_TITLE,
  PRIMARY_CITY,
  PRIMARY_STATE,
  PRIMARY_STATE_ABBR,
  SITE_NAME,
  VENUE_PATH,
} from "@/lib/siteConfig";

const description = `Host your wedding weekend at Hidden Acres — a secluded 37-acre ${PRIMARY_CITY}, ${PRIMARY_STATE_ABBR} wedding venue with chapel, ballroom, outdoor ceremonies, and on-site stays.`;

export const metadata: Metadata = {
  title: { absolute: MARION_HUB_TITLE },
  description,
  alternates: { canonical: MARION_HUB_PATH },
  openGraph: {
    title: MARION_HUB_TITLE,
    description,
    url: MARION_HUB_PATH,
  },
};

export default function MarionLocationHubPage() {
  const featured = getFeaturedWeddings(4);

  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "WeddingVenue",
          name: `${SITE_NAME} — ${PRIMARY_CITY}, ${PRIMARY_STATE_ABBR}`,
          description,
          url: `${getSiteUrl()}${MARION_HUB_PATH}`,
          address: {
            "@type": "PostalAddress",
            streetAddress: ADDRESS.street,
            addressLocality: ADDRESS.city,
            addressRegion: ADDRESS.state,
            postalCode: ADDRESS.zip,
            addressCountry: "US",
          },
        }}
      />

      <section
        id="hero-surface"
        className="relative min-h-[70svh] overflow-hidden pt-20"
      >
        <Image
          src="https://images.unsplash.com/photo-1522673607200-164d1b6ce486?auto=format&fit=crop&w=2200&q=80"
          alt="Outdoor wedding ceremony in a pastoral South Carolina setting"
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-deep/85 via-forest/45 to-forest/25" />
        <div className="relative z-10 mx-auto flex min-h-[70svh] max-w-7xl flex-col justify-end px-5 pb-16 md:px-8">
          <p className="eyebrow text-champagne-soft">Pee Dee wedding destination</p>
          <h1 className="mt-4 max-w-4xl font-script text-5xl leading-tight text-cream md:text-6xl lg:text-7xl">
            {PRIMARY_CITY}, {PRIMARY_STATE} Wedding Venue
          </h1>
          <p className="mt-5 max-w-2xl font-display text-2xl text-cream/90 md:text-3xl">
            Close enough for guests. Secluded enough to feel like yours alone.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button href={CONTACT_PATH} variant="onDark">
              Schedule a Marion tour
            </Button>
            <Button href={VENUE_PATH} variant="ghost">
              Venue tour
            </Button>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-20 md:px-8">
        <Reveal className="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 className="font-display text-3xl text-forest md:text-4xl">
              Why couples choose Marion
            </h2>
            <p className="mt-5 text-lg leading-relaxed text-muted">
              Historic downtown Marion is only about 10 minutes away, Florence
              about 30, and Myrtle Beach roughly an hour — so guests can arrive
              easily while your celebration stays secluded on 37 acres.
            </p>
            <p className="mt-4">
              <Link
                href={`${ABOUT_PATH}#directions`}
                className="text-champagne hover:text-forest"
              >
                Get driving directions →
              </Link>
            </p>
          </div>
          <div>
            <h2 className="font-display text-3xl text-forest md:text-4xl">
              Local landmarks nearby
            </h2>
            <ul className="mt-6 space-y-5">
              <li>
                <h3 className="font-display text-xl text-forest">
                  Historic Downtown Marion
                </h3>
                <p className="mt-1 text-sm text-muted">
                  A short drive for welcome dinners, coffee runs, and guest
                  exploring between Thursday and Sunday.
                </p>
              </li>
              <li>
                <h3 className="font-display text-xl text-forest">
                  Florence & the Pee Dee
                </h3>
                <p className="mt-1 text-sm text-muted">
                  Airport access and lodging options for out-of-town guests who
                  still want a countryside venue.
                </p>
              </li>
              <li>
                <h3 className="font-display text-xl text-forest">
                  Myrtle Beach day trips
                </h3>
                <p className="mt-1 text-sm text-muted">
                  Coastal energy an hour away — then return to quiet grounds for
                  the wedding weekend itself.
                </p>
              </li>
            </ul>
          </div>
        </Reveal>
      </section>

      <RelatedPortfolio
        weddings={featured}
        heading="Featured Marion weekends"
      />

      <section className="mx-auto max-w-7xl px-5 pb-8 md:px-8">
        <p className="text-sm text-muted">
          Exploring a specific wedding?{" "}
          <Link
            href={`${portfolioPath(featured[0]?.slug)}?from=${encodeURIComponent(MARION_HUB_PATH)}`}
            className="text-champagne hover:text-forest"
          >
            Start with {featured[0]?.couple}
          </Link>
          .
        </p>
      </section>

      <CtaBand
        headline="Tour Hidden Acres in Marion"
        supporting="We’ll walk The Chapel, Ballroom, outdoor ceremony sites, Silo, and lodging options with you."
        buttonLabel="Request a tour"
      />
    </>
  );
}
