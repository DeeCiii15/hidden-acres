import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import { JsonLd } from "@/components/JsonLd";
import { RelatedPortfolio } from "@/components/RelatedPortfolio";
import { Reveal } from "@/components/Reveal";
import { media } from "@/lib/media";
import { getFeaturedWeddings, getWeddingsUsingSpace } from "@/lib/portfolioData";
import {
  CONTACT_PATH,
  getSiteUrl,
  PORTFOLIO_PATH,
  VENUE_PATH,
  VENUE_TOUR_VIDEO,
  WEDDING_PATH,
} from "@/lib/siteConfig";
import { venueSpaces } from "@/lib/venueData";

const title = "Venue Tour — Chapel, Ballroom, Pond, Silo & More | Hidden Acres";
const description =
  "Tour Hidden Acres in Marion, SC: The Chapel, Ceremony Pond, Ballroom, Courtyard & Pavilion, Rusted Silo, Inn, Bridal Suite, and Groom’s Quarters.";

export const metadata: Metadata = {
  title: { absolute: title },
  description,
  alternates: { canonical: VENUE_PATH },
  openGraph: {
    title,
    description,
    url: VENUE_PATH,
    images: [{ url: media.grounds, alt: media.groundsAlt }],
  },
};

export default function VenuePage() {
  const featured = getFeaturedWeddings(3);

  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "TouristAttraction",
          name: "Hidden Acres Wedding Venue Tour",
          description,
          url: `${getSiteUrl()}${VENUE_PATH}`,
        }}
      />

      <section
        id="hero-surface"
        className="relative min-h-[78svh] overflow-hidden pt-20"
      >
        <Image
          src={media.grounds}
          alt={media.groundsAlt}
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-deep/90 via-forest-deep/55 to-forest/30" />
        <div className="relative z-10 mx-auto flex min-h-[78svh] max-w-7xl flex-col justify-end px-5 pb-16 md:px-8">
          <p className="eyebrow text-champagne-soft">The venue</p>
          <h1 className="mt-4 max-w-4xl font-script text-5xl leading-tight text-cream md:text-6xl lg:text-7xl">
            Walk the grounds
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-cream/90 md:text-xl">
            Chapel, pond, ballroom, courtyard, silo, inn, and getting-ready
            suites — every space on one private property in Marion, SC.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button href={CONTACT_PATH} variant="onDark">
              Schedule a tour
            </Button>
            <Button href={WEDDING_PATH} variant="ghost">
              Wedding packages
            </Button>
          </div>
        </div>
      </section>

      <section className="border-b border-stroke bg-[#f3f0e8]">
        <div className="mx-auto flex max-w-7xl gap-x-6 gap-y-2 overflow-x-auto px-5 py-4 md:px-8">
          <a
            href="#video-tour"
            className="font-ui shrink-0 text-sm uppercase tracking-[0.16em] text-[#2c3b32]/70 transition hover:text-[#2c3b32]"
          >
            Video tour
          </a>
          {venueSpaces.map((space) => (
            <a
              key={space.slug}
              href={`#${space.slug}`}
              className="font-ui shrink-0 text-sm uppercase tracking-[0.16em] text-[#2c3b32]/70 transition hover:text-[#2c3b32]"
            >
              {space.navLabel}
            </a>
          ))}
        </div>
      </section>

      <section
        id="video-tour"
        className="scroll-mt-24 border-b border-stroke bg-paper"
      >
        <div className="mx-auto max-w-7xl px-5 py-16 md:px-8 md:py-20">
          <Reveal>
            <p className="eyebrow text-champagne">See the property</p>
            <h2 className="mt-3 max-w-2xl font-script text-4xl text-forest md:text-5xl">
              Venue video tour
            </h2>
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-ink/85 md:text-lg">
              {VENUE_TOUR_VIDEO.credit}
            </p>
          </Reveal>
          <Reveal className="mt-10">
            <div className="relative aspect-video overflow-hidden border border-[#2c3b32]/10 bg-forest-deep">
              <iframe
                src={VENUE_TOUR_VIDEO.embedUrl}
                title={VENUE_TOUR_VIDEO.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                className="absolute inset-0 h-full w-full"
              />
            </div>
          </Reveal>
        </div>
      </section>

      <div>
        {venueSpaces.map((space, index) => {
          const related = getWeddingsUsingSpace(space.slug).slice(0, 1);
          const reverse = index % 2 === 1;

          return (
            <section
              key={space.slug}
              id={space.slug}
              className={`scroll-mt-24 border-t border-stroke ${
                index % 2 === 0 ? "bg-paper" : "bg-paper-deep/50"
              }`}
            >
              <div className="mx-auto grid max-w-7xl items-center gap-10 px-5 py-16 md:px-8 md:py-20 lg:grid-cols-2">
                <Reveal className={`relative ${reverse ? "lg:order-2" : ""}`}>
                  <div className="relative aspect-[4/5] overflow-hidden md:aspect-[5/4]">
                    <Image
                      src={space.image}
                      alt={space.imageAlt}
                      fill
                      sizes="(max-width: 1024px) 100vw, 50vw"
                      className="object-cover"
                    />
                  </div>
                  {space.secondaryImage && (
                    <div className="frame-overlap absolute -bottom-6 -right-2 hidden w-[42%] overflow-hidden md:block lg:-right-6">
                      <div className="relative aspect-[4/5]">
                        <Image
                          src={space.secondaryImage}
                          alt={space.secondaryImageAlt ?? space.name}
                          fill
                          sizes="20vw"
                          className="object-cover"
                        />
                      </div>
                    </div>
                  )}
                </Reveal>

                <Reveal className={reverse ? "lg:order-1" : ""}>
                  <p className="eyebrow text-champagne">{space.eyebrow}</p>
                  <h2 className="mt-3 font-display text-3xl text-forest md:text-5xl">
                    {space.name}
                  </h2>
                  <p className="mt-4 text-lg leading-relaxed text-ink/90">
                    {space.summary}
                  </p>
                  <p className="mt-4 text-base leading-relaxed text-ink/80">
                    {space.body}
                  </p>
                  <ul className="mt-6 space-y-2">
                    {space.highlights.map((item) => (
                      <li
                        key={item}
                        className="border-l border-champagne/50 pl-3 text-sm text-ink"
                      >
                        {item}
                      </li>
                    ))}
                  </ul>
                  <div className="mt-8 flex flex-wrap items-center gap-4">
                    <Button href={CONTACT_PATH} variant="primary">
                      Ask about this space
                    </Button>
                    {related[0] && (
                      <Link
                        href={`/portfolio/${related[0].slug}`}
                        className="font-ui text-sm uppercase tracking-[0.16em] text-champagne hover:text-forest"
                      >
                        See it in a real wedding →
                      </Link>
                    )}
                  </div>
                </Reveal>
              </div>
            </section>
          );
        })}
      </div>

      <RelatedPortfolio
        weddings={featured}
        heading="These spaces, in real weekends"
      />

      <CtaBand
        headline="Ready to tour in person?"
        supporting="We’ll walk the property with you and talk through your weekend."
        buttonLabel="Schedule a tour"
      />

      <span className="sr-only">{PORTFOLIO_PATH}</span>
    </>
  );
}
