/** Clickable pin positions on the illustrated grounds map (percent of image). */

export type MapPinSlot = "top-left" | "bottom-left" | "mid-right";

export type MapPin = {
  spaceSlug: string;
  /** Horizontal center of the painted pin tip, 0–100 */
  x: number;
  /** Vertical center of the painted pin tip, 0–100 */
  y: number;
  /** Which fixed popout slot this pin fills */
  slot: MapPinSlot;
};

export const MAP_IMAGE = "/maps/hidden-acres-grounds-illustrated.png";

/** Intrinsic pixel size of the live map PNG (user-v12 GenerateImage). */
export const MAP_IMAGE_WIDTH = 1024;
export const MAP_IMAGE_HEIGHT = 1536;

/**
 * Fixed anchors for the three popout cards (percent of map height).
 * `topPct` = vertical center of the card.
 * Funnel mouths use `topPct - mouthLift` to hit the photo (not the title).
 * Cards sit on the map edge — left/right offsets stay tight to the art.
 */
export const SLOT_LAYOUT: Record<
  MapPinSlot,
  { side: "left" | "right"; topPct: number; mouthLift: number }
> = {
  "top-left": { side: "left", topPct: 18, mouthLift: 6 },
  "mid-right": { side: "right", topPct: 60, mouthLift: 6 },
  "bottom-left": { side: "left", topPct: 78, mouthLift: 6 },
};

export const SLOT_DEFAULTS: Record<MapPinSlot, string> = {
  "top-left": "the-chapel",
  "mid-right": "rusted-silo",
  "bottom-left": "the-ballroom",
};

/**
 * Hotspot tip centers on the painted green pin markers
 * on `hidden-acres-grounds-illustrated.png` (1024×1536, user-v12 regen).
 * Hit targets in VenueMapExplorer extend upward from these tips over the pin body.
 */
export const mapPins: MapPin[] = [
  { spaceSlug: "the-inn", x: 67.2, y: 7.9, slot: "top-left" },
  { spaceSlug: "the-chapel", x: 42.2, y: 35.4, slot: "top-left" },
  { spaceSlug: "ceremony-pond", x: 32.9, y: 54.7, slot: "top-left" },
  { spaceSlug: "rusted-silo", x: 63.5, y: 58.1, slot: "mid-right" },
  { spaceSlug: "grooms-quarters", x: 49.1, y: 59.4, slot: "bottom-left" },
  { spaceSlug: "courtyard-pavilion", x: 60.5, y: 68.0, slot: "mid-right" },
  { spaceSlug: "bridal-suite-salon", x: 70.9, y: 74.3, slot: "mid-right" },
  { spaceSlug: "the-ballroom", x: 54.3, y: 77.9, slot: "bottom-left" },
];
