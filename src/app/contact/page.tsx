import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/Button";
import { ContactForm } from "@/components/ContactForm";
import { JsonLd } from "@/components/JsonLd";
import { Reveal } from "@/components/Reveal";
import {
  ABOUT_PATH,
  ADDRESS,
  CONTACT,
  getSiteUrl,
  PORTFOLIO_PATH,
  SITE_NAME,
  SOCIAL,
} from "@/lib/siteConfig";

const title = "Contact & Tour Scheduling | Hidden Acres";
const description =
  "Schedule a tour of Hidden Acres in Marion, SC. Ask about Thursday–Sunday wedding weekend packages, pricing, and on-site lodging.";

export const metadata: Metadata = {
  title: { absolute: title },
  description,
  alternates: { canonical: "/contact" },
  openGraph: {
    title,
    description,
    url: "/contact",
  },
};

export default function ContactPage() {
  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "ContactPage",
          name: title,
          url: `${getSiteUrl()}/contact`,
          mainEntity: {
            "@type": "WeddingVenue",
            name: SITE_NAME,
            email: CONTACT.email,
            telephone: CONTACT.phoneHref.replace("tel:", ""),
            address: {
              "@type": "PostalAddress",
              streetAddress: ADDRESS.street,
              addressLocality: ADDRESS.city,
              addressRegion: ADDRESS.state,
              postalCode: ADDRESS.zip,
              addressCountry: "US",
            },
          },
        }}
      />

      <section className="relative overflow-hidden pt-28">
        <div className="absolute inset-0 -z-10">
          <Image
            src="https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?auto=format&fit=crop&w=2000&q=80"
            alt="Soft outdoor wedding setting with greenery"
            fill
            priority
            className="object-cover opacity-30"
            sizes="100vw"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-cream via-paper/90 to-paper" />
        </div>

        <div className="mx-auto grid max-w-7xl gap-10 px-5 pb-20 md:gap-14 md:px-8 lg:grid-cols-[0.95fr_1.05fr] lg:gap-x-14 lg:gap-y-0">
          {/* Intro stays first on mobile; left column top on desktop */}
          <Reveal className="order-1 lg:col-start-1 lg:row-start-1">
            <p className="eyebrow text-champagne">Get in touch</p>
            <h1 className="mt-4 font-script text-5xl text-forest md:text-6xl lg:text-7xl">
              Come walk the grounds with us
            </h1>
            <p className="mt-5 max-w-lg text-lg text-muted">
              Tell us about your date, guest count, and the kind of weekend
              you&apos;re dreaming of. We&apos;d love to show you Hidden Acres
              in person.
            </p>
          </Reveal>

          {/* Form before email/phone/address on mobile; right column on desktop */}
          <Reveal className="order-2 lg:col-start-2 lg:row-start-1 lg:row-span-2">
            <div className="rounded-2xl border border-stroke bg-cream/85 p-6 shadow-[0_30px_60px_-40px_rgba(26,38,32,0.45)] md:p-8">
              <ContactForm />
            </div>
            <p className="mt-6 text-sm text-muted">
              Prefer to browse first?{" "}
              <Link href={PORTFOLIO_PATH} className="text-champagne hover:underline">
                See the portfolio
              </Link>{" "}
              or read{" "}
              <Link href={`${ABOUT_PATH}#faq`} className="text-champagne hover:underline">
                FAQs
              </Link>
              .
            </p>
          </Reveal>

          <Reveal className="order-3 lg:col-start-1 lg:row-start-2 lg:mt-10">
            <div className="space-y-4 text-sm">
              <p>
                <span className="text-muted">Email</span>
                <br />
                <a
                  href={`mailto:${CONTACT.email}`}
                  className="text-lg text-forest transition hover:text-champagne"
                >
                  {CONTACT.email}
                </a>
              </p>
              <p>
                <span className="text-muted">Phone</span>
                <br />
                <a
                  href={CONTACT.phoneHref}
                  className="text-lg text-forest transition hover:text-champagne"
                >
                  {CONTACT.phoneDisplay}
                </a>
              </p>
              <p>
                <span className="text-muted">Visit</span>
                <br />
                <span className="text-lg text-forest">{ADDRESS.full}</span>
              </p>
              <p className="pt-2 text-muted">
                Follow along on{" "}
                <a
                  href={SOCIAL.instagram}
                  className="text-champagne hover:underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  Instagram
                </a>{" "}
                and{" "}
                <a
                  href={SOCIAL.facebook}
                  className="text-champagne hover:underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  Facebook
                </a>
                .
              </p>
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button href={`${ABOUT_PATH}#directions`} variant="secondary">
                Get directions
              </Button>
            </div>
          </Reveal>
        </div>
      </section>
    </>
  );
}
