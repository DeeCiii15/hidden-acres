import Image from "next/image";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import { JsonLd } from "@/components/JsonLd";
import { RelatedPortfolio } from "@/components/RelatedPortfolio";
import { Reveal } from "@/components/Reveal";
import { Testimonials } from "@/components/Testimonials";
import { VenueMapExplorer } from "@/components/VenueMapExplorer";
import { media } from "@/lib/media";
import { getFeaturedWeddings } from "@/lib/portfolioData";
import {
  ADDRESS,
  CONTACT,
  CONTACT_PATH,
  getSiteUrl,
  HOME_DESCRIPTION,
  HOME_TITLE,
  SITE_MOOD,
  SITE_NAME,
  VENUE_PATH,
  WEDDING_PATH,
} from "@/lib/siteConfig";
import { testimonials } from "@/lib/testimonials";
import { venueSpaces } from "@/lib/venueData";

export default function HomePage() {
  const featured = getFeaturedWeddings(5);
  const siteUrl = getSiteUrl();

  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "WeddingVenue",
          name: SITE_NAME,
          description: HOME_DESCRIPTION,
          url: siteUrl,
          telephone: CONTACT.phoneHref.replace("tel:", ""),
          email: CONTACT.email,
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
        className="relative min-h-[100svh] overflow-hidden"
      >
        <div className="absolute inset-0">
          <Image
            src={media.hero}
            alt={media.heroAlt}
            fill
            priority
            quality={95}
            sizes="100vw"
            className="object-cover object-center"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-forest-deep/85 via-forest-deep/35 to-black/25" />
        </div>

        <div className="relative z-10 flex min-h-[100svh] flex-col justify-end px-5 pb-16 pt-28 md:px-8 md:pb-24">
          <div className="mx-auto w-full max-w-7xl">
            <p className="eyebrow animate-rise text-champagne-soft">
              Marion, SC · Pee Dee · Wedding weekends
            </p>
            <h1 className="animate-rise-delay-1 mt-5 max-w-4xl font-script text-5xl leading-[1.02] text-cream md:text-7xl lg:text-[5.5rem]">
              Hidden Acres
            </h1>
            <p className="animate-rise-delay-2 mt-4 max-w-xl font-display text-2xl leading-snug text-cream/95 md:text-3xl lg:text-4xl">
              {SITE_MOOD}
            </p>
            <div className="animate-rise-delay-3 mt-9 flex flex-wrap gap-3">
              <Button href={VENUE_PATH} variant="onDark">
                Tour the venue
              </Button>
              <Button href={CONTACT_PATH} variant="ghost">
                Inquire
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-20 md:px-8 md:py-28">
        <Reveal className="grid items-center gap-10 lg:grid-cols-2 lg:gap-14">
          <div className="relative aspect-[4/5] overflow-hidden md:aspect-[5/4]">
            <Image
              src={media.welcome}
              alt={media.welcomeAlt}
              fill
              sizes="(max-width: 1024px) 100vw, 50vw"
              className="object-cover object-[center_30%]"
            />
          </div>
          <div>
            <h2 className="font-script text-4xl leading-snug text-forest md:text-5xl lg:text-6xl">
              A private wedding weekend in Marion, SC
            </h2>
            <div className="mt-6 space-y-4 text-base leading-relaxed text-ink md:text-lg">
              <p>
                Hidden Acres is the perfect location for your dream wedding. It
                offers rustic charm, natural beauty, a secluded pastoral
                setting, and unexpected modern amenities.
              </p>
              <p>
                Neatly tucked into the countryside (just 10 minutes from
                historic downtown Marion, 30 minutes from Florence, and one hour
                from Myrtle Beach), Hidden Acres is a beautiful setting for your
                dream wedding.
              </p>
              <p>
                Let us help you create memories that you&apos;ll cherish for a
                lifetime.
              </p>
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button href={VENUE_PATH} variant="secondary">
                Explore every space
              </Button>
              <Button href={WEDDING_PATH}>Wedding details</Button>
            </div>
          </div>
        </Reveal>
      </section>

      <section className="border-y border-stroke bg-paper-deep/60 py-12 md:py-16">
        <div className="mx-auto max-w-7xl px-5 md:px-8">
          <Reveal>
            <h2 className="text-center font-script text-4xl text-forest md:text-5xl lg:text-6xl">
              The venue
            </h2>
          </Reveal>
          <VenueMapExplorer spaces={venueSpaces} />
        </div>
      </section>

      <RelatedPortfolio weddings={featured} />

      <Testimonials items={testimonials} />

      <CtaBand
        headline="Ready to walk the grounds?"
        supporting="Tell us your date and guest count — we’d love to show you Hidden Acres."
        buttonLabel="Reach out"
      />

      <span className="sr-only">{HOME_TITLE}</span>
    </>
  );
}
