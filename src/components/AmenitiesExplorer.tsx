"use client";

import Image from "next/image";
import { useState } from "react";
import { type WeddingAmenity } from "@/lib/weddingData";

export function AmenitiesExplorer({ items }: { items: WeddingAmenity[] }) {
  const [active, setActive] = useState(0);
  const current = items[active] ?? items[0];

  return (
    <div className="mt-12 grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:gap-12 lg:items-start">
      <ul className="divide-y divide-[#2c3b32]/12 border-y border-[#2c3b32]/12">
        {items.map((item, index) => {
          const isActive = index === active;
          return (
            <li key={item.title}>
              <button
                type="button"
                onMouseEnter={() => setActive(index)}
                onFocus={() => setActive(index)}
                onClick={() => setActive(index)}
                aria-pressed={isActive}
                className={`group flex w-full items-center justify-between gap-4 py-5 text-left transition ${
                  isActive ? "bg-[#2c3b32]/[0.04]" : "hover:bg-[#2c3b32]/[0.03]"
                }`}
              >
                <span
                  className={`block font-display text-xl transition md:text-2xl ${
                    isActive
                      ? "text-forest"
                      : "text-forest/75 group-hover:text-forest"
                  }`}
                >
                  {item.title}
                </span>
                <span
                  aria-hidden
                  className={`shrink-0 font-ui text-[11px] uppercase tracking-[0.16em] transition ${
                    isActive
                      ? "text-champagne opacity-100"
                      : "text-[#2c3b32]/30 opacity-0 group-hover:opacity-100"
                  }`}
                >
                  Included
                </span>
              </button>
            </li>
          );
        })}
      </ul>

      <div className="sticky top-28 hidden lg:block">
        <div className="overflow-hidden border border-[#2c3b32]/10 bg-[#f7f3ea]">
          <div className="relative aspect-[5/4]">
            <Image
              key={current.title}
              src={current.image}
              alt={current.imageAlt}
              fill
              sizes="(max-width: 1024px) 100vw, 45vw"
              className="object-cover"
            />
          </div>
          <div className="border-t border-[#2c3b32]/10 px-6 py-5">
            <p className="eyebrow text-champagne">Included with your rental</p>
            <p className="mt-2 font-display text-2xl text-forest">
              {current.title}
            </p>
            <p className="mt-3 text-sm leading-relaxed text-ink/80 md:text-base">
              {current.detail}
            </p>
          </div>
        </div>
      </div>

      {/* Mobile: preview follows the selected amenity */}
      <div className="lg:hidden">
        <div className="overflow-hidden border border-[#2c3b32]/10">
          <div className="relative aspect-[5/4]">
            <Image
              key={`m-${current.title}`}
              src={current.image}
              alt={current.imageAlt}
              fill
              sizes="100vw"
              className="object-cover"
            />
          </div>
          <div className="border-t border-[#2c3b32]/10 px-5 py-4">
            <p className="font-display text-xl text-forest">{current.title}</p>
            <p className="mt-2 text-sm leading-relaxed text-ink/80">
              {current.detail}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
