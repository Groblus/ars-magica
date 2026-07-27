import "./map-explorer.css";

type Audience = "player" | "storyguide";
type FeatureKind = "region" | "place";

type SourceReference = {
  label: string;
  locator: string;
};

type MapFeature = {
  id: string;
  kind: FeatureKind;
  name: string;
  x: number;
  y: number;
  tags: string[];
  summary: string;
  stories: string[];
  sources: SourceReference[];
  detail: "full" | "label";
  tribunal?: string;
  geometry?: string;
};

type StoryguideExtension = {
  audience: "storyguide";
  features: MapFeature[];
};

type MapData = {
  schemaVersion: "1.0";
  id: string;
  projection: "normalized-illustrative";
  audience: Audience;
  regions: MapFeature[];
  places: MapFeature[];
  storyguideExtension?: StoryguideExtension;
};

const coreTribunalSources: SourceReference[] = [
  {
    label: "Definitive Edition, Tribunal definition",
    locator: "Core Rules: 464",
  },
  {
    label: "Definitive Edition, thirteen Tribunal count",
    locator: "Core Rules: 553",
  },
  {
    label: "Definitive Edition, Tribunal names and supplement guide",
    locator: "Core Rules: 913",
  },
];

const regions: MapFeature[] = [
  ["hibernia", "Hibernian", 10, 32],
  ["loch-leglean", "Loch Leglean", 18, 17],
  ["stonehenge", "Stonehenge", 19, 37],
  ["normandy", "Normandy", 31, 51],
  ["rhine", "Rhine", 47, 42],
  ["greater-alps", "Greater Alps", 50, 56],
  ["provencal", "Provencal", 34, 68],
  ["iberian", "Iberian", 17, 78],
  ["roman", "Roman", 55, 70],
  ["transylvanian", "Transylvanian", 73, 57],
  ["theban", "Theban", 77, 83],
  ["novgorod", "Novgorod", 84, 23],
  ["levant", "Levant", 94, 93],
].map(([id, name, x, y]) => {
  const detail = id === "rhine" || id === "normandy" ? "full" : "label";
  const region: MapFeature = {
    id: `tribunal.${id}`,
    kind: "region",
    name: `${name} Tribunal`,
    x: Number(x),
    y: Number(y),
    tags: ["tribunal", "new-player-safe"],
    summary:
      detail === "full"
        ? `${name} is available as a player-safe reference region in this atlas.`
        : `${name} is shown as a Tribunal label. Detailed atlas material is not included yet.`,
    stories:
      detail === "full"
        ? [
            "Choose a covenant site and learn which mundane routes shape its visitors.",
            "Use the Tribunal as a first scale for politics, travel, and seasonal stories.",
          ]
        : ["Use this label as a starting point for corpus research and troupe discussion."],
    sources: coreTribunalSources,
    detail,
  };

  if (id === "rhine") {
    region.tags.push("covenant", "house-center", "magic", "trade");
    region.summary =
      "A player-safe Rhine overview: Black Forest covenants, river travel, founding institutions, and a dense Hermetic landscape.";
    region.sources = [
      ...coreTribunalSources,
      {
        label: "Guardians of the Forests: The Rhine Tribunal",
        locator: "Rhine Tribunal: 165, 408",
      },
    ];
    region.geometry = "M 37 31 L 57 31 L 61 50 L 51 59 L 37 54 L 34 42 Z";
  }

  if (id === "normandy") {
    region.tags.push("covenant", "mundane-power", "faerie", "trade");
    region.summary =
      "A player-safe Normandy overview: powerful covenants, river and sea routes, courts, cities, and faerie-rich frontiers.";
    region.sources = [
      ...coreTribunalSources,
      {
        label: "The Lion and the Lily: The Normandy Tribunal",
        locator: "Normandy Tribunal: 368, 372",
      },
    ];
    region.geometry = "M 20 39 L 39 40 L 43 52 L 36 61 L 21 58 L 17 48 Z";
  }

  return region;
});

