type FaqItem = {
  question: string;
  answer: string;
};

export function FaqAccordion({
  items,
  heading = "Frequently asked questions",
}: {
  items: FaqItem[];
  heading?: string;
}) {
  if (!items.length) return null;

  return (
    <section className="mx-auto max-w-3xl px-5 py-20 md:px-8">
      <h2 className="font-display text-3xl text-forest md:text-4xl">{heading}</h2>
      <div className="mt-8 divide-y divide-stroke border-y border-stroke">
        {items.map((item) => (
          <details key={item.question} className="group py-5">
            <summary className="cursor-pointer list-none text-left text-lg text-forest outline-none marker:content-none [&::-webkit-details-marker]:hidden">
              <span className="flex items-start justify-between gap-4">
                <span>{item.question}</span>
                <span
                  className="mt-1 text-champagne transition group-open:rotate-45"
                  aria-hidden
                >
                  +
                </span>
              </span>
            </summary>
            <p className="mt-3 max-w-2xl text-base leading-relaxed text-muted">
              {item.answer}
            </p>
          </details>
        ))}
      </div>
    </section>
  );
}
