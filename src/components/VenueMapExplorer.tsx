"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";
import {
  MAP_IMAGE,
  MAP_IMAGE_HEIGHT,
  MAP_IMAGE_WIDTH,
  mapPins,
  SLOT_DEFAULTS,
  SLOT_LAYOUT,
  type MapPin,
  type MapPinSlot,
} from "@/lib/mapPins";
import { VENUE_PATH } from "@/lib/siteConfig";
import { type VenueSpace } from "@/lib/venueData";

/** Focused crop when the source photo is wide / off-center */
const objectPositionBySlug: Record<string, string> = {
  "rusted-silo": "center center",
  "ceremony-pond": "center 48%",
};

const SLOT_ORDER: MapPinSlot[] = ["top-left", "mid-right", "bottom-left"];

/** Arch silhouette: semicircle top, soft square bottom (matches estate popout ref) */
const ARCH_CARD_RADIUS = "9999px 9999px 0.65rem 0.65rem";
const ARCH_PHOTO_RADIUS = "9999px 9999px 0.25rem 0.25rem";

function ExpandedCard({
  space,
  side,
  compact,
}: {
  space: VenueSpace;
  side: "left" | "right";
  compact?: boolean;
}) {
  return (
    <Link
      href={`${VENUE_PATH}#${space.slug}`}
      className={`group relative z-30 block ${
        compact
          ? "w-[12.5rem] sm:w-[14rem] lg:w-[15.5rem]"
          : "w-[15rem] sm:w-[17rem] lg:w-[19rem]"
      } ${
        side === "left"
          ? "animate-venue-expand-left"
          : "animate-venue-expand-right"
      }`}
      aria-label={`${space.name} — view on venue tour`}
    >
      <span
        className="relative block bg-[#faf8f3] px-2.5 pb-3.5 pt-2.5 shadow-[0_22px_48px_-14px_rgba(26,38,32,0.42)] transition duration-300 group-hover:-translate-y-0.5 group-hover:shadow-[0_28px_56px_-12px_rgba(26,38,32,0.46)] sm:px-3 sm:pb-4 sm:pt-3"
        style={{ borderRadius: ARCH_CARD_RADIUS }}
      >
        <span
          className={`relative mx-auto block w-full overflow-hidden ${
            compact ? "aspect-[3/3.7]" : "aspect-[3/4]"
          }`}
          style={{ borderRadius: ARCH_PHOTO_RADIUS }}
        >
          <Image
            src={space.image}
            alt=""
            fill
            quality={95}
            sizes="(max-width: 640px) 240px, 360px"
            className="object-cover transition duration-700 group-hover:scale-[1.03]"
            style={{
              objectPosition: objectPositionBySlug[space.slug] ?? "center",
            }}
          />
        </span>

        <span className="mt-2.5 flex flex-col items-center px-1 text-center sm:mt-3">
          <span
            className={`font-display leading-tight text-forest ${
              compact
                ? "text-[1.05rem] sm:text-[1.2rem]"
                : "text-[1.25rem] sm:text-[1.4rem] lg:text-[1.55rem]"
            }`}
          >
            {space.name}
          </span>
          <span
            aria-hidden
            className="mt-2 h-px w-8 bg-champagne/55 transition group-hover:w-11 group-hover:bg-champagne/75"
          />
        </span>
      </span>
    </Link>
  );
}

/** Soft gray translucent funnel: pin tip → photo on the popout card */
function LightFunnel({
  pin,
  slot,
}: {
  pin: MapPin;
  slot: MapPinSlot;
}) {
  const layout = SLOT_LAYOUT[slot];
  const pinX = pin.x;
  const pinY = pin.y;
  /** Aim at the arched photo (above the card’s title band) */
  const mouthY = layout.topPct - layout.mouthLift;
  const mouthHalf = 6.5;
  /** Extend past the map edge toward the off-map card */
  const edgeX = layout.side === "left" ? -5 : 105;
  const tipHalf = 0.55;
  const fillId = `funnel-fill-${slot}`;

  const tipTop = `${pinX},${pinY - tipHalf}`;
  const tipBot = `${pinX},${pinY + tipHalf}`;
  const edgeTop = `${edgeX},${mouthY - mouthHalf}`;
  const edgeBot = `${edgeX},${mouthY + mouthHalf}`;

  const points =
    layout.side === "left"
      ? `${tipTop} ${edgeTop} ${edgeBot} ${tipBot}`
      : `${tipTop} ${tipBot} ${edgeBot} ${edgeTop}`;

  return (
    <g>
      <defs>
        <linearGradient
          id={fillId}
          gradientUnits="userSpaceOnUse"
          x1={pinX}
          y1={pinY}
          x2={edgeX}
          y2={mouthY}
        >
          <stop offset="0%" stopColor="#5c6370" stopOpacity="0.36" />
          <stop offset="45%" stopColor="#8b929e" stopOpacity="0.18" />
          <stop offset="100%" stopColor="#c4c9d1" stopOpacity="0.06" />
        </linearGradient>
      </defs>
      <polygon points={points} fill={`url(#${fillId})`} />
    </g>
  );
}

