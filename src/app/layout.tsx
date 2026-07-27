import type { Metadata } from "next";
import {
  Cormorant_Garamond,
  Italianno,
  Josefin_Sans,
  Lora,
} from "next/font/google";
import { FloatingContactBar } from "@/components/FloatingContactBar";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import {
  getSiteUrl,
  HOME_DESCRIPTION,
  HOME_TITLE,
  SITE_NAME,
} from "@/lib/siteConfig";
import "./globals.css";

/** Brand script — primary expressive voice (nav wordmark + major titles). */
const italianno = Italianno({
  variable: "--font-italianno",
  weight: "400",
  subsets: ["latin"],
  display: "swap",
});

/** Elegant companion for longer headings that need more structure. */
const cormorant = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

/** Warm readable body serif that sits with the script. */
const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  display: "swap",
});

/** Light, refined sans for nav, buttons, and labels. */
const josefin = Josefin_Sans({
  variable: "--font-josefin",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: {
    default: HOME_TITLE,
    template: `%s | ${SITE_NAME}`,
  },
  description: HOME_DESCRIPTION,
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    siteName: SITE_NAME,
    title: HOME_TITLE,
    description: HOME_DESCRIPTION,
    url: "/",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${italianno.variable} ${cormorant.variable} ${lora.variable} ${josefin.variable}`}
    >
      <body className="site-shell antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <FloatingContactBar />
      </body>
    </html>
  );
}
