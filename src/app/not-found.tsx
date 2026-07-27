import Link from "next/link";
import { Button } from "@/components/Button";
import { CONTACT_PATH, PORTFOLIO_PATH, VENUE_PATH } from "@/lib/siteConfig";

export default function NotFound() {
  return (
    <section className="mx-auto flex min-h-[70svh] max-w-3xl flex-col items-start justify-center px-5 py-28 md:px-8">
      <p className="eyebrow text-champagne">404</p>
      <h1 className="mt-4 font-script text-5xl text-forest md:text-6xl">
        This path is off the map
      </h1>
      <p className="mt-4 text-muted">
        The page you&apos;re looking for may have moved. Try the venue tour,
        portfolio, or get in touch for a tour.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Button href="/">Back home</Button>
        <Button href={VENUE_PATH} variant="secondary">
          Venue tour
        </Button>
        <Button href={CONTACT_PATH} variant="secondary">
          Contact
        </Button>
        <Link
          href={PORTFOLIO_PATH}
          className="inline-flex items-center px-2 text-sm text-champagne"
        >
          Portfolio →
        </Link>
      </div>
    </section>
  );
}
