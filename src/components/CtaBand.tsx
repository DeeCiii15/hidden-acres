import { Button } from "./Button";
import { Reveal } from "./Reveal";
import { CONTACT_PATH } from "@/lib/siteConfig";

export function CtaBand({
  headline,
  buttonLabel = "Schedule a tour",
  supporting,
}: {
  headline: string;
  buttonLabel?: string;
  supporting?: string;
}) {
  return (
    <section className="cta-band relative mb-12 overflow-hidden bg-forest py-9 text-cream md:mb-16 md:py-10">
      <div
        className="pointer-events-none absolute inset-0 opacity-35"
        style={{
          background:
            "radial-gradient(600px 280px at 18% 20%, #9c8160, transparent), radial-gradient(500px 260px at 90% 80%, #8a9878, transparent)",
        }}
      />
      <Reveal className="relative mx-auto max-w-4xl px-5 text-center md:px-8">
        <p className="eyebrow text-champagne-soft">Next chapter</p>
        <h2 className="mt-2.5 font-script text-[2.35rem] leading-none md:text-5xl lg:text-[3.15rem]">
          {headline}
        </h2>
        {supporting && (
          <p className="mx-auto mt-2.5 max-w-xl text-[0.98rem] text-cream/70">
            {supporting}
          </p>
        )}
        <div className="mt-5 flex justify-center">
          <Button href={CONTACT_PATH} variant="onDark">
            {buttonLabel}
          </Button>
        </div>
      </Reveal>
    </section>
  );
}
