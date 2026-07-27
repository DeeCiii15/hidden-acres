import Link from "next/link";

type ButtonProps = {
  href: string;
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost" | "onDark";
  className?: string;
};

const variants = {
  primary: "bg-[#2c3b32] text-white hover:bg-[#1a2620]",
  secondary:
    "bg-transparent text-[#2c3b32] border border-[#2c3b32]/30 hover:border-[#2c3b32]/55 hover:bg-[#2c3b32]/5",
  ghost:
    "bg-transparent text-white border border-white/60 hover:bg-white/10",
  onDark: "bg-white text-[#2c3b32] hover:bg-[#faf8f3]",
};

export function Button({
  href,
  children,
  variant = "primary",
  className = "",
}: ButtonProps) {
  return (
    <Link
      href={href}
      className={`font-ui inline-flex items-center justify-center gap-2 px-4 py-2.5 text-[11px] font-medium uppercase tracking-[0.14em] transition duration-300 md:px-6 md:py-3.5 md:text-sm md:tracking-[0.16em] ${variants[variant]} ${className}`}
    >
      {children}
    </Link>
  );
}
