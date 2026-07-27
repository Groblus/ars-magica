export const CHARACTER_SCHEMA_ID = "ars-magica.character-draft.v1" as const;
export const CHARACTER_ARTIFACT_SCHEMA_ID = "ars-magica.artifact-spec.v1" as const;

export const RULES_AUTHORITY_NOTE =
  "This module enforces MVP draft constraints only. Definitive Edition core rules and Python rules remain authority for full character legality.";

export type CharacterRole = "magus" | "companion" | "grog";
export type CharacteristicScore = -3 | -2 | -1 | 0 | 1 | 2 | 3;

export const CHARACTERISTIC_NAMES = [
  "intelligence",
  "perception",
  "strength",
  "stamina",
  "presence",
  "communication",
  "dexterity",
  "quickness",
] as const;

export type CharacteristicName = (typeof CHARACTERISTIC_NAMES)[number];
export type CharacteristicBlock = Record<CharacteristicName, CharacteristicScore>;

export type HouseId =
  | "bonisagus"
  | "bjornaer"
  | "criamon"
  | "ex-miscellanea"
  | "flambeau"
  | "guernicus"
  | "jerbiton"
  | "mercere"
  | "merinita"
  | "tremere"
  | "tytalus"
  | "verditius";

export type VirtueId =
  | "the-gift"
  | "gentle-gift"
  | "affinity-art"
  | "puissant-art"
  | "book-learner"
  | "clear-thinker"
  | "privileged-upbringing"
  | "warrior"
  | "social-contacts"
  | "wealthy"
  | "tough"
  | "keen-vision"
  | "perfect-balance";

export type FlawId =
  | "necessary-condition"
  | "deficient-form"
  | "weak-spontaneous-magic"
  | "disfigured"
  | "weakness"
  | "dependent"
  | "enemy"
  | "poor"
  | "small-frame"
  | "soft-hearted"
  | "reckless"
  | "fear"
  | "ambitious"
  | "simple-minded";

export type AbilityId =
  | "area-lore"
  | "artes-liberales"
  | "athletics"
  | "awareness"
  | "brawl"
  | "charm"
  | "concentration"
  | "etiquette"
  | "folk-ken"
  | "guile"
  | "latin"
  | "magic-theory"
  | "parma-magica"
  | "profession"
  | "single-weapon"
  | "stealth"
  | "survival"
  | "teaching";

export type Technique = "Creo" | "Intellego" | "Muto" | "Perdo" | "Rego";
export type Form =
  | "Animal"
  | "Aquam"
  | "Auram"
  | "Corpus"
  | "Herbam"
  | "Ignem"
  | "Imaginem"
  | "Mentem"
  | "Terram"
  | "Vim";
export type ArtId = Technique | Form;

export type StarterSpellId =
  | "candle-and-shadow"
  | "read-surface-thought"
  | "mend-small-break"
  | "warding-hand"
  | "cleanse-foul-water"
  | "command-the-open-door"
  | "still-the-angry-heart"
  | "summon-harmless-flame";

export type SourceRef = {
  readonly id: string;
  readonly work: "Ars Magica - Definitive Edition (Core Rules)";
  readonly locator: string;
  readonly note: string;
};

export const SOURCE_REFS = {
  sharedCreation: {
    id: "core-2205-2222",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 2205-2222",
    note: "Shared character creation path.",
  },
  templateFirst: {
    id: "core-2224",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 2224",
    note: "Template-first starter advice.",
  },
  magusPath: {
    id: "core-2208-2216-2433-2465",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 2208-2216, 2433-2465",
    note: "Magus creation path and Hermetic apprenticeship scope.",
  },
  magusArchetypes: {
    id: "core-2262-2284",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 2262-2284",
    note: "Public magus archetypes.",
  },
  companionPath: {
    id: "core-985-992-2221-2297-2300",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 985-992, 2221, 2297-2300",
    note: "Companion role and creation notes.",
  },
  grogPath: {
    id: "core-1001-1009-2210-2295",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 1001-1009, 2210, 2295",
    note: "Grog role and simpler creation scope.",
  },
  houses: {
    id: "core-635-641",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 635-641",
    note: "Hermetic Houses overview.",
  },
  characteristics: {
    id: "core-2340-2355",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 2340-2355",
    note: "Eight characteristics and point-budget premise.",
  },
  abilities: {
    id: "core-2362-2394",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 2362-2394",
    note: "Age and Ability XP creation guidance.",
  },
  casting: {
    id: "core-9085-9115-9153-9165",
    work: "Ars Magica - Definitive Edition (Core Rules)",
    locator: "loc. 9085-9115, 9153-9165",
    note: "Casting totals and starter spell handling.",
  },
} as const satisfies Record<string, SourceRef>;

export type CatalogItemBase = {
  readonly id: string;
  readonly label: string;
  readonly summary: string;
  readonly sourceRefs: readonly SourceRef[];
};

export type RoleCatalogItem = CatalogItemBase & {
  readonly id: CharacterRole;
  readonly draftFocus: readonly string[];
};

export type HouseCatalogItem = CatalogItemBase & {
  readonly id: HouseId;
  readonly playstyle: readonly string[];
};

export type VirtueMagnitude = "minor" | "major" | "free";
export type FlawMagnitude = "minor" | "major";
export type VirtueCategory =
  | "hermetic"
  | "supernatural"
  | "general"
  | "social"
  | "martial"
  | "role-marker";
export type FlawCategory =
  | "hermetic"
  | "personality"
  | "story"
  | "social"
  | "general";

export type VirtueCatalogItem = CatalogItemBase & {
  readonly id: VirtueId;
  readonly magnitude: VirtueMagnitude;
  readonly pointCost: 0 | 1 | 3;
  readonly category: VirtueCategory;
  readonly roles: readonly CharacterRole[];
  readonly tags: readonly string[];
};

export type FlawCatalogItem = CatalogItemBase & {
  readonly id: FlawId;
  readonly magnitude: FlawMagnitude;
  readonly pointValue: 1 | 3;
  readonly category: FlawCategory;
  readonly roles: readonly CharacterRole[];
  readonly tags: readonly string[];
};

export type AbilityCatalogItem = CatalogItemBase & {
  readonly id: AbilityId;
  readonly roles: readonly CharacterRole[];
  readonly starterHint: string;
};

export type ArtCatalogItem = CatalogItemBase & {
  readonly id: ArtId;
  readonly kind: "technique" | "form";
};

export type StarterSpellCatalogItem = CatalogItemBase & {
  readonly id: StarterSpellId;
  readonly technique: Technique;
  readonly form: Form;
  readonly level: number;
  readonly roles: readonly CharacterRole[];
  readonly tags: readonly string[];
};

export const ROLE_CATALOG = [
  {
    id: "magus",
    label: "Magus",
    summary:
      "Gifted Hermetic wizard. Strongest rules burden: House, Arts, spells, and apprenticeship assumptions.",
    draftFocus: ["House", "The Gift", "Arts", "starter spells", "Latin", "Magic Theory"],
    sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.magusArchetypes],
  },
  {
    id: "companion",
    label: "Companion",
    summary:
      "Main non-magus protagonist. Social status, expertise, and story hooks matter more than Hermetic systems.",
    draftFocus: ["identity", "virtue/flaw story", "mundane expertise", "table role"],
    sourceRefs: [SOURCE_REFS.companionPath],
  },
  {
    id: "grog",
    label: "Grog",
    summary:
      "Supporting covenant character. Simpler build, narrow competence, no major/story/Gift package in this MVP.",
    draftFocus: ["duty", "combat or craft ability", "one vivid flaw", "covenant role"],
    sourceRefs: [SOURCE_REFS.grogPath],
  },
] as const satisfies readonly RoleCatalogItem[];

