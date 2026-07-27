"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { SiteLogo } from "@/components/SiteLogo";
import {
  ABOUT_PATH,
  CONTACT_PATH,
  PORTFOLIO_PATH,
  VENUE_PATH,
  WEDDING_PATH,
} from "@/lib/siteConfig";

const navLinks = [
  { href: VENUE_PATH, label: "Venue" },
  { href: WEDDING_PATH, label: "Wedding" },
  { href: PORTFOLIO_PATH, label: "Portfolio" },
  { href: ABOUT_PATH, label: "About" },
];

function heroIsInView(): boolean {
  const hero = document.getElementById("hero-surface");
  if (!hero) return false;
  const rect = hero.getBoundingClientRect();
  return rect.bottom > 72 && rect.top < window.innerHeight * 0.55;
}

function pathHasDarkHero(pathname: string) {
  return (
    pathname === "/" ||
    pathname === VENUE_PATH ||
    pathname === WEDDING_PATH ||
    pathname === "/marion-sc-wedding-venue"
  );
}

export function Header() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  // Match SSR to dark-hero routes so we never flash a cream bar + hairline on load.
  const [overHero, setOverHero] = useState(() => pathHasDarkHero(pathname));

  useEffect(() => {
    const sync = () => {
      setScrolled(window.scrollY > 24);
      setOverHero(heroIsInView());
    };
    sync();
    window.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    return () => {
      window.removeEventListener("scroll", sync);
      window.removeEventListener("resize", sync);
    };
  }, [pathname]);

  useEffect(() => {
    setOpen(false);
    // Re-check after route paint
    const id = window.requestAnimationFrame(() => setOverHero(heroIsInView()));
    return () => window.cancelAnimationFrame(id);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  // Stay transparent over the hero for the full hero height — only solidify
  // once the dark surface has scrolled away (avoids a cream strip + hard line).
  // Opening the mobile menu always uses the cream scrolled chrome (bar + panel).
  const onDarkHero = overHero && !open;
  const solidBar = open || ((scrolled || !overHero) && !onDarkHero);

  return (
    <header className="fixed inset-x-0 top-0 z-50 overflow-visible">
      <div
        className={`overflow-visible transition-[background-color,box-shadow,backdrop-filter] duration-300 ${
          onDarkHero
            ? "bg-transparent"
            : solidBar
              ? "bg-[#f3f0e8]"
              : "bg-transparent"
        }`}
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-2 overflow-visible px-4 sm:h-[4.5rem] sm:gap-3 sm:px-5 md:h-20 md:px-8">
          <Link
            href="/"
            className="inline-flex min-w-0 shrink items-center gap-1 overflow-visible sm:gap-2.5 md:gap-3"
            onClick={() => setOpen(false)}
          >
            <SiteLogo
              tone={onDarkHero ? "light" : "dark"}
              priority
              className="h-14 w-auto shrink-0 scale-[1.42] contrast-150 drop-shadow-[0_1px_3px_rgba(0,0,0,0.45)] sm:h-[4.25rem] sm:scale-[1.38] md:h-[4.75rem] md:scale-[1.45]"
            />
            <span
              className={`font-script truncate text-[1.8rem] leading-none transition-colors duration-300 sm:text-[2.15rem] md:text-[2.55rem] ${
                onDarkHero
                  ? "text-white [text-shadow:0_1px_18px_rgba(0,0,0,0.35)]"
                  : "text-[#2c3b32]"
              }`}
            >
              Hidden Acres
            </span>
          </Link>

          <nav className="hidden items-center gap-0.5 lg:flex">
            {navLinks.map((link) => {
              const active =
                pathname === link.href || pathname.startsWith(`${link.href}/`);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`font-ui px-3 py-2 text-[11px] uppercase tracking-[0.18em] transition-colors duration-300 ${
                    onDarkHero
                      ? active
                        ? "text-white [text-shadow:0_1px_12px_rgba(0,0,0,0.3)]"
                        : "text-white/85 hover:text-white [text-shadow:0_1px_12px_rgba(0,0,0,0.3)]"
                      : active
                        ? "text-[#2c3b32]"
                        : "text-[#3f4d44] hover:text-[#2c3b32]"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
            <Link
              href={CONTACT_PATH}
              className={`font-ui ml-3 px-4 py-2 text-[11px] uppercase tracking-[0.18em] transition duration-300 ${
                onDarkHero
                  ? "border border-white/70 text-white hover:bg-white/10 [text-shadow:0_1px_10px_rgba(0,0,0,0.25)]"
                  : "bg-[#2c3b32] text-white hover:bg-[#1a2620]"
              }`}
            >
              Contact
            </Link>
          </nav>

          <button
            type="button"
            className={`inline-flex h-10 w-10 shrink-0 items-center justify-center lg:hidden ${
              onDarkHero ? "text-white" : "text-[#2c3b32]"
            }`}
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            <span className="sr-only">Menu</span>
            <span className="flex flex-col gap-1.5" aria-hidden>
              <span
                className={`block h-px w-5 bg-current transition ${open ? "translate-y-[3.5px] rotate-45" : ""}`}
              />
              <span
                className={`block h-px w-5 bg-current transition ${open ? "opacity-0" : ""}`}
              />
              <span
                className={`block h-px w-5 bg-current transition ${open ? "-translate-y-[3.5px] -rotate-45" : ""}`}
              />
            </span>
          </button>
        </div>
      </div>

      <div
        className={`border-b border-[#2c3b32]/10 bg-[#f3f0e8] lg:hidden ${
          open ? "block" : "hidden"
        }`}
      >
        <div className="flex flex-col px-5 py-4">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="font-ui border-b border-[#2c3b32]/10 py-3.5 text-xs uppercase tracking-[0.18em] text-[#2c3b32]"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <Link
            href={CONTACT_PATH}
            className="font-ui mt-4 inline-flex items-center justify-center bg-[#2c3b32] px-4 py-3 text-xs uppercase tracking-[0.18em] text-white"
            onClick={() => setOpen(false)}
          >
            Contact
          </Link>
        </div>
      </div>
    </header>
  );
}