const places: MapFeature[] = [
  {
    id: "place.durenmar",
    kind: "place",
    name: "Durenmar",
    x: 43,
    y: 48,
    tribunal: "Rhine",
    tags: ["covenant", "house-center", "magic", "new-player-safe"],
    summary: "Founding site in the Black Forest and a focal point for Grand Tribunal memory.",
    stories: ["A formal visit becomes a question of access, memory, and obligation."],
    sources: [
      { label: "Guardians of the Forests: The Rhine Tribunal", locator: "Rhine Tribunal: 408" },
    ],
    detail: "full",
  },
  {
    id: "place.crintera",
    kind: "place",
    name: "Crintera",
    x: 53,
    y: 25,
    tribunal: "Rhine",
    tags: ["house-center", "magic", "new-player-safe"],
    summary: "A House Bjornaer center on Rugen, useful for stories about lineage and wild places.",
    stories: ["A messenger brings an invitation whose meaning is not explained."],
    sources: [
      { label: "Guardians of the Forests: The Rhine Tribunal", locator: "Rhine Tribunal: 408" },
    ],
    detail: "full",
  },
  {
    id: "place.irencillia",
    kind: "place",
    name: "Irencillia",
    x: 56,
    y: 42,
    tribunal: "Rhine",
    tags: ["house-center", "magic", "faerie"],
    summary: "A House Merinita center in Bohemia, where stories can turn on glamour, mystery, and travel.",
    stories: ["A courteous host offers a bargain that changes with each retelling."],
    sources: [
      { label: "Guardians of the Forests: The Rhine Tribunal", locator: "Rhine Tribunal: 408" },
    ],
    detail: "full",
  },
  {
    id: "place.fengheld",
    kind: "place",
    name: "Fengheld",
    x: 48,
    y: 35,
    tribunal: "Rhine",
    tags: ["covenant", "mountain", "magic"],
    summary: "A major Rhine covenant in the Harz Mountains.",
    stories: ["A mountain route closes during the one season a visitor is expected."],
    sources: [
      { label: "Guardians of the Forests: The Rhine Tribunal", locator: "Rhine Tribunal: 408" },
    ],
    detail: "full",
  },
  {
    id: "place.waddenzee",
    kind: "place",
    name: "Waddenzee",
    x: 36,
    y: 29,
    tribunal: "Rhine",
    tags: ["covenant", "trade", "sea"],
    summary: "A northern Rhine covenant near the Frisian coast.",
    stories: ["Storm, toll, and rumor arrive together with a trading vessel."],
    sources: [
      { label: "Guardians of the Forests: The Rhine Tribunal", locator: "Rhine Tribunal: 408" },
    ],
    detail: "full",
  },
  {
    id: "place.oculus-septentrionalis",
    kind: "place",
    name: "Oculus Septentrionalis",
    x: 48,
    y: 27,
    tribunal: "Rhine",
    tags: ["covenant", "trade", "magic"],
    summary: "A Lubeck-linked Rhine covenant, useful for northern routes and Hermetic exchange.",
    stories: ["A seasonal account contains one entry that no one remembers authorizing."],
    sources: [
      { label: "Guardians of the Forests: The Rhine Tribunal", locator: "Rhine Tribunal: 408" },
    ],
    detail: "full",
  },
  {
    id: "place.rhine-gorge",
    kind: "place",
    name: "Rhine Gorge",
    x: 42,
    y: 41,
    tribunal: "Rhine",
    tags: ["trade", "mundane-power", "faerie", "new-player-safe"],
    summary: "A focused travel region for Rhine stories: river passage, castles, tolls, and old landscapes.",
    stories: ["A river journey makes every promise contingent on the next bend."],
    sources: [
      { label: "Guardians of the Forests: The Rhine Tribunal", locator: "Rhine Tribunal: 165" },
    ],
    detail: "full",
  },
  {
    id: "place.fudarus",
    kind: "place",
    name: "Fudarus",
    x: 24,
    y: 48,
    tribunal: "Normandy",
    tags: ["house-center", "covenant", "new-player-safe"],
    summary: "A House Tytalus center in the Normandy and Brittany orbit.",
    stories: ["A contest is proposed, but no one agrees on its terms."],
    sources: [
      { label: "The Lion and the Lily: The Normandy Tribunal", locator: "Normandy Tribunal: 368" },
    ],
    detail: "full",
  },
  {
    id: "place.montverte",
    kind: "place",
    name: "Montverte",
    x: 31,
    y: 44,
    tribunal: "Normandy",
    tags: ["covenant", "faerie", "magic"],
    summary: "A notable Normandy covenant site for local politics and boundary stories.",
    stories: ["A familiar path becomes contested territory after an unexpected claim."],
    sources: [
      { label: "The Lion and the Lily: The Normandy Tribunal", locator: "Normandy Tribunal: 372" },
    ],
    detail: "full",
  },
  {
    id: "place.confluensis",
    kind: "place",
    name: "Confluensis",
    x: 32,
    y: 43,
    tribunal: "Normandy",
    tags: ["covenant", "trade", "mundane-power"],
    summary: "A political heart option for Normandy-centered play.",
    stories: ["A covenant meeting turns on precedence, guests, and a disputed agreement."],
    sources: [
      { label: "The Lion and the Lily: The Normandy Tribunal", locator: "Normandy Tribunal: 372" },
    ],
    detail: "full",
  },
  {
    id: "place.dragons-rest",
    kind: "place",
    name: "Dragon's Rest",
    x: 31,
    y: 41,
    tribunal: "Normandy",
    tags: ["covenant", "trade", "magic"],
    summary: "A Mercer and Seine-facing covenant site, connected to travel and correspondence.",
    stories: ["A letter arrives with a seal that is correct, but a date that is impossible."],
    sources: [
      { label: "The Lion and the Lily: The Normandy Tribunal", locator: "Normandy Tribunal: 372" },
    ],
    detail: "full",
  },
  {
    id: "place.brittany",
    kind: "place",
    name: "Brittany",
    x: 23,
    y: 50,
    tribunal: "Normandy",
    tags: ["faerie", "mundane-power", "new-player-safe"],
    summary: "A western region of megaliths, coastlines, and faerie-rich stories.",
    stories: ["A local custom looks harmless until a covenant must keep it."],
    sources: [
      { label: "The Lion and the Lily: The Normandy Tribunal", locator: "Normandy Tribunal: 368" },
    ],
    detail: "full",
  },
  {
    id: "place.paris",
    kind: "place",
    name: "Paris",
    x: 32,
    y: 46,
    tribunal: "Normandy",
    tags: ["mundane-power", "church", "trade", "new-player-safe"],
    summary: "A great mundane city offering university, court, church, commerce, and scrutiny.",
    stories: ["A learned contact needs help that cannot be requested in public."],
    sources: [
      { label: "The Lion and the Lily: The Normandy Tribunal", locator: "Normandy Tribunal: 368" },
    ],
    detail: "full",
  },
];

