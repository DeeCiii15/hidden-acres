"use client";

import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import Image from "next/image";
import { REVIEWS, REVIEWS_CAPTION } from "@/lib/siteConfig";
import { type Testimonial } from "@/lib/testimonials";
import { Reveal } from "./Reveal";

const REVIEW_LINKS = [
  {
    ...REVIEWS.theKnot,
    className: "h-8 w-[7.5rem] sm:h-9 sm:w-[8.75rem]",
    imgClassName: "h-full w-full object-contain object-center",
    width: 140,
    height: 40,
  },
  {
    ...REVIEWS.google,
    className: "h-8 w-[10rem] sm:h-9 sm:w-[11.5rem]",
    imgClassName: "h-full w-full object-contain object-center",
    width: 180,
    height: 40,
  },
  {
    ...REVIEWS.bestOfPeeDee,
    className: "h-14 w-14 sm:h-16 sm:w-16",
    imgClassName: "h-full w-full rounded-full object-cover object-center shadow-[0_4px_14px_-6px_rgba(26,38,32,0.35)]",
    width: 64,
    height: 64,
  },
] as const;

function BotanicalCorner({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 120 120"
      className={className}
      fill="none"
      aria-hidden
    >
      <path
        d="M18 102c22-6 38-22 46-42 6 16 18 28 38 34"
        stroke="currentColor"
        strokeWidth="1.1"
        strokeLinecap="round"
      />
      <path
        d="M42 78c8-14 10-28 8-42M64 86c10-12 22-18 36-20"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
      />
      <path
        d="M48 58c-6-2-10-8-11-14 8 1 14 6 16 14ZM72 70c-1-7 2-14 8-18-2 8-1 14-8 18Z"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M28 94c4-8 4-14 1-20M88 78c6-4 12-4 18-1"
        stroke="currentColor"
        strokeWidth="0.9"
        strokeLinecap="round"
        opacity="0.7"
      />
    </svg>
  );
}

function BotanicalSprig({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 80 28"
      className={className}
      fill="none"
      aria-hidden
    >
      <path
        d="M4 18c12-2 22-8 28-16 4 10 14 16 28 18"
        stroke="currentColor"
        strokeWidth="1.1"
        strokeLinecap="round"
      />
      <path
        d="M22 12c-4-1-7-4-8-8 5 1 9 4 10 8ZM48 16c0-5 2-9 6-12-1 5 0 9-6 12Z"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function WaxSeal({ className = "" }: { className?: string }) {
  return (
    <span
      aria-hidden
      className={`love-letter-seal relative inline-flex h-8 w-8 items-center justify-center rounded-full bg-sage shadow-[0_2px_6px_-2px_rgba(44,59,50,0.35)] ring-1 ring-forest/10 ${className}`}
    >
      <svg viewBox="0 0 24 24" className="h-3.5 w-3.5 text-cream/90" fill="none">
        <path
          d="M12 5c1.5 3 1.5 6 0 9-1.5-3-1.5-6 0-9Z"
          stroke="currentColor"
          strokeWidth="1.2"
          strokeLinejoin="round"
        />
        <path
          d="M8.5 9.5c2 .8 4.5.8 7 0M9 13c1.8.6 4.2.6 6 0"
          stroke="currentColor"
          strokeWidth="1.1"
          strokeLinecap="round"
        />
        <circle
          cx="12"
          cy="12"
          r="9.25"
          stroke="currentColor"
          strokeWidth="0.75"
          opacity="0.45"
        />
      </svg>
    </span>
  );
}

function LetterExpandModal({
  item,
  onClose,
}: {
  item: Testimonial;
  onClose: () => void;
}) {
  const titleId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key !== "Tab" || !dialogRef.current) return;

      const focusable = [
        ...dialogRef.current.querySelectorAll<HTMLElement>(
          'button, [href], textarea, input, select, [tabindex]:not([tabindex="-1"])',
        ),
      ].filter((el) => !el.hasAttribute("disabled") && el.tabIndex !== -1);

      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
      previous?.focus?.();
    };
  }, [onClose]);

  return (
    <div
      className="love-letter-modal-backdrop"
      role="presentation"
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="love-letter-modal"
        onClick={(event) => event.stopPropagation()}
      >
        <BotanicalCorner className="pointer-events-none absolute bottom-3 left-3 h-16 w-16 text-bark/14" />
        <BotanicalCorner className="pointer-events-none absolute right-3 top-4 h-12 w-12 rotate-180 text-bark/10" />

        <button
          ref={closeRef}
          type="button"
          className="love-letter-modal-close"
          aria-label="Close full letter"
          onClick={onClose}
        >
          ×
        </button>

        <p className="eyebrow text-champagne">A kept letter</p>
        <h3 id={titleId} className="love-letter-modal-title font-display italic text-forest">
          {item.name}
        </h3>
        <blockquote className="love-letter-modal-quote font-body italic text-forest">
          “{item.quote}”
        </blockquote>
      </div>
    </div>
  );
}

