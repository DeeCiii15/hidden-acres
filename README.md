# Hidden Acres

Modern Next.js marketing site for Hidden Acres, a wedding venue in Marion, South Carolina.

## Site map (IA)

| Path | Role |
|------|------|
| `/` | Brand home + CTAs |
| `/venue` | Comprehensive venue tour (primary offering) |
| `/portfolio` | Real wedding galleries (proof) |
| `/about` | FAQs, preferred vendors, directions |
| `/contact` | Tour / inquiry conversion |
| `/marion-sc-wedding-venue` | Location hub (local SEO) |

Nav: **Venue · Portfolio · About · Contact**

Legacy Squarespace paths 301 into the new structure via `next.config.ts`.

## Develop

```bash
npm install
npm run dev
```

## Notes

- Imagery currently uses Unsplash stand-ins — replace with venue and real wedding photography before launch.
- Portfolio couple names are illustrative placeholders until real galleries are provided.
- Contact form is client-side only until wired to email/CRM.
- Set `NEXT_PUBLIC_SITE_URL` in production for canonical URLs.
