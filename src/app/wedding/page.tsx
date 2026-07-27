import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { AmenitiesExplorer } from "@/components/AmenitiesExplorer";
import { AmenitiesPdfDownload } from "@/components/AmenitiesPdfDownload";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import { Reveal } from "@/components/Reveal";
import { media } from "@/lib/media";
import {
  CONTACT,
  CONTACT_PATH,
  VENUE_PATH,
  WEDDING_PATH,
} from "@/lib/siteConfig";
import { weddingPage } from "@/lib/weddingData";

const title = "Wedding Packages, Pricing & Amenities | Hidden Acres";
const description =
  "What’s included in a Hidden Acres wedding weekend in Marion, SC — tables, chairs, rain plan, ceremony and reception options. Tour to receive package pricing.";

export const metadata: Metadata = {
  title: { absolute: title },
  description,
  alternates: { canonical: WEDDING_PATH },
  openGraph: {
    title,
    description,
    url: WEDDING_PATH,
    images: [{ url: media.wedding.hero, alt: media.wedding.heroAlt }],
  },
};

export default function WeddingPage() {
  return (
    <>
      <section
        id="hero-surface"
        className="relative min-h-[70svh] overflow-hidden pt-20"
      >
        <Image
          src={media.wedding.hero}
          alt={media.wedding.heroAlt}
          fill
          priority
          quality={90}
          className="object-cover object-[center_30%]"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-deep/90 via-forest-deep/55 to-forest/25" />
        <div className="relative z-10 mx-auto flex min-h-[70svh] max-w-7xl flex-col justify-end px-5 pb-16 md:px-8">
          <p className="eyebrow text-champagne-soft">{weddingPage.eyebrow}</p>
          <h1 className="mt-4 max-w-4xl font-script text-5xl leading-tight text-cream md:text-6xl lg:text-7xl">
            {weddingPage.headline}
          </h1>
          <p className="mt-5 max-w-2xl text-lg text-cream/90">
            {weddingPage.intro}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button href={CONTACT_PATH} variant="onDark">
              Inquire about pricing
            </Button>
            <Button href={VENUE_PATH} variant="ghost">
              Tour the venue
            </Button>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 md:px-8 md:py-24">
        <Reveal>
          <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="eyebrow text-champagne">What’s included</p>
              <h2 className="mt-3 font-script text-4xl text-forest md:text-5xl">
                Amenities with your venue rental
              </h2>
              <p className="mt-4 max-w-2xl text-base leading-relaxed text-ink/85">
                {weddingPage.pricingNote}
              </p>
            </div>
            <AmenitiesPdfDownload />
          </div>
        </Reveal>

        <AmenitiesExplorer items={weddingPage.included} />

        <div className="mt-12 flex flex-wrap gap-3">
          <Button href={CONTACT_PATH}>Call or email for package pricing</Button>
          <a
            href={CONTACT.phoneHref}
            className="font-ui inline-flex items-center px-2 text-sm uppercase tracking-[0.16em] text-champagne hover:text-forest"
          >
            {CONTACT.phoneDisplay}
          </a>
        </div>
      </section>

      <section className="border-t border-stroke">
        <div className="mx-auto max-w-7xl px-5 pt-16 md:px-8 md:pt-20">
          <Reveal>
            <p className="eyebrow text-champagne">How the weekend flows</p>
            <h2 className="mt-3 font-script text-4xl text-forest md:text-5xl">
              Getting ready through reception
            </h2>
          </Reveal>
        </div>

        <div className="mt-6 md:mt-10">
          {weddingPage.sections.map((section, index) => {
            const reverse = index % 2 === 1;
            return (
              <div
                key={section.title}
                className={`border-t border-stroke ${
                  index % 2 === 0 ? "bg-paper" : "bg-paper-deep/45"
                }`}
              >
                <div className="mx-auto grid max-w-7xl items-center gap-10 px-5 py-14 md:px-8 md:py-20 lg:grid-cols-2 lg:gap-14">
                  <Reveal
                    className={`relative ${reverse ? "lg:order-2" : ""}`}
                  >
                    <div className="relative aspect-[4/5] overflow-hidden md:aspect-[5/4]">
                      <Image
                        src={section.image}
                        alt={section.imageAlt}
                        fill
                        sizes="(max-width: 1024px) 100vw, 50vw"
                        className="object-cover"
                      />
                    </div>
                    {section.secondaryImage && (
                      <div className="frame-overlap absolute -bottom-5 -right-2 hidden w-[44%] overflow-hidden md:block lg:-right-5">
                        <div className="relative aspect-[4/5]">
                          <Image
                            src={section.secondaryImage}
                            alt={
                              section.secondaryImageAlt ?? section.imageAlt
                            }
                            fill
                            sizes="22vw"
                            className="object-cover"
                          />
                        </div>
                      </div>
                    )}
                  </Reveal>

                  <Reveal className={reverse ? "lg:order-1" : ""}>
                    <h3 className="font-display text-3xl text-forest md:text-4xl">
                      {section.title}
                    </h3>
                    <div className="mt-5 space-y-3 text-base leading-relaxed text-ink/85 md:text-lg">
                      {section.body.map((paragraph) => (
                        <p key={paragraph.slice(0, 48)}>{paragraph}</p>
                      ))}
                    </div>
                    {section.links && (
                      <div className="mt-6 flex flex-wrap gap-x-5 gap-y-2">
                        {section.links.map((link) => (
                          <Link
                            key={link.href}
                            href={link.href}
                            className="font-ui text-sm uppercase tracking-[0.16em] text-champagne hover:text-forest"
                          >
                            {link.label} →
                          </Link>
                        ))}
                      </div>
                    )}
                  </Reveal>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 md:px-8 md:py-20">
        <Reveal>
          <h2 className="font-display text-3xl text-forest md:text-4xl">
            Other good things to know
          </h2>
          <ul className="mt-8 max-w-3xl space-y-4">
            {weddingPage.goodToKnow.map((item) => (
              <li
                key={item}
                className="border-l border-champagne/50 pl-4 text-base leading-relaxed text-ink"
              >
                {item}
              </li>
            ))}
          </ul>
          <div className="mt-10 flex flex-wrap gap-3">
            <Button href={CONTACT_PATH}>Schedule a tour</Button>
            <Button href="/about#faq" variant="secondary">
              Read FAQs
            </Button>
          </div>
        </Reveal>
      </section>

      <CtaBand
        headline="Let’s talk about your date"
        supporting="Tour the property and we’ll share current wedding package pricing for your weekend."
        buttonLabel="Contact Hidden Acres"
      />
    </>
  );
}
