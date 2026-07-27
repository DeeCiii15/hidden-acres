"use client";

import { useEffect, useRef } from "react";

type RevealProps = {
  children: React.ReactNode;
  className?: string;
  as?: "div" | "section" | "li" | "article";
};

export function Reveal({
  children,
  className = "",
  as = "div",
}: RevealProps) {
  const ref = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          node.classList.add("is-visible");
          observer.unobserve(node);
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const classes = `reveal ${className}`;

  if (as === "li") {
    return (
      <li ref={ref as React.RefObject<HTMLLIElement>} className={classes}>
        {children}
      </li>
    );
  }

  if (as === "section") {
    return (
      <section ref={ref as React.RefObject<HTMLElement>} className={classes}>
        {children}
      </section>
    );
  }

  if (as === "article") {
    return (
      <article ref={ref as React.RefObject<HTMLElement>} className={classes}>
        {children}
      </article>
    );
  }

  return (
    <div ref={ref as React.RefObject<HTMLDivElement>} className={classes}>
      {children}
    </div>
  );
}
