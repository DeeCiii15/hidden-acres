import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import { FaqAccordion } from "@/components/FaqAccordion";
import { JsonLd } from "@/components/JsonLd";
import { Reveal } from "@/components/Reveal";
import {
  aboutIntro,
  directionRoutes,
  faqs,
  mapsQuery,
  vendorCategories,
} from "@/lib/aboutData";
import { media } from "@/lib/media";
import {
  ABOUT_PATH,
  ADDRESS,
  CONTACT,
  CONTACT_PATH,
  getSiteUrl,
  VENUE_PATH,
} from "@/lib/siteConfig";

const title = "About, FAQs, Vendors & Directions | Hidden Acres";
const description =
  "Learn about Hidden Acres in Marion, SC — FAQs, preferred vendors, and driving directions from Marion, I-95, and Conway.";

export const metadata: Metadata = {
  title: { absolute: title },
  description,
  alternates: { canonical: ABOUT_PATH },
  openGraph: {
    title,
    description,
    url: ABOUT_PATH,
  },
};

export default function AboutPage() {
  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "FAQPage",
          mainEntity: faqs.map((faq) => ({
            "@type": "Question",
            name: faq.question,
            acceptedAnswer: {
              "@type": "Answer",
              text: faq.answer,
            },
          })),
        }}
      />

      <section className="mx-auto max-w-7xl px-5 pb-12 pt-28 md:px-8">
        <Reveal className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <p className="eyebrow text-champagne">{aboutIntro.eyebrow}</p>
            <h1 className="mt-4 font-script text-5xl text-forest md:text-6xl lg:text-7xl">
              {aboutIntro.headline}
            </h1>
            <div className="prose-venue mt-6 text-muted">
              {aboutIntro.body.map((paragraph) => (
                <p key={paragraph.slice(0, 24)}>{paragraph}</p>
              ))}
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button href={CONTACT_PATH}>Schedule a tour</Button>
              <Button href={VENUE_PATH} variant="secondary">
                Tour the venue
              </Button>
            </div>
          </div>
          <div className="relative aspect-[4/5] overflow-hidden">
            <Image
              src={media.pond.primary}
              alt={media.pond.alt}
              fill
              sizes="(max-width: 1024px) 100vw, 45vw"
              className="object-cover"
              priority
            />
          </div>
        </Reveal>

        <nav className="mt-14 flex flex-wrap gap-2 border-y border-stroke py-4">
          {[
            { href: "#faq", label: "FAQs" },
            { href: "#vendors", label: "Preferred vendors" },
            { href: "#directions", label: "Directions" },
          ].map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="font-ui rounded-full border border-stroke bg-cream px-4 py-2 text-sm uppercase tracking-[0.16em] text-muted hover:text-forest"
            >
              {item.label}
            </a>
          ))}
        </nav>
      </section>

      <div id="faq" className="scroll-mt-28">
        <FaqAccordion items={faqs} heading="Frequently asked questions" />
        <div className="mx-auto max-w-3xl px-5 pb-10 md:px-8">
          <Button href={CONTACT_PATH} variant="secondary">
            Still have questions? Contact us
          </Button>
        </div>
      </div>

      <section
        id="vendors"
        className="scroll-mt-28 border-y border-stroke bg-paper-deep/45 py-20"
      >
        <div className="mx-auto max-w-7xl px-5 md:px-8">
          <Reveal>
            <p className="eyebrow text-champagne">Preferred vendors</p>
            <h2 className="mt-3 font-display text-3xl text-forest md:text-4xl">
              Past-client approved partners
            </h2>
            <p className="mt-4 max-w-2xl text-muted">
              You&apos;re free to choose any vendors you love. These partners
              have worked beautifully with Hidden Acres couples — call us if
              you&apos;d like a recommendation for what you need.
            </p>
          </Reveal>

          <div className="mt-12 grid gap-10 md:grid-cols-2">
            {vendorCategories.map((category) => (
              <Reveal key={category.slug}>
                <h3 className="font-display text-2xl text-forest">
                  {category.name}
                </h3>
                <ul className="mt-4 space-y-3">
                  {category.vendors.map((vendor) => (
                    <li
                      key={`${category.slug}-${vendor.name}`}
                      className="border-b border-stroke pb-3 text-sm"
                    >
                      <p className="text-ink">{vendor.name}</p>
                      {vendor.detail && (
                        <p className="text-muted">{vendor.detail}</p>
                      )}
                      <p className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-muted">
                        {vendor.phone && (
                          <a
                            href={`tel:+1${vendor.phone.replace(/\D/g, "")}`}
                            className="hover:text-champagne"
                          >
                            {vendor.phone}
                          </a>
                        )}
                        {vendor.email && (
                          <a
                            href={`mailto:${vendor.email}`}
                            className="hover:text-champagne"
                          >
                            {vendor.email}
                          </a>
                        )}
                        {vendor.url && (
                          <a
                            href={vendor.url}
                            target="_blank"
                            rel="noreferrer"
                            className="hover:text-champagne"
                          >
                            Website
                          </a>
                        )}
                      </p>
                    </li>
                  ))}
                </ul>
              </Reveal>
            ))}
          </div>

          <div className="mt-10">
            <Button href={CONTACT_PATH}>Ask for a vendor suggestion</Button>
          </div>
        </div>
      </section>

      <section id="directions" className="scroll-mt-28 py-20">
        <div className="mx-auto max-w-7xl px-5 md:px-8">
          <Reveal>
            <p className="eyebrow text-champagne">Find us</p>
            <h2 className="mt-3 font-display text-3xl text-forest md:text-4xl">
              Directions
            </h2>
            <p className="mt-4 max-w-2xl text-muted">
              We recommend printing these directions. Save the pin to your phone
              — cell service can be spotty on the last stretch.
            </p>
            <p className="mt-4 text-lg text-forest">{ADDRESS.full}</p>
            <p className="text-sm text-muted">{ADDRESS.gateNote}</p>
            <div className="mt-4 flex flex-wrap gap-3">
              <a
                href={`https://maps.google.com/?q=${mapsQuery}`}
                target="_blank"
                rel="noreferrer"
                className="font-ui inline-flex rounded-sm border border-forest/20 px-5 py-3.5 text-sm uppercase tracking-[0.16em] text-forest hover:bg-forest/5"
              >
                Open in Google Maps
              </a>
              <Link
                href={`mailto:${CONTACT.email}`}
                className="font-ui inline-flex px-2 py-3.5 text-sm uppercase tracking-[0.16em] text-champagne"
              >
                Email for help →
              </Link>
            </div>
          </Reveal>

          <div className="mt-12 grid gap-8 lg:grid-cols-3">
            {directionRoutes.map((route) => (
              <Reveal
                key={route.from}
                className="rounded-2xl border border-stroke bg-cream/70 p-6"
              >
                <h3 className="font-display text-2xl text-forest">
                  {route.from}
                </h3>
                <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm leading-relaxed text-muted">
                  {route.steps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ol>
              </Reveal>
            ))}
          </div>

          <div className="mt-12 overflow-hidden rounded-2xl border border-stroke">
            <iframe
              title="Hidden Acres map"
              src={`https://maps.google.com/maps?q=${mapsQuery}&z=13&output=embed`}
              className="h-80 w-full border-0 grayscale-[20%]"
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            />
          </div>
        </div>
      </section>

      <CtaBand
        headline="Come see it for yourself"
        supporting="Tours are the best way to feel the Chapel light, Silo character, and Ballroom glow in person."
        buttonLabel="Request a tour"
      />

      <span className="sr-only">{getSiteUrl()}</span>
    </>
  );
}
