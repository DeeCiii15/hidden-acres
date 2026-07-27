/** Clickable pin positions on the illustrated grounds map (percent of image). */

export type MapPinSlot = "top-left" | "bottom-left" | "mid-right";

/** Mobile only uses two slots (bottom-left is desktop-only). */
export type MapPinMobileSlot = "top-left" | "mid-right";

export type MapPin = {
  spaceSlug: string;
  /** Horizontal center of the painted pin tip, 0–100 */
  x: number;
  /** Vertical center of the painted pin tip, 0–100 */
  y: number;
  /** Which fixed popout slot this pin fills on desktop (md+) */
  slot: MapPinSlot;
  /** Which of the two inset slots this pin fills on mobile */
  mobileSlot: MapPinMobileSlot;
};

export const MAP_IMAGE = "/maps/hidden-acres-grounds-illustrated.png";

/** Intrinsic pixel size of the live map PNG (user-v12 GenerateImage). */
export const MAP_IMAGE_WIDTH = 1024;
export const MAP_IMAGE_HEIGHT = 1536;

export type SlotLayout = {
  side: "left" | "right";
  /** Vertical center of the card, % of map height */
  topPct: number;
  /** Horizontal inset from the map edge toward the center, % of map width.
   *  0 = sit on the edge (desktop); positive = overlap into the map (mobile). */
  insetPct: number;
  /** Funnel mouth sits this many % above topPct (photo, not title band) */
  mouthLift: number;
};

/**
 * Fixed anchors for the three popout cards (percent of map height).
 * Cards sit on the map edge — left/right offsets stay tight to the art.
 */
export const SLOT_LAYOUT: Record<MapPinSlot, SlotLayout> = {
  "top-left": { side: "left", topPct: 18, insetPct: 0, mouthLift: 6 },
  "mid-right": { side: "right", topPct: 60, insetPct: 0, mouthLift: 6 },
  "bottom-left": { side: "left", topPct: 78, insetPct: 0, mouthLift: 6 },
};

/**
 * Two smaller inset slots for narrow viewports:
 * top-left overlaps into the map; mid-right sits in the empty field / little-venue area.
 */
export const MOBILE_SLOT_LAYOUT: Record<MapPinMobileSlot, SlotLayout> = {
  /** Further west (toward left edge) so Chapel card clears its pin */
  "top-left": { side: "left", topPct: 17, insetPct: 6, mouthLift: 4 },
  /** Higher / further east in the right field — clear of the courtyard cluster */
  "mid-right": { side: "right", topPct: 40, insetPct: 2, mouthLift: 4 },
};

export const SLOT_DEFAULTS: Record<MapPinSlot, string> = {
  "top-left": "the-chapel",
  "mid-right": "rusted-silo",
  "bottom-left": "the-ballroom",
};

export const MOBILE_SLOT_DEFAULTS: Record<MapPinMobileSlot, string> = {
  "top-left": "the-chapel",
  "mid-right": "rusted-silo",
};

export const DESKTOP_SLOT_ORDER: MapPinSlot[] = [
  "top-left",
  "mid-right",
  "bottom-left",
];

export const MOBILE_SLOT_ORDER: MapPinMobileSlot[] = ["top-left", "mid-right"];

/**
 * Hotspot tip centers on the painted green pin markers
 * on `hidden-acres-grounds-illustrated.png` (1024×1536, user-v12 regen).
 * Hit targets in VenueMapExplorer extend upward from these tips over the pin body.
 *
 * Mobile grouping: left/grounds cluster → top-left; right cluster → mid-right.
 */
export const mapPins: MapPin[] = [
  {
    spaceSlug: "the-inn",
    x: 67.2,
    y: 7.9,
    slot: "top-left",
    mobileSlot: "top-left",
  },
  {
    spaceSlug: "the-chapel",
    x: 42.2,
    y: 35.4,
    slot: "top-left",
    mobileSlot: "top-left",
  },
  {
    spaceSlug: "ceremony-pond",
    x: 32.9,
    y: 54.7,
    slot: "top-left",
    mobileSlot: "top-left",
  },
  {
    spaceSlug: "rusted-silo",
    x: 63.5,
    y: 58.1,
    slot: "mid-right",
    mobileSlot: "mid-right",
  },
  {
    spaceSlug: "grooms-quarters",
    x: 49.1,
    y: 59.4,
    slot: "bottom-left",
    mobileSlot: "top-left",
  },
  {
    spaceSlug: "courtyard-pavilion",
    x: 60.5,
    y: 68.0,
    slot: "mid-right",
    mobileSlot: "mid-right",
  },
  {
    spaceSlug: "bridal-suite-salon",
    x: 70.9,
    y: 74.3,
    slot: "mid-right",
    mobileSlot: "mid-right",
  },
  {
    spaceSlug: "the-ballroom",
    x: 54.3,
    y: 77.9,
    slot: "bottom-left",
    mobileSlot: "top-left",
  },
];