export function VenueMapExplorer({ spaces }: { spaces: VenueSpace[] }) {
  const spaceBySlug = useMemo(() => {
    return new Map(spaces.map((s) => [s.slug, s]));
  }, [spaces]);

  const [slotSlug, setSlotSlug] = useState<Record<MapPinSlot, string>>({
    ...SLOT_DEFAULTS,
  });

  const selectPin = (pin: MapPin) => {
    setSlotSlug((prev) => ({ ...prev, [pin.slot]: pin.spaceSlug }));
  };

  return (
    <div className="mt-5 md:mt-6">
      <div className="relative mx-auto w-full max-w-xl lg:max-w-2xl">
        <div className="relative mx-[-4.5rem] px-[4.5rem] sm:mx-[-6.5rem] sm:px-[6.5rem] lg:mx-[-8rem] lg:px-[8rem]">
          <div className="relative overflow-visible">
            <Image
              src={MAP_IMAGE}
              alt="Illustrated map of the Hidden Acres grounds"
              width={MAP_IMAGE_WIDTH}
              height={MAP_IMAGE_HEIGHT}
              quality={95}
              className="pointer-events-none relative z-0 h-auto w-full max-h-none object-contain object-top shadow-[0_24px_50px_-28px_rgba(26,38,32,0.42)]"
              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 90vw, 1024px"
              priority
            />

            <svg
              className="pointer-events-none absolute inset-0 z-[15] h-full w-full overflow-visible"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              aria-hidden
            >
              {SLOT_ORDER.map((slot) => {
                const slug = slotSlug[slot];
                const pin = mapPins.find((p) => p.spaceSlug === slug);
                if (!pin) return null;
                return <LightFunnel key={slot} pin={pin} slot={slot} />;
              })}
            </svg>

            {/* Hit targets sit above funnels/cards; anchored at tip, extend up over pin body */}
            {mapPins.map((pin) => {
              const space = spaceBySlug.get(pin.spaceSlug);
              if (!space) return null;
              const isOpen = slotSlug[pin.slot] === pin.spaceSlug;

              return (
                <button
                  key={pin.spaceSlug}
                  type="button"
                  aria-label={`Preview ${space.name}`}
                  aria-pressed={isOpen}
                  onClick={(e) => {
                    e.stopPropagation();
                    selectPin(pin);
                    e.currentTarget.blur();
                  }}
                  className="absolute z-40 h-[4.25rem] w-14 -translate-x-1/2 -translate-y-[92%] cursor-pointer rounded-[999px] border-0 bg-transparent p-0 outline-none ring-0 focus:outline-none focus:ring-0 focus-visible:ring-2 focus-visible:ring-champagne/70 sm:h-[4.75rem] sm:w-16"
                  style={{ left: `${pin.x}%`, top: `${pin.y}%` }}
                />
              );
            })}

            {SLOT_ORDER.map((slot) => {
              const slug = slotSlug[slot];
              const space = spaceBySlug.get(slug);
              const layout = SLOT_LAYOUT[slot];
              if (!space) return null;

              return (
                <div
                  key={slot}
                  className="pointer-events-none absolute z-30 h-0 w-0"
                  style={{
                    top: `${layout.topPct}%`,
                    left: layout.side === "left" ? 0 : "auto",
                    right: layout.side === "right" ? 0 : "auto",
                  }}
                >
                  <div
                    className={`pointer-events-auto absolute top-0 -translate-y-1/2 ${
                      layout.side === "left"
                        ? "right-[-0.75rem] sm:right-[-0.5rem]"
                        : "left-[-0.75rem] sm:left-[-0.5rem]"
                    }`}
                  >
                    <ExpandedCard
                      key={space.slug}
                      space={space}
                      side={layout.side}
                      compact
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <p className="mt-5 text-center font-ui text-[10px] uppercase tracking-[0.18em] text-muted">
        Tap a map pin — each side keeps its spot while you switch spaces
      </p>
    </div>
  );
}
