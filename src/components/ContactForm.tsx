"use client";

import { useState } from "react";
import { CONTACT } from "@/lib/siteConfig";

export function ContactForm() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="rounded-sm border border-stroke bg-mist/60 p-8">
        <p className="font-display text-2xl text-forest">Thank you</p>
        <p className="mt-3 text-muted">
          We received your inquiry. For the fastest reply, you can also email{" "}
          <a
            className="text-champagne underline-offset-2 hover:underline"
            href={`mailto:${CONTACT.email}`}
          >
            {CONTACT.email}
          </a>
          .
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="grid gap-5 sm:grid-cols-2">
        <label className="block text-sm text-muted">
          Your name
          <input
            required
            name="name"
            className="mt-2 w-full rounded-sm border border-stroke bg-cream px-4 py-3 text-forest outline-none transition focus:border-champagne"
          />
        </label>
        <label className="block text-sm text-muted">
          Email
          <input
            required
            type="email"
            name="email"
            className="mt-2 w-full rounded-sm border border-stroke bg-cream px-4 py-3 text-forest outline-none transition focus:border-champagne"
          />
        </label>
      </div>
      <div className="grid gap-5 sm:grid-cols-2">
        <label className="block text-sm text-muted">
          Phone
          <input
            name="phone"
            type="tel"
            className="mt-2 w-full rounded-sm border border-stroke bg-cream px-4 py-3 text-forest outline-none transition focus:border-champagne"
          />
        </label>
        <label className="block text-sm text-muted">
          Preferred wedding date
          <input
            name="date"
            type="text"
            placeholder="Month / year"
            className="mt-2 w-full rounded-sm border border-stroke bg-cream px-4 py-3 text-forest outline-none transition focus:border-champagne"
          />
        </label>
      </div>
      <label className="block text-sm text-muted">
        Guest count (approx.)
        <input
          name="guests"
          type="text"
          className="mt-2 w-full rounded-sm border border-stroke bg-cream px-4 py-3 text-forest outline-none transition focus:border-champagne"
        />
      </label>
      <label className="block text-sm text-muted">
        Tell us about your weekend
        <textarea
          required
          name="message"
          rows={5}
          className="mt-2 w-full rounded-sm border border-stroke bg-cream px-4 py-3 text-forest outline-none transition focus:border-champagne"
        />
      </label>
      <button
        type="submit"
        className="font-ui inline-flex items-center justify-center bg-[#2c3b32] px-5 py-3 text-xs font-medium uppercase tracking-[0.16em] text-white transition hover:bg-[#1a2620] md:px-6 md:py-3.5 md:text-sm"
      >
        Send inquiry
      </button>
      <p className="text-xs text-muted">
        This demo form collects your details on-page only. Connect it to your
        email or CRM before launch.
      </p>
    </form>
  );
}
