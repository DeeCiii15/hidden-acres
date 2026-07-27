import Image from "next/image";

/** Official Hidden Acres mark from hiddenacresweddings.com. */
export const LOGO_SRC = "/brand/hidden-acres-logo.png";

type SiteLogoProps = {
  /** `light` = white (over hero); `dark` = black (cream / scrolled bar). */
  tone?: "light" | "dark";
  className?: string;
  priority?: boolean;
};

export function SiteLogo({
  tone = "light",
  className = "",
  priority = false,
}: SiteLogoProps) {
  // Force monochrome so tone always matches the wordmark color,
  // regardless of whether the source PNG is light or dark artwork.
  const toneClass =
    tone === "light" ? "brightness-0 invert" : "brightness-0";

  return (
    <Image
      key={tone}
      src={LOGO_SRC}
      alt=""
      width={280}
      height={200}
      priority={priority}
      className={`w-auto object-contain transition-[filter] duration-300 ${toneClass} ${className}`}
      aria-hidden
    />
  );
}