const atlas: MapData = {
  schemaVersion: "1.0",
  id: "map.mythic-europe.1220",
  projection: "normalized-illustrative",
  audience: "player",
  regions,
  places,
};

const filterLabels: Record<string, string> = {
  all: "All subjects",
  tribunal: "Tribunals",
  covenant: "Covenants",
  "house-center": "House centers",
  "mundane-power": "Mundane power",
  faerie: "Faerie",
  magic: "Magic",
  church: "Church",
  trade: "Trade",
  "new-player-safe": "New player safe",
};

function escapeHtml(value: string): string {
  return value.replace(/[&<>'"]/g, (character) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;",
    };
    return entities[character];
  });
}

function featureButton(feature: MapFeature, selectedId: string): string {
  const selected = feature.id === selectedId;
  return `<button class="atlas-list-item${selected ? " is-selected" : ""}" type="button" data-atlas-select="${feature.id}" data-atlas-control="list" aria-pressed="${selected}">
    <span>${escapeHtml(feature.name)}</span>
    <small>${feature.kind === "region" ? "Tribunal" : escapeHtml(feature.tribunal ?? "Place")}</small>
  </button>`;
}

function dossier(feature: MapFeature): string {
  const tags = feature.tags
    .map((tag) => `<li>${escapeHtml(filterLabels[tag] ?? tag)}</li>`)
    .join("");
  const stories = feature.stories.map((story) => `<li>${escapeHtml(story)}</li>`).join("");
  const sources = feature.sources
    .map(
      (source) =>
        `<li><span>${escapeHtml(source.label)}</span><code>${escapeHtml(source.locator)}</code></li>`,
    )
    .join("");

  return `<div class="atlas-dossier-heading">
    <p class="atlas-kicker">${feature.kind === "region" ? "Tribunal region" : "Place dossier"}</p>
    <h2 id="atlas-dossier-title">${escapeHtml(feature.name)}</h2>
    ${feature.tribunal ? `<p class="atlas-dossier-parent">${escapeHtml(feature.tribunal)} Tribunal</p>` : ""}
  </div>
  <p class="atlas-summary">${escapeHtml(feature.summary)}</p>
  <section aria-labelledby="atlas-tags-title">
    <h3 id="atlas-tags-title">Reading lenses</h3>
    <ul class="atlas-tags">${tags}</ul>
  </section>
  <section aria-labelledby="atlas-hooks-title">
    <h3 id="atlas-hooks-title">Player-facing story prompts</h3>
    <ul class="atlas-prompts">${stories}</ul>
  </section>
  <section aria-labelledby="atlas-sources-title" class="atlas-sources">
    <h3 id="atlas-sources-title">Source locators</h3>
    <ul>${sources}</ul>
  </section>`;
}

