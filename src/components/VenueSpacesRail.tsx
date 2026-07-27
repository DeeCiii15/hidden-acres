"use client";

import Image from "next/image";
import Link from "next/link";
import { useRef, useState, useEffect } from "react";
import { type VenueSpace } from "@/lib/venueData";
import { VENUE_PATH } from "@/lib/siteConfig";

export function VenueSpacesRail({ spaces }: { spaces: VenueSpace[] }) {
  const scrollerRef = useRef<HTMLUListElement>(null);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(true);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;

    const sync = () => {
      const max = el.scrollWidth - el.clientWidth;
      setCanPrev(el.scrollLeft > 8);
      setCanNext(el.scrollLeft < max - 8);
    };

    sync();
    el.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    return () => {
      el.removeEventListener("scroll", sync);
      window.removeEventListener("resize", sync);
    };
  }, [spaces.length]);

  const scrollByCards = (dir: -1 | 1) => {
    const el = scrollerRef.current;
    if (!el) return;
    const card = el.querySelector("li");
    const step = card ? card.getBoundingClientRect().width + 16 : el.clientWidth * 0.7;
    el.scrollBy({ left: dir * step, behavior: "smooth" });
  };

  return (
    <div className="relative mt-12">
      <div className="mb-5 flex items-center justify-between gap-4">
        <p className="font-ui text-[11px] uppercase tracking-[0.18em] text-muted">
          {spaces.length} spaces · scroll to explore
        </p>
        <div className="flex gap-2">
          <button
            type="button"
            aria-label="Previous spaces"
            disabled={!canPrev}
            onClick={() => scrollByCards(-1)}
            className="font-ui inline-flex h-10 w-10 items-center justify-center border border-[#2c3b32]/20 text-[#2c3b32] transition enabled:hover:bg-[#2c3b32] enabled:hover:text-white disabled:opacity-30"
          >
            ←
          </button>
          <button
            type="button"
            aria-label="Next spaces"
            disabled={!canNext}
            onClick={() => scrollByCards(1)}
            className="font-ui inline-flex h-10 w-10 items-center justify-center border border-[#2c3b32]/20 text-[#2c3b32] transition enabled:hover:bg-[#2c3b32] enabled:hover:text-white disabled:opacity-30"
          >
            →
          </button>
        </div>
      </div>

      <ul
        ref={scrollerRef}
        className="no-scrollbar flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2"
      >
        {spaces.map((space) => (
          <li
            key={space.slug}
            className="w-[78%] shrink-0 snap-start sm:w-[46%] lg:w-[calc((100%-3rem)/4)]"
          >
            <Link
              href={`${VENUE_PATH}#${space.slug}`}
              className="group block h-full"
            >
              <div className="relative aspect-[4/5] overflow-hidden">
                <Image
                  src={space.image}
                  alt={space.imageAlt}
                  fill
                  sizes="(max-width: 640px) 78vw, (max-width: 1024px) 46vw, 25vw"
                  className="object-cover transition duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-forest-deep/75 via-transparent to-transparent opacity-90" />
                <div className="absolute inset-x-0 bottom-0 p-4 md:p-5">
                  <p className="eyebrow text-champagne-soft">{space.eyebrow}</p>
                  <h3 className="mt-1 font-display text-2xl text-cream md:text-[1.65rem]">
                    {space.name}
                  </h3>
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
