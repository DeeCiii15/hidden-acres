"use client";

import { weddingPage } from "@/lib/weddingData";

const PRINT_FONT = "BodoniModa";

/** Google Fonts TTF faces (Bodoni Moda) for jsPDF embedding at download time. */
const BODONI_FACES = [
  {
    file: "BodoniModa-Regular.ttf",
    style: "normal" as const,
    url: "https://fonts.gstatic.com/s/bodonimoda/v28/aFT67PxzY382XsXX63LUYL6GYFcan6NJrKp-VPjfJMShrpsGFUt8oU7a8Id4sQ.ttf",
  },
  {
    file: "BodoniModa-Bold.ttf",
    style: "bold" as const,
    url: "https://fonts.gstatic.com/s/bodonimoda/v28/aFT67PxzY382XsXX63LUYL6GYFcan6NJrKp-VPjfJMShrpsGFUt8oand8Id4sQ.ttf",
  },
  {
    file: "BodoniModa-Italic.ttf",
    style: "italic" as const,
    url: "https://fonts.gstatic.com/s/bodonimoda/v28/aFT07PxzY382XsXX63LUYJSPUqb0pL6OQqxrZLnVbvZedvJtj-V7tIaZKMNItnDN.ttf",
  },
];

async function arrayBufferToBase64(buffer: ArrayBuffer) {
  const bytes = new Uint8Array(buffer);
  const chunk = 0x8000;
  let binary = "";
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

async function registerBodoniFont(doc: {
  addFileToVFS: (filename: string, data: string) => void;
  addFont: (filename: string, fontName: string, style: string) => void;
}) {
  await Promise.all(
    BODONI_FACES.map(async (face) => {
      const res = await fetch(face.url);
      if (!res.ok) {
        throw new Error(`Failed to load print font (${face.style})`);
      }
      const base64 = await arrayBufferToBase64(await res.arrayBuffer());
      doc.addFileToVFS(face.file, base64);
      doc.addFont(face.file, PRINT_FONT, face.style);
    }),
  );
}

export function AmenitiesPdfDownload() {
  const handleDownload = async () => {
    const { jsPDF } = await import("jspdf");
    const doc = new jsPDF({ unit: "pt", format: "letter" });
    await registerBodoniFont(doc);

    const margin = 54;
    const pageWidth = doc.internal.pageSize.getWidth();
    const maxWidth = pageWidth - margin * 2;
    let y = margin;

    doc.setFont(PRINT_FONT, "bold");
    doc.setFontSize(18);
    doc.text("Hidden Acres — Amenities Included", margin, y);
    y += 28;

    doc.setFont(PRINT_FONT, "normal");
    doc.setFontSize(11);
    doc.setTextColor(60, 60, 55);
    const intro = doc.splitTextToSize(
      "The following amenities are included with your venue rental. Package pricing is shared when you tour.",
      maxWidth,
    );
    doc.text(intro, margin, y);
    y += intro.length * 14 + 18;

    weddingPage.included.forEach((item) => {
      if (y > 700) {
        doc.addPage();
        y = margin;
      }
      doc.setFont(PRINT_FONT, "bold");
      doc.setFontSize(12);
      doc.setTextColor(44, 59, 50);
      doc.text(`•  ${item.title}`, margin, y);
      y += 16;
      doc.setFont(PRINT_FONT, "normal");
      doc.setFontSize(11);
      doc.setTextColor(50, 55, 50);
      const lines = doc.splitTextToSize(item.detail, maxWidth - 14);
      doc.text(lines, margin + 14, y);
      y += lines.length * 14 + 14;
    });

    y += 8;
    if (y > 720) {
      doc.addPage();
      y = margin;
    }
    doc.setFont(PRINT_FONT, "italic");
    doc.setFontSize(10);
    doc.setTextColor(90, 90, 85);
    doc.text(
      "6701 Ella Grace Court, Marion, SC 29571  ·  (843) 430-0332",
      margin,
      y,
    );

    doc.save("hidden-acres-amenities-included.pdf");
  };

  return (
    <button
      type="button"
      onClick={handleDownload}
      className="font-ui inline-flex items-center justify-center border border-[#2c3b32]/30 px-3.5 py-2.5 text-[11px] uppercase tracking-[0.14em] text-[#2c3b32] transition hover:border-[#2c3b32]/55 hover:bg-[#2c3b32]/5 md:px-5 md:py-3.5 md:text-sm md:tracking-[0.16em]"
    >
      Download amenities PDF
    </button>
  );
}