function mapMarkup(
  visibleRegions: MapFeature[],
  visiblePlaces: MapFeature[],
  selectedId: string,
  bordersVisible: boolean,
): string {
  const regionShapes = visibleRegions
    .filter((region) => region.geometry)
    .map(
      (region) => `<path class="atlas-border${bordersVisible ? " is-visible" : ""}${region.id === selectedId ? " is-selected" : ""}" d="${region.geometry}" data-atlas-select="${region.id}" data-atlas-control="region-border" tabindex="0" role="button" aria-label="Select ${escapeHtml(region.name)} approximate boundary"></path>`,
    )
    .join("");
  const regionLabels = visibleRegions
    .map(
      (region) => `<g class="atlas-region-label${region.id === selectedId ? " is-selected" : ""}" data-atlas-select="${region.id}" data-atlas-control="region-label" tabindex="0" role="button" aria-label="Select ${escapeHtml(region.name)}">
        <rect x="${region.x - 5.7}" y="${region.y - 2.7}" width="11.4" height="5.4"></rect>
        <text x="${region.x}" y="${region.y + 0.8}" text-anchor="middle">${escapeHtml(region.name.replace(" Tribunal", ""))}</text>
      </g>`,
    )
    .join("");
  const placeMarks = visiblePlaces
    .map(
      (place) => `<g class="atlas-place-mark${place.id === selectedId ? " is-selected" : ""}" data-atlas-select="${place.id}" data-atlas-control="place-mark" tabindex="0" role="button" aria-label="Select ${escapeHtml(place.name)}">
        <circle cx="${place.x}" cy="${place.y}" r="1.35"></circle>
        <circle class="atlas-place-inner" cx="${place.x}" cy="${place.y}" r="0.38"></circle>
      </g>`,
    )
    .join("");

  return `<svg class="atlas-map" viewBox="0 0 100 100" role="group" aria-label="Illustrative map of Mythic Europe, with interactive Tribunal labels and places">
    <title>Mythic Europe Atlas</title>
    <desc>Normalized illustrative positions for player-facing Atlas discovery. This is not a canonical geographic map.</desc>
    <path class="atlas-landmass" d="M 5 18 L 19 9 L 32 12 L 42 8 L 57 14 L 69 12 L 86 17 L 96 29 L 92 40 L 99 51 L 91 61 L 96 78 L 84 92 L 72 88 L 64 80 L 52 84 L 44 75 L 36 80 L 27 73 L 16 71 L 8 59 L 12 49 L 4 39 Z"></path>
    <path class="atlas-river" d="M 54 19 C 51 27, 51 33, 46 39 S 39 48, 42 57"></path>
    <path class="atlas-river atlas-river-secondary" d="M 32 39 C 33 44, 30 48, 27 54"></path>
    <g class="atlas-borders">${regionShapes}</g>
    <g class="atlas-region-labels">${regionLabels}</g>
    <g class="atlas-place-marks">${placeMarks}</g>
  </svg>`;
}

