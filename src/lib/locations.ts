import { MARION_HUB_PATH } from "./siteConfig";

export type LocationDef = {
  id: string;
  city: string;
  region: string;
  path: string;
  status: "live" | "soon";
  x: number;
  y: number;
  featured?: boolean;
  blurb: string;
};

export const locations: LocationDef[] = [
  {
    id: "marion",
    city: "Marion",
    region: "SC",
    path: MARION_HUB_PATH,
    status: "live",
    x: 58,
    y: 48,
    featured: true,
    blurb:
      "Our home base — 10 minutes from historic downtown Marion, tucked into quiet countryside.",
  },
  {
    id: "florence",
    city: "Florence",
    region: "SC",
    path: "/florence-sc-wedding-venue",
    status: "soon",
    x: 42,
    y: 40,
    blurb: "About 30 minutes west — a favorite for Pee Dee couples.",
  },
  {
    id: "myrtle-beach",
    city: "Myrtle Beach",
    region: "SC",
    path: "/myrtle-beach-sc-wedding-venue",
    status: "soon",
    x: 78,
    y: 52,
    blurb: "About an hour to the coast for destination-feeling weekends inland.",
  },
  {
    id: "mullins",
    city: "Mullins",
    region: "SC",
    path: "/mullins-sc-wedding-venue",
    status: "soon",
    x: 62,
    y: 38,
    blurb: "Nearby neighbors who love a short drive to a private estate.",
  },
];

export function getLiveLocations(): LocationDef[] {
  return locations.filter((l) => l.status === "live");
}

export function getLocationById(id: string): LocationDef | undefined {
  return locations.find((l) => l.id === id);
}

export function getLiveLocationForCityId(
  cityId?: string,
): LocationDef | undefined {
  if (!cityId) return undefined;
  const matches = getLiveLocations()
    .filter(
      (l) => cityId === l.id || cityId.startsWith(`${l.id}-`),
    )
    .sort((a, b) => b.id.length - a.id.length);
  return matches[0];
}
