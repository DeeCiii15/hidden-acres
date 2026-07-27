"use client";

import { weddingPage } from "@/lib/weddingData";

export function AmenitiesPdfDownload() {
  const handleDownload = async () => {
    const { jsPDF } = await import("jspdf");
    const doc = new jsPDF({ unit: "pt", format: "letter" });
    const margin = 54;
    const pageWidth = doc.internal.pageSize.getWidth();
    const maxWidth = pageWidth - margin * 2;
    let y = margin;

    doc.setFont("times", "bold");
    doc.setFontSize(18);
    doc.text("Hidden Acres — Amenities Included", margin, y);
    y += 28;

    doc.setFont("times", "normal");
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
      doc.setFont("times", "bold");
      doc.setFontSize(12);
      doc.setTextColor(44, 59, 50);
      doc.text(`•  ${item.title}`, margin, y);
      y += 16;
      doc.setFont("times", "normal");
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
    doc.setFont("times", "italic");
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
      className="font-ui inline-flex items-center justify-center border border-[#2c3b32]/30 px-5 py-3 text-[11px] uppercase tracking-[0.18em] text-[#2c3b32] transition hover:border-[#2c3b32]/55 hover:bg-[#2c3b32]/5"
    >
      Download amenities PDF
    </button>
  );
}
