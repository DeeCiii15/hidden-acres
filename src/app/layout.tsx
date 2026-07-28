import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import {
  Bodoni_Moda,
  Cormorant_Garamond,
  Italianno,
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

/** Site UI / body / display — all non-script type (default weight 600). */
const cormorant = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

/** Print / PDF serif — classic Bodoni via Google’s Bodoni Moda. */
const bodoni = Bodoni_Moda({
  variable: "--font-bodoni",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
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
      className={`${italianno.variable} ${cormorant.variable} ${bodoni.variable}`}
    >
      <body className="site-shell antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <FloatingContactBar />
        <Analytics />
      </body>
    </html>
  );
}