function LetterFromEnvelope({
  item,
  isActive,
  isUnveiled,
  onSelect,
  onExpand,
}: {
  item: Testimonial;
  isActive: boolean;
  isUnveiled: boolean;
  onSelect: () => void;
  onExpand: () => void;
}) {
  const quoteRef = useRef<HTMLParagraphElement>(null);
  const [isTruncated, setIsTruncated] = useState(false);

  useEffect(() => {
    const el = quoteRef.current;
    if (!el) return;

    const measure = () => {
      setIsTruncated(el.scrollHeight > el.clientHeight + 1);
    };

    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [item.quote, isUnveiled, isActive]);

  return (
    <article
      aria-current={isActive ? "true" : undefined}
      onClick={onSelect}
      className={`love-letter-unit relative mx-auto cursor-pointer ${
        isActive ? "is-active" : ""
      } ${isActive && !isUnveiled ? "love-letter-float" : ""} ${
        isUnveiled ? "is-unveiled" : ""
      }`}
    >
      <div className="love-letter-envelope">
        <div aria-hidden className="love-letter-flap-open">
          <div className="love-letter-flap-open-face" />
        </div>

        <div aria-hidden className="love-letter-back" />
        <div aria-hidden className="love-letter-lining" />

        <blockquote className="love-letter-sheet">
          <BotanicalCorner className="pointer-events-none absolute bottom-2 left-1.5 h-12 w-12 text-bark/16 md:h-14 md:w-14" />
          <BotanicalCorner className="pointer-events-none absolute right-1.5 top-3 h-10 w-10 rotate-180 text-bark/10" />

          <p
            ref={quoteRef}
            className="love-letter-quote relative font-body text-[0.86rem] italic leading-[1.6] text-forest sm:text-[0.92rem] sm:leading-[1.65] md:text-[0.96rem]"
          >
            “{item.quote}”
          </p>

          {isUnveiled && isTruncated && (
            <button
              type="button"
              className="love-letter-expand"
              aria-label={`Read full letter from ${item.name}`}
              onClick={(event) => {
                event.stopPropagation();
                onExpand();
              }}
            >
              <span aria-hidden>↓</span>
            </button>
          )}
        </blockquote>

        <div aria-hidden className="love-letter-pocket">
          <div className="love-letter-pocket-face">
            <div className="love-letter-pocket-folds" />
            <p className="love-letter-pocket-name font-display italic text-forest">
              {item.name}
            </p>
            <BotanicalCorner className="love-letter-pocket-botanical text-sage/55" />
            <span className="absolute left-1/2 top-[52%] flex -translate-x-1/2 -translate-y-1/2 justify-center">
              <WaxSeal />
            </span>
          </div>
        </div>
      </div>
    </article>
  );
}

export function Testimonials({
  items,
  heading = "Love letters from our couples",
}: {
  items: Testimonial[];
  heading?: string;
}) {
  const sectionRef = useRef<HTMLElement>(null);
  const scrollerRef = useRef<HTMLUListElement>(null);
  const wrappingRef = useRef(false);
  const count = items.length;
  const canLoop = count > 1;
  const loopItems = useMemo(
    () => (canLoop ? [...items, ...items, ...items] : items),
    [items, canLoop],
  );
  const middleStart = canLoop ? count : 0;
  const initialLogical = Math.floor((Math.max(count, 1) - 1) / 2);
  const initialDomIndex = middleStart + initialLogical;

  const [active, setActive] = useState(initialLogical);
  const [activeDom, setActiveDom] = useState(initialDomIndex);
  const [sectionInView, setSectionInView] = useState(false);
  const [expanded, setExpanded] = useState<Testimonial | null>(null);

  const scrollToIndex = useCallback(
    (index: number, behavior: ScrollBehavior = "smooth") => {
      const el = scrollerRef.current;
      if (!el) return;
      const card = el.querySelectorAll("li")[index] as HTMLElement | undefined;
      if (!card) return;
      const left = card.offsetLeft - (el.clientWidth - card.offsetWidth) / 2;
      el.scrollTo({ left: Math.max(0, left), behavior });
    },
    [],
  );

  const logicalFromDom = useCallback(
    (domIndex: number) => {
      if (!canLoop || count === 0) return domIndex;
      return ((domIndex % count) + count) % count;
    },
    [canLoop, count],
  );

  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) setSectionInView(true);
      },
      { threshold: 0.28, rootMargin: "0px 0px -8% 0px" },
    );
    io.observe(section);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;

    const sync = () => {
      if (wrappingRef.current) return;

      const cards = [...el.querySelectorAll("li")];
      if (!cards.length) return;

      const mid = el.scrollLeft + el.clientWidth * 0.5;
      let best = 0;
      let bestDist = Infinity;
      cards.forEach((card, i) => {
        const dist = Math.abs(card.offsetLeft + card.offsetWidth * 0.5 - mid);
        if (dist < bestDist) {
          bestDist = dist;
          best = i;
        }
      });

      const logical = logicalFromDom(best);
      setActive(logical);

      if (!canLoop) {
        setActiveDom(best);
        return;
      }

      // Keep scroll in the middle copy so either direction always has cards
      if (best < count) {
        const target = best + count;
        wrappingRef.current = true;
        setActiveDom(target);
        scrollToIndex(target, "instant");
        requestAnimationFrame(() => {
          wrappingRef.current = false;
        });
      } else if (best >= count * 2) {
        const target = best - count;
        wrappingRef.current = true;
        setActiveDom(target);
        scrollToIndex(target, "instant");
        requestAnimationFrame(() => {
          wrappingRef.current = false;
        });
      } else {
        setActiveDom(best);
      }
    };

    scrollToIndex(initialDomIndex, "instant");
    sync();
    el.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    return () => {
      el.removeEventListener("scroll", sync);
      window.removeEventListener("resize", sync);
    };
  }, [
    canLoop,
    count,
    initialDomIndex,
    logicalFromDom,
    scrollToIndex,
  ]);

  const scrollByCards = (dir: -1 | 1) => {
    const el = scrollerRef.current;
    if (!el) return;
    const card = el.querySelector("li");
    const step = card
      ? card.getBoundingClientRect().width + 16
      : el.clientWidth * 0.7;
    el.scrollBy({ left: dir * step, behavior: "smooth" });
  };

  const goTo = (logicalIndex: number) => {
    scrollToIndex(middleStart + logicalIndex, "smooth");
  };

  if (!items.length) return null;

  const navBtnClass =
    "font-ui absolute top-[78%] z-20 inline-flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-sm border border-forest/20 bg-cream/90 text-forest shadow-[0_8px_20px_-12px_rgba(26,38,32,0.45)] backdrop-blur-sm transition enabled:hover:border-sage enabled:hover:bg-sage enabled:hover:text-cream disabled:opacity-30 md:top-[80%] md:h-10 md:w-10";

  return (
    <section
      ref={sectionRef}
      id="love-letters"
      className={`love-letters relative overflow-hidden py-20 md:py-28 ${
        sectionInView ? "is-in-view" : ""
      }`}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background: `
            radial-gradient(900px 420px at 12% 8%, color-mix(in oklab, var(--sage-soft) 28%, transparent), transparent 60%),
            radial-gradient(700px 380px at 92% 18%, color-mix(in oklab, var(--champagne-soft) 22%, transparent), transparent 55%),
            linear-gradient(180deg, var(--mist) 0%, var(--linen) 42%, var(--paper-deep) 100%)
          `,
        }}
      />
      <div
        aria-hidden
        className="love-letters-linen pointer-events-none absolute inset-0 opacity-[0.35]"
      />

      <BotanicalCorner className="pointer-events-none absolute -left-2 bottom-8 h-36 w-36 text-bark/15 md:bottom-12 md:h-48 md:w-48" />
      <BotanicalCorner className="pointer-events-none absolute -right-2 top-16 h-32 w-32 rotate-180 text-bark/12 md:top-20 md:h-44 md:w-44" />

      <div className="relative mx-auto max-w-6xl px-5 md:px-8">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="eyebrow text-champagne">Kept with care</p>
          <div className="mt-2 flex items-center justify-center gap-3 text-sage sm:gap-4">
            <BotanicalSprig className="hidden h-6 w-16 shrink-0 sm:block" />
            <h2 className="whitespace-nowrap font-script text-3xl text-forest md:text-4xl lg:text-5xl">
              {heading}
            </h2>
            <BotanicalSprig className="hidden h-6 w-16 shrink-0 scale-x-[-1] sm:block" />
          </div>
          <p className="mx-auto mt-2 mb-0 whitespace-nowrap text-[clamp(0.625rem,2.7vw,0.875rem)] leading-none tracking-tight text-muted">
            Words pressed like stationery — from weekends on the grounds.
          </p>
        </Reveal>

        <div className="relative mt-1 md:mt-2">
          <div className="relative">
            <button
              type="button"
              aria-label="Previous letter"
              disabled={!canLoop}
              onClick={() => scrollByCards(-1)}
              className={`${navBtnClass} left-0 sm:left-1 md:-left-1 lg:-left-2`}
            >
              ←
            </button>
            <button
              type="button"
              aria-label="Next letter"
              disabled={!canLoop}
              onClick={() => scrollByCards(1)}
              className={`${navBtnClass} right-0 sm:right-1 md:-right-1 lg:-right-2`}
            >
              →
            </button>

            <ul
              ref={scrollerRef}
              className="no-scrollbar flex snap-x snap-mandatory gap-4 overflow-x-auto px-[max(2.25rem,calc(50%-7.75rem))] pb-2 pt-[8.5rem] md:gap-5 md:px-[max(2.75rem,calc(50%-8.75rem))] md:pb-4 md:pt-36"
            >
              {loopItems.map((item, index) => {
                const logical = logicalFromDom(index);
                return (
                  <li
                    key={`${item.name}-${index}`}
                    className="w-[min(68vw,15.5rem)] shrink-0 snap-center md:w-[17.5rem]"
                  >
                    <LetterFromEnvelope
                      item={item}
                      isActive={index === activeDom}
                      isUnveiled={sectionInView && index === activeDom}
                      onSelect={() => goTo(logical)}
                      onExpand={() => setExpanded(item)}
                    />
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="mt-3 flex flex-col items-center gap-3 md:mt-5 md:gap-4">
            <p className="font-ui text-center text-[11px] uppercase tracking-[0.18em] text-muted">
              {String(active + 1).padStart(2, "0")} /{" "}
              {String(items.length).padStart(2, "0")}
            </p>
            <div className="flex justify-center gap-2">
              {items.map((item, index) => (
                <button
                  key={`dot-${item.name}-${index}`}
                  type="button"
                  aria-label={`Show letter from ${item.name}`}
                  aria-current={index === active ? "true" : undefined}
                  onClick={() => goTo(index)}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    index === active
                      ? "w-7 bg-sage"
                      : "w-1.5 bg-forest/20 hover:bg-forest/35"
                  }`}
                />
              ))}
            </div>

            <nav
              aria-label="Reviews and awards"
              className="mt-4 flex w-full max-w-lg flex-col items-center gap-4 border-t border-forest/10 pt-6 sm:mt-5 sm:gap-5 md:mt-6 md:gap-5 md:pt-7"
            >
              <div className="flex w-full flex-wrap items-center justify-center gap-x-8 gap-y-5 sm:gap-x-10 md:gap-x-12">
                {REVIEW_LINKS.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`${REVIEWS_CAPTION} — ${link.label}`}
                    className={`inline-flex items-center justify-center opacity-[0.88] transition hover:opacity-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-sage ${link.className}`}
                  >
                    <Image
                      src={link.logo}
                      alt=""
                      width={link.width}
                      height={link.height}
                      className={link.imgClassName}
                      unoptimized
                    />
                  </a>
                ))}
              </div>
              <p className="max-w-sm text-center font-body text-sm italic leading-snug text-muted md:text-[0.9375rem]">
                {REVIEWS_CAPTION}
              </p>
            </nav>
          </div>
        </div>
      </div>

      {expanded && (
        <LetterExpandModal
          item={expanded}
          onClose={() => setExpanded(null)}
        />
      )}
    </section>
  );
}
