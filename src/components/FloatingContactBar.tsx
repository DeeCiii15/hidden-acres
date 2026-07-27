import { CONTACT, SOCIAL } from "@/lib/siteConfig";

function PhoneIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      className={className}
      aria-hidden
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106a1.125 1.125 0 0 0-1.173.417l-.97 1.293a1.125 1.125 0 0 1-1.21.38 12.035 12.035 0 0 1-7.143-7.143 1.125 1.125 0 0 1 .38-1.21l1.293-.97c.363-.275.565-.724.417-1.173L6.963 3.102a1.125 1.125 0 0 0-1.091-.852H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25z"
      />
    </svg>
  );
}

function EmailIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      className={className}
      aria-hidden
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"
      />
    </svg>
  );
}

function FacebookIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden
    >
      <path d="M22 12.07C22 6.48 17.52 2 11.93 2S1.86 6.48 1.86 12.07c0 5.02 3.66 9.18 8.44 9.93v-7.03H7.9v-2.9h2.4V9.86c0-2.37 1.4-3.68 3.56-3.68 1.03 0 2.12.18 2.12.18v2.34h-1.2c-1.18 0-1.55.74-1.55 1.5v1.8h2.64l-.42 2.9h-2.22V22c4.78-.75 8.44-4.91 8.44-9.93z" />
    </svg>
  );
}

function InstagramIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden
    >
      <path d="M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2m-.2 2A3.6 3.6 0 0 0 4 7.6v8.8C4 18.39 5.61 20 7.6 20h8.8a3.6 3.6 0 0 0 3.6-3.6V7.6C20 5.61 18.39 4 16.4 4H7.6m9.65 1.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5M12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10m0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6z" />
    </svg>
  );
}

export function FloatingContactBar() {
  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-3 z-50 flex justify-center px-3 md:inset-x-auto md:right-[max(1.5rem,calc(env(safe-area-inset-right,0px)+1.25rem))] md:bottom-5 md:justify-end md:px-0">
      <div className="pointer-events-auto flex max-w-full items-center gap-2.5 rounded-full border border-cream/15 bg-forest-deep/95 px-3.5 py-2 text-cream shadow-[0_18px_40px_-18px_rgba(18,28,23,0.75)] backdrop-blur-md md:gap-3 md:px-4 md:py-2.5">
        <a
          href={CONTACT.phoneHref}
          className="font-ui inline-flex items-center gap-2 text-[11px] tracking-[0.04em] text-cream/90 transition hover:text-cream"
          aria-label={`Call ${CONTACT.phoneDisplay}`}
        >
          <PhoneIcon className="h-3.5 w-3.5 shrink-0" />
          <span>{CONTACT.phoneDisplay}</span>
        </a>

        <span className="h-4 w-px bg-cream/25" aria-hidden />

        <a
          href={`mailto:${CONTACT.email}`}
          aria-label={`Email ${CONTACT.email}`}
          className="inline-flex h-8 w-8 items-center justify-center rounded-full text-cream/80 transition hover:bg-cream/10 hover:text-cream"
        >
          <EmailIcon className="h-4 w-4" />
        </a>

        <a
          href={SOCIAL.facebook}
          target="_blank"
          rel="noreferrer"
          aria-label="Facebook"
          className="inline-flex h-8 w-8 items-center justify-center rounded-full text-cream/80 transition hover:bg-cream/10 hover:text-cream"
        >
          <FacebookIcon className="h-4 w-4" />
        </a>
        <a
          href={SOCIAL.instagram}
          target="_blank"
          rel="noreferrer"
          aria-label="Instagram"
          className="inline-flex h-8 w-8 items-center justify-center rounded-full text-cream/80 transition hover:bg-cream/10 hover:text-cream"
        >
          <InstagramIcon className="h-4 w-4" />
        </a>
      </div>
    </div>
  );
}