export const CHARACTERISTIC_CATALOG = [
  {
    id: "intelligence",
    label: "Intelligence",
    summary: "Reasoning, study, invention, and learned problem-solving.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
  {
    id: "perception",
    label: "Perception",
    summary: "Noticing detail, ambushes, clues, and subtle changes.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
  {
    id: "strength",
    label: "Strength",
    summary: "Raw physical power, hauling, grappling, and heavy blows.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
  {
    id: "stamina",
    label: "Stamina",
    summary: "Endurance, toughness, fatigue, wounds, and harsh conditions.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
  {
    id: "presence",
    label: "Presence",
    summary: "Force of personality, command, aura, and first impression.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
  {
    id: "communication",
    label: "Communication",
    summary: "Teaching, writing, persuasion, and clear expression.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
  {
    id: "dexterity",
    label: "Dexterity",
    summary: "Manual precision, weapon handling, craft, and careful motion.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
  {
    id: "quickness",
    label: "Quickness",
    summary: "Speed, reflex, initiative feel, and nimble movement.",
    sourceRefs: [SOURCE_REFS.characteristics],
  },
] as const satisfies readonly (CatalogItemBase & { readonly id: CharacteristicName })[];

export const HOUSE_CATALOG = [
  {
    id: "bonisagus",
    label: "Bonisagus",
    summary: "Theory, invention, and Hermetic scholarship.",
    playstyle: ["researcher", "teacher", "rules explorer"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "bjornaer",
    label: "Bjornaer",
    summary: "Inner nature, mystery, and animal transformation identity.",
    playstyle: ["mystic", "outsider", "identity drama"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "criamon",
    label: "Criamon",
    summary: "Enigma, prophecy, and strange metaphysics.",
    playstyle: ["mystic", "symbolic scenes", "slow-burn revelation"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "ex-miscellanea",
    label: "Ex Miscellanea",
    summary: "Diverse traditions folded into Hermetic society.",
    playstyle: ["folk magic", "outsider", "custom tradition"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "flambeau",
    label: "Flambeau",
    summary: "Conflict, force, and decisive magical action.",
    playstyle: ["duelist", "protector", "battle magic"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "guernicus",
    label: "Guernicus",
    summary: "Law, investigation, and Hermetic order.",
    playstyle: ["investigator", "judge", "political pressure"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "jerbiton",
    label: "Jerbiton",
    summary: "Art, society, diplomacy, and mundane contact.",
    playstyle: ["courtly", "artist", "urban liaison"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "mercere",
    label: "Mercere",
    summary: "Messages, travel, service, and covenant networks.",
    playstyle: ["networker", "traveler", "logistics"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "merinita",
    label: "Merinita",
    summary: "Faerie contact, wonder, and liminal bargains.",
    playstyle: ["faerie", "wonder", "uncertain bargains"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "tremere",
    label: "Tremere",
    summary: "Organization, duty, strategy, and disciplined power.",
    playstyle: ["planner", "chain of command", "long game"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "tytalus",
    label: "Tytalus",
    summary: "Conflict, growth through struggle, and provocation.",
    playstyle: ["rivalry", "pressure", "dangerous lessons"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
  {
    id: "verditius",
    label: "Verditius",
    summary: "Craft, devices, enchantment, and material excellence.",
    playstyle: ["maker", "commission drama", "magic items"],
    sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
  },
] as const satisfies readonly HouseCatalogItem[];

export const VIRTUE_CATALOG = [
  {
    id: "the-gift",
    label: "The Gift",
    summary: "Role marker for Gifted characters. Costs 0 here because this MVP treats it as role state.",
    magnitude: "free",
    pointCost: 0,
    category: "role-marker",
    roles: ["magus", "companion"],
    tags: ["gift"],
    sourceRefs: [SOURCE_REFS.magusPath],
  },
  {
    id: "gentle-gift",
    label: "Gentle Gift",
    summary: "Gifted social play without usual Gift friction. Best for diplomatic magi.",
    magnitude: "major",
    pointCost: 3,
    category: "hermetic",
    roles: ["magus", "companion"],
    tags: ["gift", "social"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.magusPath],
  },
  {
    id: "affinity-art",
    label: "Affinity with Art",
    summary: "Focus one Technique or Form as defining magical talent.",
    magnitude: "minor",
    pointCost: 1,
    category: "hermetic",
    roles: ["magus", "companion"],
    tags: ["art"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.magusPath],
  },
  {
    id: "puissant-art",
    label: "Puissant Art",
    summary: "One Art feels reliably strong in play. Pick Art in notes for now.",
    magnitude: "minor",
    pointCost: 1,
    category: "hermetic",
    roles: ["magus", "companion"],
    tags: ["art"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.magusPath],
  },
  {
    id: "book-learner",
    label: "Book Learner",
    summary: "Study-forward character who improves through texts and seasons.",
    magnitude: "minor",
    pointCost: 1,
    category: "general",
    roles: ["magus", "companion"],
    tags: ["study"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.abilities],
  },
  {
    id: "clear-thinker",
    label: "Clear Thinker",
    summary: "Steady mind under pressure. Useful for scholars, judges, and investigators.",
    magnitude: "minor",
    pointCost: 1,
    category: "general",
    roles: ["magus", "companion", "grog"],
    tags: ["mental"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
  {
    id: "privileged-upbringing",
    label: "Privileged Upbringing",
    summary: "Education and social access. Strong companion starter pick.",
    magnitude: "minor",
    pointCost: 1,
    category: "social",
    roles: ["companion"],
    tags: ["social", "education"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.companionPath],
  },
  {
    id: "warrior",
    label: "Warrior",
    summary: "Combat identity. Good for shield grogs and martial companions.",
    magnitude: "minor",
    pointCost: 1,
    category: "martial",
    roles: ["companion", "grog"],
    tags: ["combat"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.grogPath],
  },
  {
    id: "social-contacts",
    label: "Social Contacts",
    summary: "Built-in network for errands, rumors, and favors.",
    magnitude: "minor",
    pointCost: 1,
    category: "social",
    roles: ["companion"],
    tags: ["network"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.companionPath],
  },
  {
    id: "wealthy",
    label: "Wealthy",
    summary: "Material support and obligations. Use with storyguide approval.",
    magnitude: "major",
    pointCost: 3,
    category: "social",
    roles: ["companion"],
    tags: ["resources"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.companionPath],
  },
  {
    id: "tough",
    label: "Tough",
    summary: "Durable body. Simple, useful choice for dangerous jobs.",
    magnitude: "minor",
    pointCost: 1,
    category: "general",
    roles: ["companion", "grog"],
    tags: ["durable"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.grogPath],
  },
  {
    id: "keen-vision",
    label: "Keen Vision",
    summary: "Scout-friendly perception edge.",
    magnitude: "minor",
    pointCost: 1,
    category: "general",
    roles: ["companion", "grog"],
    tags: ["senses"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.grogPath],
  },
  {
    id: "perfect-balance",
    label: "Perfect Balance",
    summary: "Agile physical competence for scouts, thieves, and duelists.",
    magnitude: "minor",
    pointCost: 1,
    category: "general",
    roles: ["companion", "grog"],
    tags: ["movement"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
] as const satisfies readonly VirtueCatalogItem[];

export const FLAW_CATALOG = [
  {
    id: "necessary-condition",
    label: "Necessary Condition",
    summary: "Magic depends on a limiting condition. Needs table approval.",
    magnitude: "major",
    pointValue: 3,
    category: "hermetic",
    roles: ["magus"],
    tags: ["magic"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.magusPath],
  },
  {
    id: "deficient-form",
    label: "Deficient Form",
    summary: "One Form is weak. Pick Form in notes for now.",
    magnitude: "minor",
    pointValue: 1,
    category: "hermetic",
    roles: ["magus"],
    tags: ["art"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.magusPath],
  },
  {
    id: "weak-spontaneous-magic",
    label: "Weak Spontaneous Magic",
    summary: "Magic flexibility costs more. Good when player wants formulaic focus.",
    magnitude: "major",
    pointValue: 3,
    category: "hermetic",
    roles: ["magus"],
    tags: ["magic"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.casting],
  },
  {
    id: "disfigured",
    label: "Disfigured",
    summary: "Visible mark creates social friction.",
    magnitude: "minor",
    pointValue: 1,
    category: "general",
    roles: ["magus", "companion", "grog"],
    tags: ["social"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
  {
    id: "weakness",
    label: "Weakness",
    summary: "Recurring temptation or vulnerability. Define trigger in notes.",
    magnitude: "minor",
    pointValue: 1,
    category: "personality",
    roles: ["magus", "companion", "grog"],
    tags: ["personality"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
  {
    id: "dependent",
    label: "Dependent",
    summary: "Someone needs you. Strong companion hook; too big for grog MVP.",
    magnitude: "major",
    pointValue: 3,
    category: "story",
    roles: ["magus", "companion"],
    tags: ["story"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.companionPath],
  },
  {
    id: "enemy",
    label: "Enemy",
    summary: "Active opposition in saga. Requires storyguide ownership.",
    magnitude: "major",
    pointValue: 3,
    category: "story",
    roles: ["magus", "companion"],
    tags: ["story"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.companionPath],
  },
  {
    id: "poor",
    label: "Poor",
    summary: "Resource pressure and social constraint.",
    magnitude: "minor",
    pointValue: 1,
    category: "social",
    roles: ["companion", "grog"],
    tags: ["resources"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.companionPath],
  },
  {
    id: "small-frame",
    label: "Small Frame",
    summary: "Physical limitation with clear table-facing consequence.",
    magnitude: "minor",
    pointValue: 1,
    category: "general",
    roles: ["magus", "companion", "grog"],
    tags: ["body"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
  {
    id: "soft-hearted",
    label: "Soft-Hearted",
    summary: "Mercy complicates hard choices.",
    magnitude: "minor",
    pointValue: 1,
    category: "personality",
    roles: ["magus", "companion", "grog"],
    tags: ["personality"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
  {
    id: "reckless",
    label: "Reckless",
    summary: "Fast action before caution. Strong grog and companion table signal.",
    magnitude: "minor",
    pointValue: 1,
    category: "personality",
    roles: ["companion", "grog"],
    tags: ["personality"],
    sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.grogPath],
  },
  {
    id: "fear",
    label: "Fear",
    summary: "Specific fear. Define trigger plainly in notes.",
    magnitude: "minor",
    pointValue: 1,
    category: "personality",
    roles: ["magus", "companion", "grog"],
    tags: ["personality"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
  {
    id: "ambitious",
    label: "Ambitious",
    summary: "Driven personality hook that generates choices.",
    magnitude: "minor",
    pointValue: 1,
    category: "personality",
    roles: ["magus", "companion"],
    tags: ["personality"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
  {
    id: "simple-minded",
    label: "Simple-Minded",
    summary: "Narrow understanding. Use carefully; should make play fun, not remove agency.",
    magnitude: "minor",
    pointValue: 1,
    category: "general",
    roles: ["companion", "grog"],
    tags: ["mental"],
    sourceRefs: [SOURCE_REFS.sharedCreation],
  },
] as const satisfies readonly FlawCatalogItem[];

export const ABILITY_CATALOG = [
  {
    id: "area-lore",
    label: "Area Lore",
    summary: "Local knowledge, routes, customs, rumors, and dangers.",
    roles: ["magus", "companion", "grog"],
    starterHint: "Good first pick for every covenant-facing character.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "artes-liberales",
    label: "Artes Liberales",
    summary: "Educated liberal arts foundation.",
    roles: ["magus", "companion"],
    starterHint: "Useful for literate scholars and noble companions.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "athletics",
    label: "Athletics",
    summary: "Running, climbing, swimming, and physical movement.",
    roles: ["magus", "companion", "grog"],
    starterHint: "Reliable default for active characters.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "awareness",
    label: "Awareness",
    summary: "Notice ambushes, details, and nearby changes.",
    roles: ["magus", "companion", "grog"],
    starterHint: "Almost always useful at table.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "brawl",
    label: "Brawl",
    summary: "Unarmed scuffles and rough physical conflict.",
    roles: ["companion", "grog"],
    starterHint: "Good grog fallback when weapons unavailable.",
    sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.grogPath],
  },
  {
    id: "charm",
    label: "Charm",
    summary: "Warm persuasion and friendly influence.",
    roles: ["magus", "companion", "grog"],
    starterHint: "Good social companion signal.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "concentration",
    label: "Concentration",
    summary: "Hold focus under strain.",
    roles: ["magus", "companion"],
    starterHint: "Core magus table skill.",
    sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.casting],
  },
  {
    id: "etiquette",
    label: "Etiquette",
    summary: "Courtly manners and social correctness.",
    roles: ["magus", "companion"],
    starterHint: "Useful for nobles, diplomats, and Jerbiton concepts.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "folk-ken",
    label: "Folk Ken",
    summary: "Read motives and ordinary social signals.",
    roles: ["magus", "companion", "grog"],
    starterHint: "Good low-magic investigation pick.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "guile",
    label: "Guile",
    summary: "Lie, misdirect, and hide intent.",
    roles: ["magus", "companion", "grog"],
    starterHint: "Useful for spies, rogues, and political sagas.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "latin",
    label: "Latin",
    summary: "Scholarly and Hermetic language baseline.",
    roles: ["magus", "companion"],
    starterHint: "Magus draft should include some Latin XP.",
    sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.magusPath],
  },
  {
    id: "magic-theory",
    label: "Magic Theory",
    summary: "Hermetic lab and theory literacy.",
    roles: ["magus"],
    starterHint: "Magus draft should include Magic Theory XP.",
    sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.magusPath],
  },
  {
    id: "parma-magica",
    label: "Parma Magica",
    summary: "Hermetic protection and Order identity.",
    roles: ["magus"],
    starterHint: "Magus-only in this curated MVP.",
    sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.magusPath],
  },
  {
    id: "profession",
    label: "Profession",
    summary: "Craft or job competence. Define specialty in notes.",
    roles: ["companion", "grog"],
    starterHint: "Best default for covenant workers.",
    sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.grogPath],
  },
  {
    id: "single-weapon",
    label: "Single Weapon",
    summary: "Fight with one-handed weapon and shield or similar kit.",
    roles: ["companion", "grog"],
    starterHint: "Shield grog core pick.",
    sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.grogPath],
  },
  {
    id: "stealth",
    label: "Stealth",
    summary: "Move unseen and stay quiet.",
    roles: ["companion", "grog"],
    starterHint: "Scout and thief starter pick.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "survival",
    label: "Survival",
    summary: "Travel, weather, food, and wilderness judgment.",
    roles: ["magus", "companion", "grog"],
    starterHint: "Good for frontier covenants.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
  {
    id: "teaching",
    label: "Teaching",
    summary: "Train others and transmit knowledge.",
    roles: ["magus", "companion"],
    starterHint: "Useful for mentors and covenant schools.",
    sourceRefs: [SOURCE_REFS.abilities],
  },
] as const satisfies readonly AbilityCatalogItem[];

export const ART_CATALOG = [
  { id: "Creo", label: "Creo", summary: "Create, heal, perfect, or restore.", kind: "technique", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Intellego", label: "Intellego", summary: "Perceive, learn, reveal, or understand.", kind: "technique", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Muto", label: "Muto", summary: "Transform nature, shape, or properties.", kind: "technique", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Perdo", label: "Perdo", summary: "Destroy, weaken, age, or diminish.", kind: "technique", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Rego", label: "Rego", summary: "Control, command, move, ward, or govern.", kind: "technique", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Animal", label: "Animal", summary: "Animals and animal products.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Aquam", label: "Aquam", summary: "Water and liquids.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Auram", label: "Auram", summary: "Air, wind, weather, and lightning.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Corpus", label: "Corpus", summary: "Human bodies.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Herbam", label: "Herbam", summary: "Plants and plant matter.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Ignem", label: "Ignem", summary: "Fire, heat, and light.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Imaginem", label: "Imaginem", summary: "Images, sounds, smells, and species.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Mentem", label: "Mentem", summary: "Minds, emotions, and memory.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Terram", label: "Terram", summary: "Earth, stone, metal, and gems.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
  { id: "Vim", label: "Vim", summary: "Magic itself and magical power.", kind: "form", sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting] },
] as const satisfies readonly ArtCatalogItem[];

export const STARTER_SPELL_CATALOG = [
  {
    id: "candle-and-shadow",
    label: "Candle and Shadow",
    summary: "Tiny Creo Ignem practice spell for safe light scenes. Draft exercise, not full corpus item.",
    technique: "Creo",
    form: "Ignem",
    level: 5,
    roles: ["magus"],
    tags: ["practice", "light"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
  {
    id: "read-surface-thought",
    label: "Read Surface Thought",
    summary: "Intellego Mentem starter for social investigation. Requires storyguide consent in play.",
    technique: "Intellego",
    form: "Mentem",
    level: 10,
    roles: ["magus"],
    tags: ["practice", "social"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
  {
    id: "mend-small-break",
    label: "Mend Small Break",
    summary: "Creo Terram practice spell for repairing small material damage.",
    technique: "Creo",
    form: "Terram",
    level: 10,
    roles: ["magus"],
    tags: ["practice", "craft"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
  {
    id: "warding-hand",
    label: "Warding Hand",
    summary: "Rego Vim practice ward concept. Placeholder until full spell rules authorize details.",
    technique: "Rego",
    form: "Vim",
    level: 10,
    roles: ["magus"],
    tags: ["practice", "ward"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
  {
    id: "cleanse-foul-water",
    label: "Cleanse Foul Water",
    summary: "Perdo Aquam practice spell for removing impurity from water in simple scenes.",
    technique: "Perdo",
    form: "Aquam",
    level: 5,
    roles: ["magus"],
    tags: ["practice", "travel"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
  {
    id: "command-the-open-door",
    label: "Command the Open Door",
    summary: "Rego Terram practice spell for simple object movement.",
    technique: "Rego",
    form: "Terram",
    level: 5,
    roles: ["magus"],
    tags: ["practice", "utility"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
  {
    id: "still-the-angry-heart",
    label: "Still the Angry Heart",
    summary: "Perdo Mentem practice spell for emotional scene framing.",
    technique: "Perdo",
    form: "Mentem",
    level: 10,
    roles: ["magus"],
    tags: ["practice", "social"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
  {
    id: "summon-harmless-flame",
    label: "Summon Harmless Flame",
    summary: "Creo Ignem practice spell for visible magic demonstration.",
    technique: "Creo",
    form: "Ignem",
    level: 10,
    roles: ["magus"],
    tags: ["practice", "demonstration"],
    sourceRefs: [SOURCE_REFS.casting, SOURCE_REFS.magusPath],
  },
] as const satisfies readonly StarterSpellCatalogItem[];

export const MAX_CHARACTERISTIC_POINTS = 7;
export const MAX_VIRTUE_POINTS = 10;
export const MAX_FLAW_POINTS = 10;
export const GROG_MAX_MINOR_FLAWS = 3;

export type CharacterDraft = {
  readonly schema: typeof CHARACTER_SCHEMA_ID;
  readonly role: CharacterRole;
  readonly name: string;
  readonly concept: string;
  readonly playerName: string;
  readonly sagaName: string;
  readonly age: number;
  readonly nativeLanguage: string;
  readonly house?: HouseId;
  readonly characteristics: CharacteristicBlock;
  readonly virtues: readonly VirtueId[];
  readonly flaws: readonly FlawId[];
  readonly abilityXp: Partial<Record<AbilityId, number>>;
  readonly artXp: Partial<Record<ArtId, number>>;
  readonly starterSpellIds: readonly StarterSpellId[];
  readonly notes: string;
};

export type ValidationSeverity = "error" | "advisory";

export type CharacterValidationIssue = {
  readonly severity: ValidationSeverity;
  readonly code: string;
  readonly path: string;
  readonly message: string;
  readonly sourceRefs: readonly SourceRef[];
};

export type IncompleteRuleAdvisory = {
  readonly code: string;
  readonly message: string;
  readonly authority: typeof RULES_AUTHORITY_NOTE;
  readonly sourceRefs: readonly SourceRef[];
};

export type CharacterValidationTotals = {
  readonly characteristicPoints: number;
  readonly virtuePoints: number;
  readonly flawPoints: number;
  readonly abilityXp: number;
  readonly artXp: number;
  readonly starterSpellLevels: number;
};

export type CharacterValidation = {
  readonly valid: boolean;
  readonly errors: readonly CharacterValidationIssue[];
  readonly advisories: readonly CharacterValidationIssue[];
  readonly incompleteRules: readonly IncompleteRuleAdvisory[];
  readonly totals: CharacterValidationTotals;
  readonly sourceRefs: readonly SourceRef[];
};

export type CharacterCompletionStep = {
  readonly id: string;
  readonly label: string;
  readonly done: boolean;
  readonly required: boolean;
  readonly sourceRefs: readonly SourceRef[];
};

export type CharacterCompletionSummary = {
  readonly complete: boolean;
  readonly percent: number;
  readonly done: number;
  readonly total: number;
  readonly steps: readonly CharacterCompletionStep[];
  readonly nextActions: readonly string[];
  readonly errors: number;
  readonly advisories: number;
};

export type CharacterDraftParseResult = {
  readonly draft: CharacterDraft;
  readonly changed: boolean;
  readonly issues: readonly string[];
  readonly sourceRefs: readonly SourceRef[];
};

export type CharacterJsonExport = {
  readonly schema: typeof CHARACTER_SCHEMA_ID;
  readonly version: 1;
  readonly kind: "character-draft";
  readonly exportedAt: string;
  readonly rulesAuthority: typeof RULES_AUTHORITY_NOTE;
  readonly data: CharacterDraft;
  readonly validation: CharacterValidation;
  readonly completion: CharacterCompletionSummary;
  readonly sourceRefs: readonly PortableSourceReference[];
};

export type ArtifactAudience = "player" | "storyguide" | "public";

export type PortableSourceReference = {
  readonly id: string;
  readonly title: SourceRef["work"];
  readonly locator: string;
  readonly citation: string;
  readonly authority: "definitive";
  readonly notes: string;
};

export type ArtifactSpec = {
  readonly template: "magus-character-sheet" | "companion-grog-sheet";
  readonly theme: "clear-ledger";
  readonly preset: "home-letter" | "home-a4";
  readonly title: string;
  readonly audience: ArtifactAudience;
  readonly content: {
    readonly identity: Record<string, string | number>;
    readonly characteristics: CharacteristicBlock;
    readonly arts: readonly { readonly name: string; readonly score: string; readonly notes: string }[];
    readonly abilities: readonly { readonly name: string; readonly score: string; readonly notes: string }[];
    readonly virtues: readonly string[];
    readonly flaws: readonly string[];
    readonly spells: readonly { readonly name: string; readonly level: number; readonly notes: string }[];
    readonly notes: string;
  };
  readonly assets: readonly [];
  readonly source_references: readonly PortableSourceReference[];
  readonly rulesAuthority: typeof RULES_AUTHORITY_NOTE;
};

const ROLE_BY_ID = indexById<RoleCatalogItem, CharacterRole>(ROLE_CATALOG);
const HOUSE_BY_ID = indexById<HouseCatalogItem, HouseId>(HOUSE_CATALOG);
const VIRTUE_BY_ID = indexById<VirtueCatalogItem, VirtueId>(VIRTUE_CATALOG);
const FLAW_BY_ID = indexById<FlawCatalogItem, FlawId>(FLAW_CATALOG);
const ABILITY_BY_ID = indexById<AbilityCatalogItem, AbilityId>(ABILITY_CATALOG);
const ART_BY_ID = indexById<ArtCatalogItem, ArtId>(ART_CATALOG);
const STARTER_SPELL_BY_ID = indexById<StarterSpellCatalogItem, StarterSpellId>(STARTER_SPELL_CATALOG);

const EMPTY_CHARACTERISTICS: CharacteristicBlock = {
  intelligence: 0,
  perception: 0,
  strength: 0,
  stamina: 0,
  presence: 0,
  communication: 0,
  dexterity: 0,
  quickness: 0,
};

function indexById<T extends { readonly id: Id }, Id extends string>(
  items: readonly T[],
): ReadonlyMap<Id, T> {
  return new Map(items.map((item) => [item.id, item] as const));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseText(value: unknown, fallback = "", maxLength = 240): string {
  if (typeof value !== "string") {
    return fallback;
  }
  const trimmed = value.trim();
  return trimmed.length > maxLength ? trimmed.slice(0, maxLength) : trimmed;
}

function isRole(value: unknown): value is CharacterRole {
  return typeof value === "string" && ROLE_BY_ID.has(value as CharacterRole);
}

function toCharacteristicScore(value: unknown): CharacteristicScore | undefined {
  if (typeof value !== "number" || !Number.isInteger(value) || value < -3 || value > 3) {
    return undefined;
  }
  return value as CharacteristicScore;
}

function isIntegerInRange(value: unknown, minimum: number, maximum: number): value is number {
  return (
    typeof value === "number" &&
    Number.isInteger(value) &&
    value >= minimum &&
    value <= maximum
  );
}

function parseCharacteristics(
  value: unknown,
  issues: string[],
): CharacteristicBlock {
  const parsed: CharacteristicBlock = { ...EMPTY_CHARACTERISTICS };
  if (!isRecord(value)) {
    issues.push("characteristics missing or not object; reset to zero block");
    return parsed;
  }
  for (const name of CHARACTERISTIC_NAMES) {
    const score = toCharacteristicScore(value[name]);
    if (score === undefined) {
      issues.push(`characteristics.${name} invalid or missing; reset to 0`);
      parsed[name] = 0;
      continue;
    }
    parsed[name] = score;
  }
  return parsed;
}

function parseKnownIdArray<Id extends string>(
  value: unknown,
  catalog: ReadonlyMap<Id, unknown>,
  label: string,
  issues: string[],
): Id[] {
  if (!Array.isArray(value)) {
    return [];
  }
  const seen = new Set<Id>();
  const output: Id[] = [];
  for (const rawId of value) {
    if (typeof rawId !== "string") {
      issues.push(`${label} contained non-string id; skipped`);
      continue;
    }
    const id = rawId as Id;
    if (!catalog.has(id)) {
      issues.push(`${label}.${rawId} unknown; skipped`);
      continue;
    }
    if (seen.has(id)) {
      issues.push(`${label}.${rawId} duplicate; skipped`);
      continue;
    }
    seen.add(id);
    output.push(id);
  }
  return output;
}

function parseXpRecord<Id extends string>(
  value: unknown,
  catalog: ReadonlyMap<Id, unknown>,
  label: string,
  maxXp: number,
  issues: string[],
): Partial<Record<Id, number>> {
  const output: Partial<Record<Id, number>> = {};
  if (!isRecord(value)) {
    return output;
  }
  for (const [rawId, rawXp] of Object.entries(value)) {
    const id = rawId as Id;
    if (!catalog.has(id)) {
      issues.push(`${label}.${rawId} unknown; skipped`);
      continue;
    }
    if (!isIntegerInRange(rawXp, 0, maxXp)) {
      issues.push(`${label}.${rawId} invalid XP; skipped`);
      continue;
    }
    if (rawXp > 0) {
      output[id] = rawXp;
    }
  }
  return output;
}

function issue(
  severity: ValidationSeverity,
  code: string,
  path: string,
  message: string,
  sourceRefs: readonly SourceRef[],
): CharacterValidationIssue {
  return { severity, code, path, message, sourceRefs };
}

function sumRecord(record: Partial<Record<string, number>>): number {
  return Object.values(record).reduce<number>((total, value) => {
    return total + (typeof value === "number" && Number.isFinite(value) ? value : 0);
  }, 0);
}

function uniqueRefs(refs: readonly SourceRef[]): SourceRef[] {
  const seen = new Set<string>();
  const output: SourceRef[] = [];
  for (const ref of refs) {
    if (seen.has(ref.id)) {
      continue;
    }
    seen.add(ref.id);
    output.push(ref);
  }
  return output;
}

function duplicateIds(ids: readonly string[]): string[] {
  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const id of ids) {
    if (seen.has(id)) {
      duplicates.add(id);
      continue;
    }
    seen.add(id);
  }
  return [...duplicates];
}

function selectedVirtues(draft: CharacterDraft): VirtueCatalogItem[] {
  return draft.virtues.flatMap((id) => {
    const item = VIRTUE_BY_ID.get(id);
    return item ? [item] : [];
  });
}

function selectedFlaws(draft: CharacterDraft): FlawCatalogItem[] {
  return draft.flaws.flatMap((id) => {
    const item = FLAW_BY_ID.get(id);
    return item ? [item] : [];
  });
}

function roleDefaultAge(role: CharacterRole): number {
  if (role === "magus") {
    return 25;
  }
  if (role === "companion") {
    return 20;
  }
  return 18;
}

function baseDraft(role: CharacterRole): CharacterDraft {
  return {
    schema: CHARACTER_SCHEMA_ID,
    role,
    name: "",
    concept: "",
    playerName: "",
    sagaName: "",
    age: roleDefaultAge(role),
    nativeLanguage: "Local vernacular",
    house: undefined,
    characteristics: { ...EMPTY_CHARACTERISTICS },
    virtues: role === "magus" ? ["the-gift"] : [],
    flaws: [],
    abilityXp: {},
    artXp: {},
    starterSpellIds: [],
    notes: "",
  };
}

export function characteristicCost(score: CharacteristicScore | number): number {
  if (!Number.isInteger(score) || score < -3 || score > 3) {
    throw new RangeError("Characteristic score must be an integer from -3 to 3.");
  }
  const absolute = Math.abs(score);
  const cost = (absolute * (absolute + 1)) / 2;
  return score < 0 ? -cost : cost;
}

export function totalCharacteristicCost(characteristics: CharacteristicBlock): number {
  return CHARACTERISTIC_NAMES.reduce((total, name) => {
    return total + characteristicCost(characteristics[name]);
  }, 0);
}

export function totalVirtuePoints(virtues: readonly VirtueId[]): number {
  return virtues.reduce((total, id) => total + (VIRTUE_BY_ID.get(id)?.pointCost ?? 0), 0);
}

export function totalFlawPoints(flaws: readonly FlawId[]): number {
  return flaws.reduce((total, id) => total + (FLAW_BY_ID.get(id)?.pointValue ?? 0), 0);
}

export function createDefaultDraft(
  role: CharacterRole = "magus",
  overrides: Partial<CharacterDraft> = {},
): CharacterDraft {
  const safeRole = isRole(overrides.role) ? overrides.role : role;
  const base = baseDraft(safeRole);
  return {
    ...base,
    ...overrides,
    schema: CHARACTER_SCHEMA_ID,
    role: safeRole,
    characteristics: {
      ...base.characteristics,
      ...(overrides.characteristics ?? {}),
    },
    virtues: overrides.virtues ? [...overrides.virtues] : [...base.virtues],
    flaws: overrides.flaws ? [...overrides.flaws] : [...base.flaws],
    abilityXp: { ...base.abilityXp, ...(overrides.abilityXp ?? {}) },
    artXp: { ...base.artXp, ...(overrides.artXp ?? {}) },
    starterSpellIds: overrides.starterSpellIds
      ? [...overrides.starterSpellIds]
      : [...base.starterSpellIds],
  };
}

export function parseCharacterDraft(
  value: unknown,
  fallbackRole: CharacterRole = "magus",
): CharacterDraftParseResult {
  const issues: string[] = [];
  const root = isRecord(value) && isRecord(value.data) ? value.data : value;

  if (!isRecord(root)) {
    return {
      draft: baseDraft(fallbackRole),
      changed: true,
      issues: ["input not object; default draft created"],
      sourceRefs: [SOURCE_REFS.sharedCreation],
    };
  }

  const role = isRole(root.role) ? root.role : fallbackRole;
  if (!isRole(root.role)) {
    issues.push("role missing or invalid; fallback role used");
  }
  const base = baseDraft(role);
  const parsedHouse =
    typeof root.house === "string" && HOUSE_BY_ID.has(root.house as HouseId)
      ? (root.house as HouseId)
      : undefined;
  if (root.house !== undefined && parsedHouse === undefined) {
    issues.push("house unknown; skipped");
  }

  const draft: CharacterDraft = {
    schema: CHARACTER_SCHEMA_ID,
    role,
    name: parseText(root.name, base.name, 100),
    concept: parseText(root.concept, base.concept, 240),
    playerName: parseText(root.playerName, base.playerName, 100),
    sagaName: parseText(root.sagaName, base.sagaName, 100),
    age: isIntegerInRange(root.age, 0, 150) ? root.age : base.age,
    nativeLanguage: parseText(root.nativeLanguage, base.nativeLanguage, 80),
    house: parsedHouse,
    characteristics: parseCharacteristics(root.characteristics, issues),
    virtues: Array.isArray(root.virtues)
      ? parseKnownIdArray(root.virtues, VIRTUE_BY_ID, "virtues", issues)
      : [...base.virtues],
    flaws: Array.isArray(root.flaws)
      ? parseKnownIdArray(root.flaws, FLAW_BY_ID, "flaws", issues)
      : [...base.flaws],
    abilityXp: parseXpRecord(root.abilityXp, ABILITY_BY_ID, "abilityXp", 500, issues),
    artXp: parseXpRecord(root.artXp, ART_BY_ID, "artXp", 500, issues),
    starterSpellIds: Array.isArray(root.starterSpellIds)
      ? parseKnownIdArray(root.starterSpellIds, STARTER_SPELL_BY_ID, "starterSpellIds", issues)
      : [...base.starterSpellIds],
    notes: parseText(root.notes, base.notes, 2000),
  };

  if (!isIntegerInRange(root.age, 0, 150)) {
    issues.push("age missing or invalid; role default used");
  }

  return {
    draft,
    changed: issues.length > 0,
    issues,
    sourceRefs: collectSourceRefsForDraft(draft),
  };
}

export function collectSourceRefsForDraft(draft: CharacterDraft): SourceRef[] {
  const refs: SourceRef[] = [
    SOURCE_REFS.sharedCreation,
    SOURCE_REFS.templateFirst,
    SOURCE_REFS.characteristics,
    SOURCE_REFS.abilities,
  ];

  const role = ROLE_BY_ID.get(draft.role);
  if (role) {
    refs.push(...role.sourceRefs);
  }
  if (draft.house) {
    refs.push(...(HOUSE_BY_ID.get(draft.house)?.sourceRefs ?? []));
  }
  for (const virtue of selectedVirtues(draft)) {
    refs.push(...virtue.sourceRefs);
  }
  for (const flaw of selectedFlaws(draft)) {
    refs.push(...flaw.sourceRefs);
  }
  for (const abilityId of Object.keys(draft.abilityXp) as AbilityId[]) {
    refs.push(...(ABILITY_BY_ID.get(abilityId)?.sourceRefs ?? []));
  }
  for (const artId of Object.keys(draft.artXp) as ArtId[]) {
    refs.push(...(ART_BY_ID.get(artId)?.sourceRefs ?? []));
  }
  for (const spellId of draft.starterSpellIds) {
    refs.push(...(STARTER_SPELL_BY_ID.get(spellId)?.sourceRefs ?? []));
  }

  return uniqueRefs(refs);
}

export function validateCharacterDraft(draft: CharacterDraft): CharacterValidation {
  const errors: CharacterValidationIssue[] = [];
  const advisories: CharacterValidationIssue[] = [];

  const pushError = (
    code: string,
    path: string,
    message: string,
    sourceRefs: readonly SourceRef[],
  ) => errors.push(issue("error", code, path, message, sourceRefs));
  const pushAdvisory = (
    code: string,
    path: string,
    message: string,
    sourceRefs: readonly SourceRef[],
  ) => advisories.push(issue("advisory", code, path, message, sourceRefs));

  if (!ROLE_BY_ID.has(draft.role)) {
    pushError("role.invalid", "role", "Role must be magus, companion, or grog.", [
      SOURCE_REFS.sharedCreation,
    ]);
  }
  if (draft.name.trim().length === 0) {
    pushError("identity.name.required", "name", "Name required before printable export.", [
      SOURCE_REFS.sharedCreation,
    ]);
  }
  if (draft.concept.trim().length === 0) {
    pushError("identity.concept.required", "concept", "Concept required before printable export.", [
      SOURCE_REFS.templateFirst,
    ]);
  }
  if (!Number.isInteger(draft.age) || draft.age < 5 || draft.age > 120) {
    pushError("identity.age.invalid", "age", "Age must be integer from 5 to 120 for MVP drafts.", [
      SOURCE_REFS.abilities,
    ]);
  }
  if (draft.nativeLanguage.trim().length === 0) {
    pushError(
      "identity.nativeLanguage.required",
      "nativeLanguage",
      "Native language/basic language field required.",
      [SOURCE_REFS.abilities],
    );
  }

  for (const name of CHARACTERISTIC_NAMES) {
    const score = draft.characteristics[name];
    if (toCharacteristicScore(score) === undefined) {
      pushError(
        "characteristics.score.invalid",
        `characteristics.${name}`,
        `${name} must be integer from -3 to 3.`,
        [SOURCE_REFS.characteristics],
      );
    }
  }

  const characteristicPoints = CHARACTERISTIC_NAMES.reduce((total, name) => {
    const score = toCharacteristicScore(draft.characteristics[name]);
    return score === undefined ? total : total + characteristicCost(score);
  }, 0);

  if (characteristicPoints > MAX_CHARACTERISTIC_POINTS) {
    pushError(
      "characteristics.budget.exceeded",
      "characteristics",
      `Characteristic cost ${characteristicPoints} exceeds ${MAX_CHARACTERISTIC_POINTS}-point MVP budget.`,
      [SOURCE_REFS.characteristics],
    );
  }
  if (characteristicPoints < MAX_CHARACTERISTIC_POINTS) {
    pushAdvisory(
      "characteristics.budget.unspent",
      "characteristics",
      `Characteristic budget has ${MAX_CHARACTERISTIC_POINTS - characteristicPoints} unspent point(s).`,
      [SOURCE_REFS.characteristics],
    );
  }

  for (const id of duplicateIds(draft.virtues)) {
    pushError("virtues.duplicate", "virtues", `Virtue ${id} selected more than once.`, [
      SOURCE_REFS.sharedCreation,
    ]);
  }
  for (const id of duplicateIds(draft.flaws)) {
    pushError("flaws.duplicate", "flaws", `Flaw ${id} selected more than once.`, [
      SOURCE_REFS.sharedCreation,
    ]);
  }
  for (const id of draft.virtues) {
    const virtue = VIRTUE_BY_ID.get(id);
    if (!virtue) {
      pushError("virtues.unknown", "virtues", `Unknown virtue ${id}.`, [SOURCE_REFS.sharedCreation]);
      continue;
    }
    if (!virtue.roles.includes(draft.role)) {
      pushError(
        "virtues.role.invalid",
        "virtues",
        `${virtue.label} not allowed for ${draft.role} in curated MVP.`,
        virtue.sourceRefs,
      );
    }
  }
  for (const id of draft.flaws) {
    const flaw = FLAW_BY_ID.get(id);
    if (!flaw) {
      pushError("flaws.unknown", "flaws", `Unknown flaw ${id}.`, [SOURCE_REFS.sharedCreation]);
      continue;
    }
    if (!flaw.roles.includes(draft.role)) {
      pushError(
        "flaws.role.invalid",
        "flaws",
        `${flaw.label} not allowed for ${draft.role} in curated MVP.`,
        flaw.sourceRefs,
      );
    }
  }

  const virtuePoints = totalVirtuePoints(draft.virtues);
  const flawPoints = totalFlawPoints(draft.flaws);

  if (virtuePoints > MAX_VIRTUE_POINTS) {
    pushError(
      "virtues.cap.exceeded",
      "virtues",
      `Virtue points ${virtuePoints} exceed cap ${MAX_VIRTUE_POINTS}.`,
      [SOURCE_REFS.sharedCreation],
    );
  }
  if (flawPoints > MAX_FLAW_POINTS) {
    pushError("flaws.cap.exceeded", "flaws", `Flaw points ${flawPoints} exceed cap ${MAX_FLAW_POINTS}.`, [
      SOURCE_REFS.sharedCreation,
    ]);
  }
  if (virtuePoints !== flawPoints) {
    pushError(
      "virtuesFlaws.balance",
      "virtues",
      `Virtue points (${virtuePoints}) must equal flaw points (${flawPoints}) in MVP draft.`,
      [SOURCE_REFS.sharedCreation],
    );
  }

  if (draft.house && !HOUSE_BY_ID.has(draft.house)) {
    pushError("house.unknown", "house", `Unknown House ${draft.house}.`, [
      SOURCE_REFS.houses,
      SOURCE_REFS.magusPath,
    ]);
  }

  const abilityXp = sumRecord(draft.abilityXp);
  for (const [id, xp] of Object.entries(draft.abilityXp)) {
    if (!ABILITY_BY_ID.has(id as AbilityId)) {
      pushError("abilityXp.unknown", `abilityXp.${id}`, `Unknown Ability ${id}.`, [
        SOURCE_REFS.abilities,
      ]);
    }
    if (!Number.isInteger(xp) || xp < 0) {
      pushError("abilityXp.invalid", `abilityXp.${id}`, "Ability XP must be non-negative integer.", [
        SOURCE_REFS.abilities,
      ]);
    }
  }
  if (abilityXp === 0) {
    pushAdvisory(
      "abilityXp.empty",
      "abilityXp",
      "No Ability XP entered. MVP can store draft, but table-ready character needs basic abilities.",
      [SOURCE_REFS.abilities],
    );
  }

  const artXp = sumRecord(draft.artXp);
  for (const [id, xp] of Object.entries(draft.artXp)) {
    if (!ART_BY_ID.has(id as ArtId)) {
      pushError("artXp.unknown", `artXp.${id}`, `Unknown Art ${id}.`, [
        SOURCE_REFS.magusPath,
        SOURCE_REFS.casting,
      ]);
    }
    if (!Number.isInteger(xp) || xp < 0) {
      pushError("artXp.invalid", `artXp.${id}`, "Art XP must be non-negative integer.", [
        SOURCE_REFS.magusPath,
        SOURCE_REFS.casting,
      ]);
    }
  }

  let starterSpellLevels = 0;
  for (const spellId of draft.starterSpellIds) {
    const spell = STARTER_SPELL_BY_ID.get(spellId);
    if (!spell) {
      pushError("starterSpells.unknown", "starterSpellIds", `Unknown starter spell ${spellId}.`, [
        SOURCE_REFS.casting,
      ]);
      continue;
    }
    starterSpellLevels += spell.level;
    if (!spell.roles.includes(draft.role)) {
      pushError(
        "starterSpells.role.invalid",
        "starterSpellIds",
        `${spell.label} not allowed for ${draft.role} in curated MVP.`,
        spell.sourceRefs,
      );
    }
  }

  if (draft.role === "magus") {
    if (!draft.house) {
      pushError("magus.house.required", "house", "Magus requires House selection.", [
        SOURCE_REFS.houses,
        SOURCE_REFS.magusPath,
      ]);
    }
    if (!draft.virtues.includes("the-gift")) {
      pushError("magus.gift.required", "virtues", "Magus draft must include The Gift role marker.", [
        SOURCE_REFS.magusPath,
      ]);
    }
    if (artXp === 0) {
      pushError("magus.arts.required", "artXp", "Magus draft needs at least one Art XP entry.", [
        SOURCE_REFS.magusPath,
        SOURCE_REFS.casting,
      ]);
    }
    if (draft.starterSpellIds.length === 0) {
      pushError(
        "magus.starterSpells.required",
        "starterSpellIds",
        "Magus draft needs at least one starter spell sketch.",
        [SOURCE_REFS.magusPath, SOURCE_REFS.casting],
      );
    }
    if ((draft.abilityXp.latin ?? 0) === 0) {
      pushAdvisory("magus.latin.missing", "abilityXp.latin", "Magus usually needs Latin XP.", [
        SOURCE_REFS.abilities,
        SOURCE_REFS.magusPath,
      ]);
    }
    if ((draft.abilityXp["magic-theory"] ?? 0) === 0) {
      pushAdvisory(
        "magus.magicTheory.missing",
        "abilityXp.magic-theory",
        "Magus usually needs Magic Theory XP.",
        [SOURCE_REFS.abilities, SOURCE_REFS.magusPath],
      );
    }
    if (draft.age < 20) {
      pushAdvisory("magus.age.young", "age", "Magus age looks too young for apprenticeship assumptions.", [
        SOURCE_REFS.magusPath,
        SOURCE_REFS.abilities,
      ]);
    }
  }

  if (draft.role === "companion") {
    if (draft.house) {
      pushAdvisory("companion.house.ignored", "house", "House field ignored for companion drafts.", [
        SOURCE_REFS.companionPath,
      ]);
    }
    if (draft.virtues.includes("the-gift")) {
      pushAdvisory(
        "companion.gift.review",
        "virtues",
        "Gifted companion is possible as story premise, but needs storyguide review.",
        [SOURCE_REFS.companionPath, SOURCE_REFS.magusPath],
      );
    }
    if (artXp > 0 || draft.starterSpellIds.length > 0) {
      pushAdvisory(
        "companion.magic.review",
        "artXp",
        "Companion magic support is outside this MVP; Python rules must review.",
        [SOURCE_REFS.companionPath, SOURCE_REFS.casting],
      );
    }
  }

  if (draft.role === "grog") {
    if (draft.house) {
      pushAdvisory("grog.house.ignored", "house", "House field ignored for grog drafts.", [
        SOURCE_REFS.grogPath,
      ]);
    }
    const grogVirtues = selectedVirtues(draft);
    const grogFlaws = selectedFlaws(draft);
    for (const virtue of grogVirtues) {
      if (virtue.magnitude === "major") {
        pushError("grog.majorVirtue.forbidden", "virtues", "Grog MVP forbids major virtues.", [
          SOURCE_REFS.grogPath,
          ...virtue.sourceRefs,
        ]);
      }
      if (virtue.tags.includes("gift")) {
        pushError("grog.gift.forbidden", "virtues", "Grog MVP forbids The Gift or Gift-like virtues.", [
          SOURCE_REFS.grogPath,
          ...virtue.sourceRefs,
        ]);
      }
    }
    for (const flaw of grogFlaws) {
      if (flaw.magnitude === "major") {
        pushError("grog.majorFlaw.forbidden", "flaws", "Grog MVP forbids major flaws.", [
          SOURCE_REFS.grogPath,
          ...flaw.sourceRefs,
        ]);
      }
      if (flaw.category === "story") {
        pushError("grog.storyFlaw.forbidden", "flaws", "Grog MVP forbids story flaws.", [
          SOURCE_REFS.grogPath,
          ...flaw.sourceRefs,
        ]);
      }
    }
    const minorFlaws = grogFlaws.filter((flaw) => flaw.magnitude === "minor").length;
    if (minorFlaws > GROG_MAX_MINOR_FLAWS) {
      pushError(
        "grog.minorFlaw.cap",
        "flaws",
        `Grog MVP allows at most ${GROG_MAX_MINOR_FLAWS} minor flaws.`,
        [SOURCE_REFS.grogPath],
      );
    }
    if (artXp > 0 || draft.starterSpellIds.length > 0) {
      pushAdvisory(
        "grog.magic.ignored",
        "artXp",
        "Grog MVP ignores Arts and starter spells.",
        [SOURCE_REFS.grogPath, SOURCE_REFS.casting],
      );
    }
  }

  const incompleteRules: IncompleteRuleAdvisory[] = [
    {
      code: "full-virtue-flaw-legality",
      message:
        "MVP balances points and curated roles only; it does not enforce every canonical exclusion, free benefit, or social-status interaction.",
      authority: RULES_AUTHORITY_NOTE,
      sourceRefs: [SOURCE_REFS.sharedCreation],
    },
    {
      code: "ability-xp-buckets",
      message:
        "MVP checks non-negative integer XP; it does not enforce childhood, later-life, or apprenticeship bucket math.",
      authority: RULES_AUTHORITY_NOTE,
      sourceRefs: [SOURCE_REFS.abilities, SOURCE_REFS.magusPath],
    },
    {
      code: "spell-guideline-legality",
      message:
        "Starter spells are draft-safe sketches; full spell guideline, range/duration/target, requisites, and lab legality remain external.",
      authority: RULES_AUTHORITY_NOTE,
      sourceRefs: [SOURCE_REFS.casting],
    },
  ];

  const totals: CharacterValidationTotals = {
    characteristicPoints,
    virtuePoints,
    flawPoints,
    abilityXp,
    artXp,
    starterSpellLevels,
  };

  return {
    valid: errors.length === 0,
    errors,
    advisories,
    incompleteRules,
    totals,
    sourceRefs: collectSourceRefsForDraft(draft),
  };
}

export function summarizeCharacterCompletion(draft: CharacterDraft): CharacterCompletionSummary {
  const validation = validateCharacterDraft(draft);
  const steps: CharacterCompletionStep[] = [
    {
      id: "identity",
      label: "Name and concept",
      done: draft.name.trim().length > 0 && draft.concept.trim().length > 0,
      required: true,
      sourceRefs: [SOURCE_REFS.sharedCreation, SOURCE_REFS.templateFirst],
    },
    {
      id: "age-language",
      label: "Age and native language",
      done:
        Number.isInteger(draft.age) &&
        draft.age >= 5 &&
        draft.age <= 120 &&
        draft.nativeLanguage.trim().length > 0,
      required: true,
      sourceRefs: [SOURCE_REFS.abilities],
    },
    {
      id: "characteristics",
      label: "Eight characteristics within 7-point budget",
      done: validation.totals.characteristicPoints <= MAX_CHARACTERISTIC_POINTS,
      required: true,
      sourceRefs: [SOURCE_REFS.characteristics],
    },
    {
      id: "virtues-flaws",
      label: "Virtues and flaws balanced within caps",
      done:
        validation.totals.virtuePoints === validation.totals.flawPoints &&
        validation.totals.virtuePoints <= MAX_VIRTUE_POINTS &&
        validation.totals.flawPoints <= MAX_FLAW_POINTS,
      required: true,
      sourceRefs: [SOURCE_REFS.sharedCreation],
    },
    {
      id: "abilities",
      label: "Basic Ability XP started",
      done: validation.totals.abilityXp > 0,
      required: true,
      sourceRefs: [SOURCE_REFS.abilities],
    },
  ];

  if (draft.role === "magus") {
    steps.push(
      {
        id: "magus-house",
        label: "Hermetic House selected",
        done: Boolean(draft.house),
        required: true,
        sourceRefs: [SOURCE_REFS.houses, SOURCE_REFS.magusPath],
      },
      {
        id: "magus-arts",
        label: "Arts started",
        done: validation.totals.artXp > 0,
        required: true,
        sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting],
      },
      {
        id: "magus-spells",
        label: "Starter spells selected",
        done: draft.starterSpellIds.length > 0,
        required: true,
        sourceRefs: [SOURCE_REFS.magusPath, SOURCE_REFS.casting],
      },
    );
  }

  const done = steps.filter((step) => step.done).length;
  const nextActions = steps.filter((step) => !step.done).map((step) => step.label);

  return {
    complete: validation.valid && nextActions.length === 0,
    percent: Math.round((done / steps.length) * 100),
    done,
    total: steps.length,
    steps,
    nextActions,
    errors: validation.errors.length,
    advisories: validation.advisories.length + validation.incompleteRules.length,
  };
}

function exportSourceReferences(refs: readonly SourceRef[]): PortableSourceReference[] {
  const seen = new Set<string>();
  return refs.flatMap((ref) => {
    const locators = ref.locator.replace(/^loc\.\s*/, "").split(",");
    return locators.flatMap((locator, index) => {
      const normalizedLocator = locator.trim();
      const id = `${ref.id}-${index + 1}`;
      if (!normalizedLocator || seen.has(id)) {
        return [];
      }
      seen.add(id);
      return [{
        id,
        title: ref.work,
        locator: normalizedLocator,
        citation: `reviewed/Ars Magica - Definitive Edition (Core Rules).md:${normalizedLocator}`,
        authority: "definitive" as const,
        notes: ref.note,
      }];
    });
  });
}

export function exportCharacterJson(
  draft: CharacterDraft,
  options: { readonly exportedAt?: string } = {},
): CharacterJsonExport {
  const validation = validateCharacterDraft(draft);
  return {
    schema: CHARACTER_SCHEMA_ID,
    version: 1,
    kind: "character-draft",
    exportedAt: options.exportedAt ?? new Date().toISOString(),
    rulesAuthority: RULES_AUTHORITY_NOTE,
    data: draft,
    validation,
    completion: summarizeCharacterCompletion(draft),
    sourceRefs: exportSourceReferences(validation.sourceRefs),
  };
}

export function exportCharacterArtifactSpec(
  draft: CharacterDraft,
  options: {
    readonly audience?: ArtifactAudience;
    readonly paper?: "letter" | "a4";
  } = {},
): ArtifactSpec {
  const validation = validateCharacterDraft(draft);
  const roleLabel = ROLE_BY_ID.get(draft.role)?.label ?? draft.role;
  const houseLabel = draft.house ? HOUSE_BY_ID.get(draft.house)?.label : undefined;
  const virtueLabels = selectedVirtues(draft).map((virtue) => virtue.label);
  const flawLabels = selectedFlaws(draft).map((flaw) => flaw.label);
  const abilities = Object.entries(draft.abilityXp).map(([id, xp]) => {
    return {
      name: ABILITY_BY_ID.get(id as AbilityId)?.label ?? id,
      score: "",
      notes: `${xp} XP allocated in this draft`,
    };
  });
  const arts = Object.entries(draft.artXp).map(([id, xp]) => ({
    name: ART_BY_ID.get(id as ArtId)?.label ?? id,
    score: "",
    notes: `${xp} XP allocated in this draft`,
  }));
  const spells = draft.starterSpellIds.flatMap((id) => {
    const spell = STARTER_SPELL_BY_ID.get(id);
    return spell
      ? [{ name: spell.label, level: spell.level, notes: `${spell.technique} ${spell.form}` }]
      : [];
  });

  return {
    template: draft.role === "magus" ? "magus-character-sheet" : "companion-grog-sheet",
    theme: "clear-ledger",
    preset: options.paper === "a4" ? "home-a4" : "home-letter",
    title: draft.name.trim() || "Unnamed Ars Magica Character",
    audience: options.audience ?? "player",
    content: {
      identity: {
        name: draft.name.trim() || "Unnamed",
        player: draft.playerName,
        role: roleLabel,
        house: houseLabel ?? "",
        concept: draft.concept,
        age: draft.age,
      },
      characteristics: draft.characteristics,
      arts,
      abilities,
      virtues: virtueLabels,
      flaws: flawLabels,
      spells,
      notes: `${RULES_AUTHORITY_NOTE} Validation: ${validation.errors.length} error(s), ${validation.advisories.length} advisory note(s).`,
    },
    assets: [],
    source_references: exportSourceReferences(validation.sourceRefs),
    rulesAuthority: RULES_AUTHORITY_NOTE,
  };
}
