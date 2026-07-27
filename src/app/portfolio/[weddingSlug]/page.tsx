import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Button } from "@/components/Button";
import { CtaBand } from "@/components/CtaBand";
import { Reveal } from "@/components/Reveal";
import {
  getAllWeddingSlugs,
  getWedding,
  portfolioPath,
} from "@/lib/portfolioData";
import {
  CONTACT_PATH,
  MARION_HUB_PATH,
  PORTFOLIO_PATH,
  VENUE_PATH,
} from "@/lib/siteConfig";
import { getSpace, venueSpacePath } from "@/lib/venueData";
import { getLiveLocationForCityId } from "@/lib/locations";

type PageProps = {
  params: Promise<{ weddingSlug: string }>;
  searchParams: Promise<{ from?: string }>;
};

export function generateStaticParams() {
  return getAllWeddingSlugs().map((weddingSlug) => ({ weddingSlug }));
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { weddingSlug } = await params;
  const wedding = getWedding(weddingSlug);
  if (!wedding) return {};

  return {
    title: `${wedding.couple} — ${wedding.title}`,
    description: wedding.summary,
    alternates: { canonical: portfolioPath(wedding.slug) },
    openGraph: {
      title: `${wedding.couple} | Hidden Acres`,
      description: wedding.summary,
      url: portfolioPath(wedding.slug),
      images: [{ url: wedding.coverImage, alt: wedding.coverAlt }],
    },
  };
}

export default async function PortfolioWeddingPage({
  params,
  searchParams,
}: PageProps) {
  const { weddingSlug } = await params;
  const { from } = await searchParams;
  const wedding = getWedding(weddingSlug);
  if (!wedding) notFound();

  const location = getLiveLocationForCityId(wedding.cityId);
  const backHref =
    from?.startsWith("/") && !from.startsWith("//") ? from : PORTFOLIO_PATH;

  return (
    <article className="pb-8">
      <div className="relative min-h-[65svh] overflow-hidden pt-20">
        <Image
          src={wedding.coverImage}
          alt={wedding.coverAlt}
          fill
          priority
          sizes="100vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-deep/85 via-forest/35 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 mx-auto max-w-7xl px-5 pb-12 md:px-8">
          <p className="eyebrow text-champagne-soft">
            <Link href={PORTFOLIO_PATH} className="hover:text-cream">
              Portfolio
            </Link>
            {" / "}
            {wedding.dateLabel}
          </p>
          <h1 className="mt-3 font-script text-5xl text-cream md:text-6xl lg:text-7xl">
            {wedding.couple}
          </h1>
          <p className="mt-3 font-display text-2xl text-cream/90 md:text-3xl">
            {wedding.title}
          </p>
        </div>
      </div>

      <div className="mx-auto grid max-w-7xl gap-12 px-5 py-14 md:px-8 lg:grid-cols-[1.25fr_0.75fr]">
        <Reveal>
          <p className="text-lg leading-relaxed text-muted md:text-xl">
            {wedding.story}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button href={CONTACT_PATH}>Plan a similar weekend</Button>
            <Button href={VENUE_PATH} variant="secondary">
              Tour these spaces
            </Button>
          </div>
        </Reveal>

        <Reveal className="space-y-5 border-l border-stroke pl-6 text-sm">
          <div>
            <p className="eyebrow text-muted">Spaces featured</p>
            <ul className="mt-3 space-y-2">
              {wedding.spacesUsed.map((slug) => {
                const space = getSpace(slug);
                if (!space) return null;
                return (
                  <li key={slug}>
                    <Link
                      href={venueSpacePath(slug)}
                      className="text-forest transition hover:text-champagne"
                    >
                      {space.name}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
          {location && (
            <p>
              <span className="text-muted">Location</span>
              <br />
              <Link
                href={`${location.path}?from=${encodeURIComponent(portfolioPath(wedding.slug))}`}
                className="text-forest hover:text-champagne"
              >
                {location.city}, {location.region} wedding venue
              </Link>
            </p>
          )}
          <p>
            <Link href={backHref} className="text-champagne hover:text-forest">
              ← Back
            </Link>
          </p>
        </Reveal>
      </div>

      <section className="mx-auto max-w-7xl px-5 pb-16 md:px-8">
        <h2 className="font-display text-3xl text-forest">Gallery</h2>
        <ul className="mt-8 columns-1 gap-4 sm:columns-2 lg:columns-3">
          {wedding.photos.map((photo) => (
            <li key={photo.src} className="mb-4 break-inside-avoid">
              <div className="relative aspect-[4/5] overflow-hidden">
                <Image
                  src={photo.src}
                  alt={photo.alt}
                  fill
                  sizes="(max-width: 768px) 100vw, 33vw"
                  className="object-cover"
                />
              </div>
            </li>
          ))}
        </ul>
      </section>

      <CtaBand
        headline="Fall in love with the grounds"
        supporting="Schedule a tour and we’ll show you every space from this gallery — in person."
        buttonLabel="Schedule a tour"
      />

      {!location && (
        <p className="sr-only">
          Related hub: {MARION_HUB_PATH}
        </p>
      )}
    </article>
  );
}