/**
 * Mounts player-safe Mythic Europe atlas into a host element.
 *
 * Caller owns routing and creates one root per mounted module. Returned cleanup
 * removes DOM and listeners. This browser data intentionally contains no
 * Storyguide extension content, though MapData reserves that type for a gated bundle.
 */
export function mountMapExplorer(root: HTMLElement): () => void {
  let query = "";
  let activeFilter = "all";
  let selectedId = "tribunal.rhine";
  let bordersVisible = false;
  const allFeatures = [...atlas.regions, ...atlas.places];

  type FocusRestore =
    | {
        kind: "feature";
        featureId: string;
        control: string;
      }
    | {
        kind: "search";
        selectionStart: number | null;
        selectionEnd: number | null;
      };

  const restoreFocus = (target: FocusRestore): void => {
    if (target.kind === "search") {
      const search = root.querySelector<HTMLInputElement>("#atlas-search");
      search?.focus({ preventScroll: true });
      if (search && target.selectionStart !== null && target.selectionEnd !== null) {
        search.setSelectionRange(target.selectionStart, target.selectionEnd);
      }
      return;
    }
    const control = Array.from(
      root.querySelectorAll<HTMLElement>("[data-atlas-select][data-atlas-control]"),
    ).find(
      (element) =>
        element.dataset.atlasSelect === target.featureId &&
        element.dataset.atlasControl === target.control,
    );
    control?.focus({ preventScroll: true });
  };

  const selectFeature = (id: string, focusTarget?: FocusRestore): void => {
    if (allFeatures.some((feature) => feature.id === id)) {
      selectedId = id;
      render(focusTarget);
    }
  };

  const visibleFeatures = (): MapFeature[] => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    return allFeatures.filter((feature) => {
      const matchesFilter = activeFilter === "all" || feature.tags.includes(activeFilter);
      const haystack = [feature.name, feature.tribunal ?? "", feature.summary, ...feature.tags]
        .join(" ")
        .toLocaleLowerCase();
      return matchesFilter && (!normalizedQuery || haystack.includes(normalizedQuery));
    });
  };

  const render = (focusTarget?: FocusRestore): void => {
    const visible = visibleFeatures();
    const visibleRegions = atlas.regions.filter((region) => visible.includes(region));
    const visiblePlaces = atlas.places.filter((place) => visible.includes(place));
    const selected = allFeatures.find((feature) => feature.id === selectedId) ?? atlas.regions[0];
    const listFeatures = [...visibleRegions, ...visiblePlaces];
    const controls = Object.entries(filterLabels)
      .map(
        ([filter, label]) =>
          `<option value="${filter}"${activeFilter === filter ? " selected" : ""}>${escapeHtml(label)}</option>`,
      )
      .join("");

    root.innerHTML = `<section class="atlas-shell" aria-labelledby="atlas-title">
      <header class="atlas-heading">
        <div>
          <p class="atlas-kicker">Mythic Europe, 1220</p>
          <h1 id="atlas-title">Atlas of Tribunal and travel</h1>
          <p>Explore player-safe places, routes, and story scales. Map positions are illustrative normalized coordinates, not canonical borders or survey data.</p>
        </div>
        <button class="atlas-print" type="button" data-atlas-print>Print current atlas</button>
      </header>

      <div class="atlas-notice" role="note">
        <strong>Illustrative map.</strong> Tribunal labels and detailed Rhine and Normandy material are study aids. Exact boundaries, distances, and coordinates require source consultation and troupe agreement.
      </div>

      <div class="atlas-controls" aria-label="Atlas filters">
        <label class="atlas-search-label" for="atlas-search">Find a place or lens</label>
        <input id="atlas-search" type="search" placeholder="Durenmar, trade, faerie..." value="${escapeHtml(query)}" autocomplete="off">
        <label class="atlas-filter-label" for="atlas-filter">Filter</label>
        <select id="atlas-filter">${controls}</select>
        <label class="atlas-switch"><input id="atlas-borders" type="checkbox"${bordersVisible ? " checked" : ""}> <span>Show approximate region outlines</span></label>
      </div>

      <div class="atlas-workspace">
        <aside class="atlas-index" aria-label="Atlas index">
          <div class="atlas-index-heading"><h2>Index</h2><span>${listFeatures.length} shown</span></div>
          <div class="atlas-index-group">
            <h3>Tribunals</h3>
            ${visibleRegions.map((feature) => featureButton(feature, selectedId)).join("") || "<p class=\"atlas-empty\">No Tribunal matches this filter.</p>"}
          </div>
          <div class="atlas-index-group">
            <h3>Places</h3>
            ${visiblePlaces.map((feature) => featureButton(feature, selectedId)).join("") || "<p class=\"atlas-empty\">No places match this filter.</p>"}
          </div>
        </aside>

        <div class="atlas-canvas">
          ${mapMarkup(visibleRegions, visiblePlaces, selectedId, bordersVisible)}
          <p class="atlas-map-key"><span class="atlas-key-place"></span> curated place <span class="atlas-key-region"></span> Tribunal label</p>
        </div>

        <aside class="atlas-dossier" aria-live="polite" aria-labelledby="atlas-dossier-title">
          ${dossier(selected)}
        </aside>
      </div>
    </section>`;

    const search = root.querySelector<HTMLInputElement>("#atlas-search");
    const filter = root.querySelector<HTMLSelectElement>("#atlas-filter");
    const borders = root.querySelector<HTMLInputElement>("#atlas-borders");
    search?.addEventListener("input", () => {
      query = search.value;
      render({
        kind: "search",
        selectionStart: search.selectionStart,
        selectionEnd: search.selectionEnd,
      });
    });
    filter?.addEventListener("change", () => {
      activeFilter = filter.value;
      render();
    });
    borders?.addEventListener("change", () => {
      bordersVisible = borders.checked;
      render();
    });
    root.querySelector<HTMLButtonElement>("[data-atlas-print]")?.addEventListener("click", () => {
      window.print();
    });
    root.querySelectorAll<HTMLElement>("[data-atlas-select]").forEach((element) => {
      const id = element.dataset.atlasSelect;
      if (!id) return;
      element.addEventListener("click", () => selectFeature(id));
      element.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          const control = element.dataset.atlasControl;
          if (control) selectFeature(id, { kind: "feature", featureId: id, control });
        }
      });
    });
    if (focusTarget) restoreFocus(focusTarget);
  };

  render();
  return () => {
    root.replaceChildren();
  };
}
