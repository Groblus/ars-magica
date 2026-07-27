import './styles.css';
import {
  academyLessons,
  newPlayerPrimer,
  primerChapters,
  type AcademyLesson,
  type Citation,
  type PrimerChapter,
  type RoleId,
} from './content';
import {
  ABILITY_CATALOG,
  ART_CATALOG,
  CHARACTERISTIC_CATALOG,
  CHARACTERISTIC_NAMES,
  FLAW_CATALOG,
  HOUSE_CATALOG,
  ROLE_CATALOG,
  RULES_AUTHORITY_NOTE,
  SOURCE_REFS,
  STARTER_SPELL_CATALOG,
  VIRTUE_CATALOG,
  createDefaultDraft,
  exportCharacterArtifactSpec,
  exportCharacterJson,
  summarizeCharacterCompletion,
  totalCharacteristicCost,
  validateCharacterDraft,
  type AbilityId,
  type ArtId,
  type CharacterDraft,
  type CharacterRole,
  type CharacteristicName,
  type CharacteristicScore,
  type FlawId,
  type HouseId,
  type SourceRef,
  type StarterSpellId,
  type VirtueId,
} from './character';
import {
  actionTotal,
  castingScore,
  formulaicCasting,
  penetrationTotal,
  simpleDie,
  stressDie,
  type RuleCitation,
} from './rules';
import { mountMapExplorer } from './map-explorer';

type Route = 'start' | 'forge' | 'academy' | 'atlas';
type ForgeStepId = 'identity' | 'characteristics' | 'virtues' | 'abilities' | 'magic' | 'review';
type AcademyLessonId = (typeof academyLessons)[number]['id'];

type StartState = {
  role: RoleId;
  chapterId: string;
  answers: Record<string, number>;
};

type AcademyState = {
  lessonId: AcademyLessonId;
  answers: Record<string, number>;
  dice: {
    simpleRaw: number;
    stressSequence: string;
    botchDice: number;
    botchResults: string;
    canBotch: boolean;
  };
  action: {
    characteristic: number;
    ability: number;
    dieRaw: number;
    easeFactor: number;
  };
  casting: {
    technique: number;
    form: number;
    stamina: number;
    encumbrance: number;
    aura: number;
    dieMode: 'calm' | 'pressure';
    simpleRaw: number;
    stressSequence: string;
    botchDice: number;
    botchResults: string;
    canBotch: boolean;
    spellLevel: number;
    penetrationBonus: number;
    magicResistance: number;
    forceless: boolean;
  };
};

type PrimerCheck = {
  question: string;
  options: readonly string[];
  correctAnswer: number;
  explanation: string;
};

type ForgeStep = {
  id: ForgeStepId;
  label: string;
  description: string;
  visible: (role: CharacterRole) => boolean;
};

const routes: readonly { id: Route; label: string; short: string }[] = [
  { id: 'start', label: 'Start', short: 'Start' },
  { id: 'forge', label: 'Character Forge', short: 'Forge' },
  { id: 'academy', label: 'Rules Academy', short: 'Academy' },
  { id: 'atlas', label: 'Atlas', short: 'Atlas' },
];

const forgeSteps: readonly ForgeStep[] = [
  {
    id: 'identity',
    label: 'Identity',
    description: 'Role, concept, House, age, table names.',
    visible: () => true,
  },
  {
    id: 'characteristics',
    label: 'Characteristics',
    description: 'Eight scores with MVP point-budget feedback.',
    visible: () => true,
  },
  {
    id: 'virtues',
    label: 'Virtues and flaws',
    description: 'Curated starter choices and point balance.',
    visible: () => true,
  },
  {
    id: 'abilities',
    label: 'Abilities',
    description: 'Starter Ability XP for table-facing competence.',
    visible: () => true,
  },
  {
    id: 'magic',
    label: 'Arts and spells',
    description: 'Magus-only Arts and starter spell sketches.',
    visible: (role) => role === 'magus',
  },
  {
    id: 'review',
    label: 'Review',
    description: 'Printable summary, JSON, ArtifactSpec, warnings.',
    visible: () => true,
  },
];

const primerChecks: Record<string, PrimerCheck> = {
  'mythic-europe-1220': {
    question: 'Best first scene for Mythic Europe?',
    options: [
      'Explain every supernatural realm before play starts.',
      'Begin with one local place, one problem, one strange detail.',
      'Skip mundane history because magic replaces it.',
    ],
    correctAnswer: 1,
    explanation: 'Concrete place first. Wonder becomes playable when it attaches to one visible problem.',
  },
  'troupe-play': {
    question: 'What makes troupe play different?',
    options: [
      'One protagonist solves every story.',
      'Only Storyguide can shape saga direction.',
      'Players can shift among magi, companions, and grogs when scene needs change.',
    ],
    correctAnswer: 2,
    explanation: 'Troupe play shares spotlight and cast. Scene need decides who enters.',
  },
  covenant: {
    question: 'How should first saga prep treat covenant?',
    options: [
      'As shared institution with needs, resources, and politics.',
      'As background wallpaper until winter.',
      'As secret Storyguide material only.',
    ],
    correctAnswer: 0,
    explanation: 'Covenant is home base and pressure engine. It gives everyone something to protect or change.',
  },
  'order-and-houses': {
    question: 'Best first use of House choice?',
    options: [
      'Trivia quiz before character identity.',
      'A play-facing expectation that creates style and trouble.',
      'Pure color label with no social pressure.',
    ],
    correctAnswer: 1,
    explanation: 'House choice should create table behavior: duties, reputation, allies, and friction.',
  },
  seasons: {
    question: 'Why do seasons matter?',
    options: [
      'They make long-term study and covenant choices part of play.',
      'They replace adventures.',
      'They remove consequences between sessions.',
    ],
    correctAnswer: 0,
    explanation: 'Seasonal time turns years, study, laboratories, and recovery into playable decisions.',
  },
  'first-session': {
    question: 'Best teaching method for first session?',
    options: [
      'Rules at point of use, with starter characters if needed.',
      'Full chargen lecture before any scene.',
      'No rules explanation until after finale.',
    ],
    correctAnswer: 0,
    explanation: 'Teach when rule matters. First session should create action before encyclopedic mastery.',
  },
};

const storageKeys = {
  theme: 'ars-magica.study.theme',
  start: 'ars-magica.study.start',
  forge: 'ars-magica.study.character-draft',
  forgeStep: 'ars-magica.study.forge-step',
  academy: 'ars-magica.study.academy',
} as const;

const app = document.querySelector<HTMLDivElement>('#app');
if (!app) {
  throw new Error('Missing #app root.');
}
const appRoot: HTMLDivElement = app;

let atlasCleanup: (() => void) | null = null;
let route: Route = parseRoute();
let theme = loadTheme();
let startState = readStored<StartState>(storageKeys.start, {
  role: 'magus',
  chapterId: primerChapters[0]?.id ?? 'mythic-europe-1220',
  answers: {},
});
let draft = readDraft();
let forgeStep: ForgeStepId = readStored<ForgeStepId>(storageKeys.forgeStep, 'identity');
let academyState = readStored<AcademyState>(storageKeys.academy, defaultAcademyState());
let renderScheduled = false;

type SavedFocus = {
  readonly selector: string;
  readonly selectionStart: number | null;
  readonly selectionEnd: number | null;
};

function defaultAcademyState(): AcademyState {
  return {
    lessonId: academyLessons[0]?.id ?? 'simple-and-stress-dice',
    answers: {},
    dice: {
      simpleRaw: 7,
      stressSequence: '1,5',
      botchDice: 1,
      botchResults: '0',
      canBotch: true,
    },
    action: {
      characteristic: 1,
      ability: 3,
      dieRaw: 6,
      easeFactor: 9,
    },
    casting: {
      technique: 8,
      form: 6,
      stamina: 1,
      encumbrance: 0,
      aura: 3,
      dieMode: 'calm',
      simpleRaw: 4,
      stressSequence: '1,5',
      botchDice: 1,
      botchResults: '0',
      canBotch: true,
      spellLevel: 15,
      penetrationBonus: 2,
      magicResistance: 12,
      forceless: false,
    },
  };
}

function readDraft(): CharacterDraft {
  const stored = readStored<unknown>(storageKeys.forge, null);
  if (!stored) {
    return createDefaultDraft('magus');
  }
  return createDefaultDraft('magus', stored as Partial<CharacterDraft>);
}

function parseRoute(): Route {
  const raw = window.location.hash.replace('#', '').replace('/', '').trim();
  return routes.some((item) => item.id === raw) ? (raw as Route) : 'start';
}

function readStored<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeStored(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    return;
  }
}

function loadTheme(): 'day' | 'night' {
  const stored = readStored<'day' | 'night' | null>(storageKeys.theme, null);
  if (stored === 'day' || stored === 'night') {
    return stored;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'night' : 'day';
}

function escapeHtml(value: string | number | undefined): string {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => {
    const entities: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;',
    };
    return entities[character] ?? character;
  });
}

function option(value: string | number, label: string, selected: boolean): string {
  return `<option value="${escapeHtml(value)}"${selected ? ' selected' : ''}>${escapeHtml(label)}</option>`;
}

function checked(value: boolean): string {
  return value ? ' checked' : '';
}

function citationList(citations: readonly Citation[]): string {
  if (citations.length === 0) {
    return '';
  }
  return `<ul class="source-list">${citations
    .map(
      (citation) => `<li><span>${escapeHtml(citation.source)}</span><code>${escapeHtml(citation.locator)}</code>${
        citation.note ? `<small>${escapeHtml(citation.note)}</small>` : ''
      }</li>`,
    )
    .join('')}</ul>`;
}

function sourceRefList(refs: readonly SourceRef[]): string {
  if (refs.length === 0) {
    return '';
  }
  return `<ul class="source-list">${uniqueSourceRefs(refs)
    .map(
      (ref) => `<li><span>${escapeHtml(ref.work)}</span><code>${escapeHtml(ref.locator)}</code><small>${escapeHtml(
        ref.note,
      )}</small></li>`,
    )
    .join('')}</ul>`;
}

function ruleCitationList(citations: readonly RuleCitation[]): string {
  if (citations.length === 0) {
    return '';
  }
  return `<ul class="source-list compact">${[...new Set(citations)]
    .map((citation) => `<li><span>Definitive rules helper</span><code>${escapeHtml(citation)}</code></li>`)
    .join('')}</ul>`;
}

function uniqueSourceRefs(refs: readonly SourceRef[]): SourceRef[] {
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

function supportsRole(item: { readonly roles: readonly CharacterRole[] }, roleValue: CharacterRole): boolean {
  return item.roles.includes(roleValue);
}

function numberInput(
  label: string,
  value: number,
  attributes: string,
  optionsData: { min?: number; max?: number; step?: number } = {},
): string {
  const min = optionsData.min ?? -99;
  const max = optionsData.max ?? 500;
  const step = optionsData.step ?? 1;
  return `<label class="field"><span>${escapeHtml(label)}</span><input type="number" min="${min}" max="${max}" step="${step}" value="${escapeHtml(
    value,
  )}" ${attributes}></label>`;
}

function textInput(label: string, value: string, attributes: string): string {
  return `<label class="field"><span>${escapeHtml(label)}</span><input type="text" value="${escapeHtml(value)}" ${attributes}></label>`;
}

function textareaInput(label: string, value: string, attributes: string): string {
  return `<label class="field wide"><span>${escapeHtml(label)}</span><textarea rows="4" ${attributes}>${escapeHtml(value)}</textarea></label>`;
}

function render(): void {
  route = parseRoute();
  document.documentElement.dataset.theme = theme;
  document.body.dataset.route = route;

  if (atlasCleanup) {
    atlasCleanup();
    atlasCleanup = null;
  }

  appRoot.innerHTML = `<div class="app-shell">
    ${renderHeader()}
    <main id="main-content" class="route-frame" tabindex="-1">${renderRoute()}</main>
    ${renderMobileDock()}
  </div>`;

  installStartHeroFallback();

  if (route === 'atlas') {
    const root = document.querySelector<HTMLElement>('#atlas-root');
    if (root) {
      atlasCleanup = mountMapExplorer(root);
    }
  }
}

function installStartHeroFallback(): void {
  const heroImage = appRoot.querySelector<HTMLImageElement>('#start-hero-image');
  if (!heroImage) {
    return;
  }
  heroImage.addEventListener('error', () => {
    if (heroImage.dataset.fallbackApplied === 'true') {
      return;
    }
    heroImage.dataset.fallbackApplied = 'true';
    heroImage.src = `${import.meta.env.BASE_URL}reference/hero-placeholder.svg`;
  });
}

function saveForgeFocus(): SavedFocus | null {
  const active = document.activeElement;
  if (!(active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement || active instanceof HTMLSelectElement)) {
    return null;
  }
  const dataAttribute = [
    'field',
    'characteristic',
    'virtue',
    'flaw',
    'ability',
    'art',
    'spell',
  ].find((name) => active.dataset[name] !== undefined);
  if (!dataAttribute) {
    return null;
  }
  const value = active.dataset[dataAttribute];
  if (value === undefined) {
    return null;
  }
  const selector = `[data-${dataAttribute}="${CSS.escape(value)}"]`;
  return {
    selector,
    selectionStart: active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement ? active.selectionStart : null,
    selectionEnd: active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement ? active.selectionEnd : null,
  };
}

function saveAcademyFocus(): SavedFocus | null {
  const active = document.activeElement;
  if (!(active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement || active instanceof HTMLSelectElement)) {
    return null;
  }
  const scope = active.dataset.academyScope;
  const field = active.dataset.academyField;
  if (!scope || !field) {
    return null;
  }
  return {
    selector: `[data-academy-scope="${CSS.escape(scope)}"][data-academy-field="${CSS.escape(field)}"]`,
    selectionStart: active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement ? active.selectionStart : null,
    selectionEnd: active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement ? active.selectionEnd : null,
  };
}

function restoreForgeFocus(savedFocus: SavedFocus | null): void {
  if (!savedFocus) {
    return;
  }
  const next = appRoot.querySelector<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(savedFocus.selector);
  if (!next || next.disabled) {
    return;
  }
  next.focus({ preventScroll: true });
  if (
    (next instanceof HTMLInputElement || next instanceof HTMLTextAreaElement) &&
    savedFocus.selectionStart !== null &&
    savedFocus.selectionEnd !== null
  ) {
    next.setSelectionRange(savedFocus.selectionStart, savedFocus.selectionEnd);
  }
}

function scheduleRender(): void {
  if (renderScheduled) {
    return;
  }
  const savedFocus = route === 'forge' ? saveForgeFocus() : route === 'academy' ? saveAcademyFocus() : null;
  renderScheduled = true;
  queueMicrotask(() => {
    renderScheduled = false;
    render();
    restoreForgeFocus(savedFocus);
  });
}

function renderHeader(): string {
  const nav = routes
    .map(
      (item) => `<a href="#${item.id}" class="nav-link${route === item.id ? ' is-active' : ''}" aria-current="${
        route === item.id ? 'page' : 'false'
      }">${escapeHtml(item.label)}</a>`,
    )
    .join('');
  return `<header class="site-header">
    <a class="brand-mark" href="#start" aria-label="Ars Magica Study Folio home">
      <span class="brand-sigil">AM</span>
      <span><strong>Ars Magica</strong><small>Study Folio</small></span>
    </a>
    <nav class="desktop-nav" aria-label="Primary">${nav}</nav>
    <button class="theme-toggle" type="button" data-action="toggle-theme" aria-pressed="${theme === 'night'}">${
      theme === 'night' ? 'Day study' : 'Night study'
    }</button>
  </header>`;
}

function renderMobileDock(): string {
  return `<nav class="mobile-dock" aria-label="Mobile primary">${routes
    .map(
      (item) => `<a href="#${item.id}" class="dock-link${route === item.id ? ' is-active' : ''}" aria-current="${
        route === item.id ? 'page' : 'false'
      }"><span>${escapeHtml(item.short)}</span></a>`,
    )
    .join('')}</nav>`;
}

function renderRoute(): string {
  if (route === 'forge') {
    return renderForge();
  }
  if (route === 'academy') {
    return renderAcademy();
  }
  if (route === 'atlas') {
    return renderAtlas();
  }
  return renderStart();
}

function renderStart(): string {
  const selectedRole = newPlayerPrimer.roles.find((item) => item.id === startState.role) ?? newPlayerPrimer.roles[0];
  const activeChapter = primerChapters.find((chapter) => chapter.id === startState.chapterId) ?? primerChapters[0];
  const answered = Object.keys(startState.answers).length;
  const progress = Math.round((answered / primerChapters.length) * 100);

  return `<section class="route start-route" aria-labelledby="start-title">
    <div class="route-hero manuscript-hero">
      <figure class="start-hero-art">
        <img id="start-hero-image" src="${import.meta.env.BASE_URL}reference/hero.jpg" alt="Painterly wizard study with open manuscript">
      </figure>
      <p class="kicker">Definitive Edition study table</p>
      <h1 id="start-title">Enter Mythic Europe through play.</h1>
      <p>${escapeHtml(newPlayerPrimer.audience)}. Learn role, covenant, season, and rules at table speed.</p>
      <div class="route-actions">
        <a class="ink-button" href="#forge">Begin character</a>
        <a class="ghost-button" href="#academy">Practice rules</a>
      </div>
    </div>

    <div class="start-layout">
      <section class="folio-sheet role-selector" aria-labelledby="role-title">
        <div class="section-heading">
          <h2 id="role-title">Choose table lens</h2>
          <p>Same primer changes emphasis for Storyguide, magus, companion, or grog.</p>
        </div>
        <div class="role-ledger" role="list">${newPlayerPrimer.roles
          .map(
            (roleItem) => `<button class="ledger-row${roleItem.id === selectedRole.id ? ' is-selected' : ''}" type="button" data-start-role="${
              roleItem.id
            }" aria-pressed="${roleItem.id === selectedRole.id}">
              <span><strong>${escapeHtml(roleItem.name)}</strong><small>${escapeHtml(roleItem.tableJob)}</small></span>
              <em>${escapeHtml(roleItem.goodFirstMove)}</em>
            </button>`,
          )
          .join('')}</div>
        <aside class="margin-note">
          <h3>${escapeHtml(selectedRole.name)} play feel</h3>
          <p>${escapeHtml(selectedRole.playFeel)}</p>
          <p><strong>Watch:</strong> ${escapeHtml(selectedRole.watchFor)}</p>
          ${citationList(selectedRole.citations)}
        </aside>
      </section>

      <section class="folio-sheet primer-reader" aria-labelledby="primer-title">
        <div class="section-heading">
          <h2 id="primer-title">New player primer</h2>
          <p>${answered} of ${primerChapters.length} checks answered. ${progress}% remembered in this browser.</p>
        </div>
        <div class="chapter-tabs" role="tablist" aria-label="Primer chapters">${primerChapters
          .map(
            (chapter) => `<button type="button" role="tab" class="chapter-tab${
              chapter.id === activeChapter.id ? ' is-active' : ''
            }" aria-selected="${chapter.id === activeChapter.id}" data-chapter="${chapter.id}">${escapeHtml(
              chapter.title,
            )}</button>`,
          )
          .join('')}</div>
        ${renderPrimerChapter(activeChapter)}
      </section>
    </div>
  </section>`;
}

function renderPrimerChapter(chapter: PrimerChapter): string {
  const checkData = primerChecks[chapter.id];
  const answer = startState.answers[chapter.id];
  const feedback =
    answer === undefined || !checkData
      ? ''
      : `<div class="feedback ${answer === checkData.correctAnswer ? 'is-correct' : 'is-wrong'}" role="status"><strong>${
          answer === checkData.correctAnswer ? 'Correct.' : 'Review.'
        }</strong> ${escapeHtml(checkData.explanation)}</div>`;

  return `<article class="chapter-leaf">
    <header>
      <p>${chapter.readTimeMinutes} minute read</p>
      <h3>${escapeHtml(chapter.title)}</h3>
      <h4>${escapeHtml(chapter.subtitle)}</h4>
    </header>
    <p class="lead-copy">${escapeHtml(chapter.summary)}</p>
    <div class="two-column">
      <section>
        <h4>Essentials</h4>
        <ul class="plain-list">${chapter.essentials.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
      </section>
      <section>
        <h4>Table prompts</h4>
        <ul class="plain-list prompts">${chapter.tablePrompts.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
      </section>
    </div>
    ${
      checkData
        ? `<section class="knowledge-check" aria-labelledby="check-${chapter.id}">
          <h4 id="check-${chapter.id}">Check for understanding</h4>
          <p>${escapeHtml(checkData.question)}</p>
          <div class="choice-cluster">${checkData.options
            .map(
              (item, index) => `<button type="button" class="choice-button${answer === index ? ' is-selected' : ''}" data-primer-answer="${
                chapter.id
              }" data-answer-index="${index}">${escapeHtml(item)}</button>`,
            )
            .join('')}</div>
          ${feedback}
        </section>`
        : ''
    }
    <section class="sources-block" aria-label="Chapter citations"><h4>Sources</h4>${citationList(chapter.citations)}</section>
  </article>`;
}

function renderForge(): string {
  normalizeForgeStep();
  const completion = summarizeCharacterCompletion(draft);
  const validation = validateCharacterDraft(draft);
  const exportBlocked = validation.errors.length > 0;
  const activeStep = forgeSteps.find((step) => step.id === forgeStep) ?? forgeSteps[0];

  return `<section class="route forge-route" aria-labelledby="forge-title">
    <div class="route-hero compact-hero">
      <p class="kicker">Guided creator</p>
      <h1 id="forge-title">Forge playable drafts, not final legal characters.</h1>
      <p>Curated starter choices help magi, companions, and grogs reach table review fast.</p>
    </div>

    <div class="rules-warning" role="note">
      <strong>Rules authority warning:</strong> ${escapeHtml(RULES_AUTHORITY_NOTE)} Full legality, full spell construction, XP bucket math, and edge cases need Python rules plus table review.
    </div>

    <div class="forge-workspace">
      <aside class="forge-steps" aria-label="Character workflow steps">
        ${visibleForgeSteps()
          .map(
            (step) => `<button type="button" class="step-link${step.id === activeStep.id ? ' is-active' : ''}" data-forge-step="${
              step.id
            }"><strong>${escapeHtml(step.label)}</strong><small>${escapeHtml(step.description)}</small></button>`,
          )
          .join('')}
      </aside>
      <section class="folio-sheet forge-form" aria-labelledby="active-forge-step">
        <div class="section-heading">
          <h2 id="active-forge-step">${escapeHtml(activeStep.label)}</h2>
          <p>${escapeHtml(activeStep.description)}</p>
        </div>
        ${renderForgeStep(activeStep.id)}
      </section>
      <aside class="validation-margin" aria-live="polite">
        <h2>Completion</h2>
        <div class="seal-meter" aria-label="${completion.percent}% complete"><span style="--meter:${completion.percent}%"></span><strong>${completion.percent}%</strong></div>
        <p>${completion.done} of ${completion.total} required checks complete.</p>
        <dl class="totals-ledger">
          <div><dt>Characteristic cost</dt><dd>${validation.totals.characteristicPoints}</dd></div>
          <div><dt>Virtue points</dt><dd>${validation.totals.virtuePoints}</dd></div>
          <div><dt>Flaw points</dt><dd>${validation.totals.flawPoints}</dd></div>
          <div><dt>Ability XP</dt><dd>${validation.totals.abilityXp}</dd></div>
          <div><dt>Art XP</dt><dd>${validation.totals.artXp}</dd></div>
        </dl>
        ${renderValidationMessages()}
        <p id="forge-export-status" class="export-status" role="status">${
          exportBlocked
            ? `Downloads unlock after ${validation.errors.length} validation ${validation.errors.length === 1 ? 'issue is' : 'issues are'} resolved.`
            : 'Draft passes current validation. Exports ready for table review.'
        }</p>
        <div class="action-stack">
          <button class="ink-button" type="button" data-action="download-character-json" aria-describedby="forge-export-status"${
            exportBlocked ? ' disabled' : ''
          }>Download JSON</button>
          <button class="ghost-button" type="button" data-action="download-artifact" aria-describedby="forge-export-status"${
            exportBlocked ? ' disabled' : ''
          }>Download ArtifactSpec</button>
          <button class="ghost-button" type="button" data-action="print">Print preview</button>
          <button class="quiet-button" type="button" data-action="reset-character">Reset draft</button>
        </div>
      </aside>
    </div>
  </section>`;
}

function visibleForgeSteps(): readonly ForgeStep[] {
  return forgeSteps.filter((step) => step.visible(draft.role));
}

function normalizeForgeStep(): void {
  if (!visibleForgeSteps().some((step) => step.id === forgeStep)) {
    forgeStep = 'identity';
    writeStored(storageKeys.forgeStep, forgeStep);
  }
}

function renderForgeStep(step: ForgeStepId): string {
  if (step === 'characteristics') {
    return renderCharacteristicsStep();
  }
  if (step === 'virtues') {
    return renderVirtuesStep();
  }
  if (step === 'abilities') {
    return renderAbilitiesStep();
  }
  if (step === 'magic') {
    return renderMagicStep();
  }
  if (step === 'review') {
    return renderReviewStep();
  }
  return renderIdentityStep();
}

function renderIdentityStep(): string {
  return `<div class="form-grid">
    ${textInput('Character name', draft.name, 'data-field="name" autocomplete="off"')}
    ${textInput('Player name', draft.playerName, 'data-field="playerName" autocomplete="off"')}
    ${textInput('Saga name', draft.sagaName, 'data-field="sagaName" autocomplete="off"')}
    ${numberInput('Age', draft.age, 'data-field="age"', { min: 5, max: 120 })}
    ${textInput('Native language', draft.nativeLanguage, 'data-field="nativeLanguage" autocomplete="off"')}
    <label class="field"><span>Role</span><select data-field="role">${ROLE_CATALOG.map((item) =>
      option(item.id, item.label, draft.role === item.id),
    ).join('')}</select></label>
    ${
      draft.role === 'magus'
        ? `<label class="field"><span>Hermetic House</span><select data-field="house"><option value="">Choose House</option>${HOUSE_CATALOG.map(
            (house) => option(house.id, house.label, draft.house === house.id),
          ).join('')}</select></label>`
        : `<div class="field note-field"><span>House</span><p>House ignored for ${escapeHtml(draft.role)} drafts.</p></div>`
    }
    ${textareaInput('Concept', draft.concept, 'data-field="concept"')}
    ${textareaInput('Notes for table review', draft.notes, 'data-field="notes"')}
    <section class="sources-block wide" aria-label="Identity citations"><h3>Sources</h3>${sourceRefList([
      SOURCE_REFS.sharedCreation,
      SOURCE_REFS.templateFirst,
      SOURCE_REFS.houses,
    ])}</section>
  </div>`;
}

function renderCharacteristicsStep(): string {
  return `<div class="characteristic-board">
    ${CHARACTERISTIC_CATALOG.map((item) => {
      const score = draft.characteristics[item.id];
      return `<label class="score-control"><span><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(
        item.summary,
      )}</small></span><select data-characteristic="${item.id}">${[-3, -2, -1, 0, 1, 2, 3]
        .map((value) => option(value, String(value), score === value))
        .join('')}</select></label>`;
    }).join('')}
    <aside class="margin-note wide">
      <h3>Point budget</h3>
      <p>Current characteristic cost: <strong>${totalCharacteristicCost(draft.characteristics)}</strong> of 7 MVP points.</p>
      ${sourceRefList([SOURCE_REFS.characteristics])}
    </aside>
  </div>`;
}

function renderVirtuesStep(): string {
  const virtues = VIRTUE_CATALOG.filter((item) => supportsRole(item, draft.role));
  const flaws = FLAW_CATALOG.filter((item) => supportsRole(item, draft.role));
  return `<div class="split-workbench">
    <section>
      <h3>Virtues</h3>
      <div class="choice-ledger">${virtues
        .map(
          (virtue) => `<label class="check-row"><input type="checkbox" data-virtue="${virtue.id}"${checked(
            draft.virtues.includes(virtue.id),
          )}><span><strong>${escapeHtml(virtue.label)}</strong><small>${escapeHtml(virtue.summary)}</small><em>${escapeHtml(
            `${virtue.magnitude}, ${virtue.pointCost} point(s)`,
          )}</em></span></label>`,
        )
        .join('')}</div>
    </section>
    <section>
      <h3>Flaws</h3>
      <div class="choice-ledger">${flaws
        .map(
          (flaw) => `<label class="check-row"><input type="checkbox" data-flaw="${flaw.id}"${checked(
            draft.flaws.includes(flaw.id),
          )}><span><strong>${escapeHtml(flaw.label)}</strong><small>${escapeHtml(flaw.summary)}</small><em>${escapeHtml(
            `${flaw.magnitude}, ${flaw.pointValue} point(s)`,
          )}</em></span></label>`,
        )
        .join('')}</div>
    </section>
    <aside class="sources-block full-bleed"><h3>Sources</h3>${sourceRefList([SOURCE_REFS.sharedCreation])}</aside>
  </div>`;
}

function renderAbilitiesStep(): string {
  const abilities = ABILITY_CATALOG.filter((item) => supportsRole(item, draft.role));
  return `<div class="ability-ledger">
    ${abilities
      .map(
        (ability) => `<label class="xp-row"><span><strong>${escapeHtml(ability.label)}</strong><small>${escapeHtml(
          ability.starterHint,
        )}</small></span><input type="number" min="0" max="500" step="1" value="${escapeHtml(
          draft.abilityXp[ability.id] ?? 0,
        )}" data-ability="${ability.id}"></label>`,
      )
      .join('')}
    <aside class="margin-note wide"><h3>Ability scope</h3><p>This MVP stores non-negative XP only. Childhood, later-life, and apprenticeship buckets remain outside browser authority.</p>${sourceRefList(
      [SOURCE_REFS.abilities],
    )}</aside>
  </div>`;
}

function renderMagicStep(): string {
  if (draft.role !== 'magus') {
    return '<p class="lead-copy">Arts and starter spells are magus-only in this guided creator.</p>';
  }
  const techniques = ART_CATALOG.filter((item) => item.kind === 'technique');
  const forms = ART_CATALOG.filter((item) => item.kind === 'form');
  return `<div class="magic-workbench">
    <section>
      <h3>Techniques</h3>
      <div class="art-grid">${techniques.map(renderArtInput).join('')}</div>
    </section>
    <section>
      <h3>Forms</h3>
      <div class="art-grid">${forms.map(renderArtInput).join('')}</div>
    </section>
    <section class="full-bleed">
      <h3>Starter spell sketches</h3>
      <div class="choice-ledger spell-ledger">${STARTER_SPELL_CATALOG.map(
        (spell) => `<label class="check-row"><input type="checkbox" data-spell="${spell.id}"${checked(
          draft.starterSpellIds.includes(spell.id),
        )}><span><strong>${escapeHtml(spell.label)}</strong><small>${escapeHtml(
          `${spell.technique} ${spell.form}, level ${spell.level}. ${spell.summary}`,
        )}</small></span></label>`,
      ).join('')}</div>
    </section>
    <aside class="sources-block full-bleed"><h3>Sources</h3>${sourceRefList([
      SOURCE_REFS.magusPath,
      SOURCE_REFS.casting,
    ])}</aside>
  </div>`;
}

function renderArtInput(art: (typeof ART_CATALOG)[number]): string {
  return `<label class="xp-row compact"><span><strong>${escapeHtml(art.label)}</strong><small>${escapeHtml(
    art.summary,
  )}</small></span><input type="number" min="0" max="500" step="1" value="${escapeHtml(
    draft.artXp[art.id] ?? 0,
  )}" data-art="${art.id}"></label>`;
}

function renderReviewStep(): string {
  const validation = validateCharacterDraft(draft);
  const completion = summarizeCharacterCompletion(draft);
  const roleLabel = ROLE_CATALOG.find((item) => item.id === draft.role)?.label ?? draft.role;
  const houseLabel = draft.house ? HOUSE_CATALOG.find((item) => item.id === draft.house)?.label : undefined;
  return `<article class="print-sheet">
    <header class="print-title">
      <p>Ars Magica draft sheet</p>
      <h2>${escapeHtml(draft.name || 'Unnamed character')}</h2>
      <h3>${escapeHtml([roleLabel, houseLabel, draft.concept].filter(Boolean).join(' / ') || 'Concept missing')}</h3>
    </header>
    <div class="review-grid">
      <section><h3>Identity</h3><dl class="sheet-ledger">
        <div><dt>Role</dt><dd>${escapeHtml(roleLabel)}</dd></div>
        <div><dt>Age</dt><dd>${draft.age}</dd></div>
        <div><dt>Language</dt><dd>${escapeHtml(draft.nativeLanguage)}</dd></div>
        <div><dt>Completion</dt><dd>${completion.percent}%</dd></div>
      </dl></section>
      <section><h3>Characteristics</h3><dl class="sheet-ledger">${CHARACTERISTIC_NAMES.map(
        (name) => `<div><dt>${escapeHtml(name)}</dt><dd>${draft.characteristics[name]}</dd></div>`,
      ).join('')}</dl></section>
      <section><h3>Virtues and flaws</h3><p>${draft.virtues.length} virtue(s), ${draft.flaws.length} flaw(s).</p><p>${validation.totals.virtuePoints} virtue points, ${validation.totals.flawPoints} flaw points.</p></section>
      <section><h3>Abilities and magic</h3><p>${validation.totals.abilityXp} Ability XP. ${validation.totals.artXp} Art XP. ${validation.totals.starterSpellLevels} starter spell levels.</p></section>
    </div>
    <section class="sources-block"><h3>Sources</h3>${sourceRefList(validation.sourceRefs)}</section>
  </article>`;
}

function renderValidationMessages(): string {
  const validation = validateCharacterDraft(draft);
  const errors = validation.errors
    .map((item) => `<li><strong>${escapeHtml(item.path)}</strong><span>${escapeHtml(item.message)}</span></li>`)
    .join('');
  const advisories = [...validation.advisories, ...validation.incompleteRules]
    .slice(0, 6)
    .map((item) => `<li><span>${escapeHtml(item.message)}</span></li>`)
    .join('');
  return `<section class="validation-list">
    <h3>Errors</h3>
    ${errors ? `<ul>${errors}</ul>` : '<p>No blocking errors.</p>'}
    <h3>Advisories</h3>
    ${advisories ? `<ul>${advisories}</ul>` : '<p>No advisory notes.</p>'}
  </section>`;
}

function renderAcademy(): string {
  const lesson = academyLessons.find((item) => item.id === academyState.lessonId) ?? academyLessons[0];
  return `<section class="route academy-route" aria-labelledby="academy-title">
    <div class="route-hero compact-hero">
      <p class="kicker">Rules Academy</p>
      <h1 id="academy-title">Practice rules with deterministic rolls.</h1>
      <p>Enter die faces and totals yourself. No random roller hides math from table.</p>
    </div>
    <div class="academy-layout">
      <aside class="lesson-index" aria-label="Rules lessons">${academyLessons
        .map(
          (item) => `<button type="button" class="lesson-link${item.id === lesson.id ? ' is-active' : ''}" data-lesson="${
            item.id
          }"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.playerGoal)}</small></button>`,
        )
        .join('')}</aside>
      <section class="folio-sheet lesson-sheet" aria-labelledby="lesson-title">
        ${renderLesson(lesson)}
      </section>
    </div>
  </section>`;
}

function renderLesson(lesson: AcademyLesson): string {
  return `<article>
    <header class="lesson-head">
      <p>${escapeHtml(lesson.focus)}</p>
      <h2 id="lesson-title">${escapeHtml(lesson.title)}</h2>
      <h3>${escapeHtml(lesson.playerGoal)}</h3>
      <p>${escapeHtml(lesson.intro)}</p>
    </header>
    <div class="lesson-steps">${lesson.steps
      .map(
        (step) => `<section><h3>${escapeHtml(step.title)}</h3><p>${escapeHtml(step.body)}</p>${
          step.example ? `<p class="example-line">${escapeHtml(step.example)}</p>` : ''
        }${step.citations ? citationList(step.citations) : ''}</section>`,
      )
      .join('')}</div>
    ${renderLessonTool(lesson)}
    ${renderAcademyCheck(lesson)}
    <section class="sources-block"><h3>Lesson sources</h3>${citationList(lesson.citations)}</section>
  </article>`;
}

function renderLessonTool(lesson: AcademyLesson): string {
  if (lesson.focus === 'dice') {
    return renderDiceTool();
  }
  if (lesson.focus === 'resolution') {
    return renderActionTool();
  }
  return renderCastingTool();
}

function renderDiceTool(): string {
  const simple = safeTool(() => simpleDie(academyState.dice.simpleRaw));
  const stress = safeTool(() =>
    stressDie(
      parseDieSequence(academyState.dice.stressSequence),
      academyState.dice.botchDice,
      parseDieSequence(academyState.dice.botchResults),
      academyState.dice.canBotch,
    ),
  );
  return `<section class="tool-panel" aria-labelledby="dice-tool-title">
    <h3 id="dice-tool-title">Dice workbench</h3>
    <div class="tool-grid">
      ${numberInput('Simple raw face', academyState.dice.simpleRaw, 'data-academy-scope="dice" data-academy-field="simpleRaw"', {
        min: 0,
        max: 9,
      })}
      <label class="field"><span>Stress sequence</span><input type="text" value="${escapeHtml(
        academyState.dice.stressSequence,
      )}" data-academy-scope="dice" data-academy-field="stressSequence"></label>
      ${numberInput('Botch dice', academyState.dice.botchDice, 'data-academy-scope="dice" data-academy-field="botchDice"', {
        min: 0,
        max: 20,
      })}
      <label class="field"><span>Botch results</span><input type="text" value="${escapeHtml(
        academyState.dice.botchResults,
      )}" data-academy-scope="dice" data-academy-field="botchResults"></label>
      <label class="check-inline"><input type="checkbox" data-academy-scope="dice" data-academy-field="canBotch"${checked(
        academyState.dice.canBotch,
      )}> <span>Situation can botch</span></label>
    </div>
    ${renderToolResult('Simple die', simple)}
    ${renderToolResult('Stress die', stress)}
  </section>`;
}

function renderActionTool(): string {
  const die = safeTool(() => simpleDie(academyState.action.dieRaw));
  const result =
    'value' in die
      ? safeTool(() =>
          actionTotal(
            academyState.action.characteristic,
            academyState.action.ability,
            die.value,
            academyState.action.easeFactor,
          ),
        )
      : die;
  return `<section class="tool-panel" aria-labelledby="action-tool-title">
    <h3 id="action-tool-title">Action total workbench</h3>
    <div class="tool-grid">
      ${numberInput('Characteristic', academyState.action.characteristic, 'data-academy-scope="action" data-academy-field="characteristic"', {
        min: -5,
        max: 10,
      })}
      ${numberInput('Ability', academyState.action.ability, 'data-academy-scope="action" data-academy-field="ability"', {
        min: 0,
        max: 20,
      })}
      ${numberInput('Simple die raw face', academyState.action.dieRaw, 'data-academy-scope="action" data-academy-field="dieRaw"', {
        min: 0,
        max: 9,
      })}
      ${numberInput('Ease Factor', academyState.action.easeFactor, 'data-academy-scope="action" data-academy-field="easeFactor"', {
        min: 0,
        max: 30,
      })}
    </div>
    ${renderToolResult('Simple die', die)}
    ${renderToolResult('Action total', result)}
  </section>`;
}

function renderCastingTool(): string {
  const die = safeTool(() => {
    if (academyState.casting.dieMode === 'calm') {
      return simpleDie(academyState.casting.simpleRaw);
    }
    if (academyState.casting.dieMode === 'pressure') {
      return stressDie(
        parseDieSequence(academyState.casting.stressSequence),
        academyState.casting.botchDice,
        parseDieSequence(academyState.casting.botchResults),
        academyState.casting.canBotch,
      );
    }
    throw new RangeError('Choose Calm or pressure before resolving Formulaic casting.');
  });
  const score = safeTool(() =>
    castingScore(
      academyState.casting.technique,
      academyState.casting.form,
      academyState.casting.stamina,
      academyState.casting.encumbrance,
      academyState.casting.aura,
    ),
  );
  const formulaic =
    'value' in score && 'value' in die
      ? safeTool(() => formulaicCasting(score.value.value, die.value, academyState.casting.spellLevel))
      : 'error' in score
        ? score
        : die;
  const formulaicResult = 'value' in formulaic ? formulaic.value : null;
  const penetration =
    formulaicResult && isFormulaicCastingResult(formulaicResult) && formulaicResult.spellCast
      ? safeTool(() =>
          penetrationTotal(
            formulaicResult.total,
            academyState.casting.spellLevel,
            academyState.casting.penetrationBonus,
            academyState.casting.magicResistance,
            academyState.casting.forceless,
          ),
        )
      : null;
  const penetrationOutput =
    formulaicResult && isFormulaicCastingResult(formulaicResult) && !formulaicResult.spellCast
      ? '<div class="tool-result"><h4>Penetration total</h4><p>No Penetration Total: spell was not cast.</p></div>'
      : penetration
        ? renderToolResult('Penetration total', penetration)
        : renderToolResult('Penetration total', formulaic);

  return `<section class="tool-panel" aria-labelledby="casting-tool-title">
    <h3 id="casting-tool-title">Casting and penetration workbench</h3>
    <div class="tool-grid">
      ${numberInput('Technique', academyState.casting.technique, 'data-academy-scope="casting" data-academy-field="technique"', {
        min: 0,
        max: 50,
      })}
      ${numberInput('Form', academyState.casting.form, 'data-academy-scope="casting" data-academy-field="form"', { min: 0, max: 50 })}
      ${numberInput('Stamina', academyState.casting.stamina, 'data-academy-scope="casting" data-academy-field="stamina"', {
        min: -5,
        max: 10,
      })}
      ${numberInput('Encumbrance', academyState.casting.encumbrance, 'data-academy-scope="casting" data-academy-field="encumbrance"', {
        min: 0,
        max: 20,
      })}
      ${numberInput('Aura modifier', academyState.casting.aura, 'data-academy-scope="casting" data-academy-field="aura"', {
        min: -20,
        max: 20,
      })}
      <fieldset class="choice-field"><legend>Formulaic casting situation</legend>
        <label class="check-inline"><input type="radio" name="casting-die-mode" value="calm" data-academy-scope="casting" data-academy-field="dieMode"${checked(
          academyState.casting.dieMode === 'calm',
        )}> <span>Calm: simple die</span></label>
        <label class="check-inline"><input type="radio" name="casting-die-mode" value="pressure" data-academy-scope="casting" data-academy-field="dieMode"${checked(
          academyState.casting.dieMode === 'pressure',
        )}> <span>Pressure: stress die</span></label>
      </fieldset>
      ${
        academyState.casting.dieMode === 'calm'
          ? numberInput('Simple die raw face', academyState.casting.simpleRaw, 'data-academy-scope="casting" data-academy-field="simpleRaw"', {
              min: 0,
              max: 9,
            })
          : `<label class="field"><span>Stress sequence</span><input type="text" value="${escapeHtml(
              academyState.casting.stressSequence,
            )}" data-academy-scope="casting" data-academy-field="stressSequence"></label>
            ${numberInput('Botch dice', academyState.casting.botchDice, 'data-academy-scope="casting" data-academy-field="botchDice"', {
              min: 0,
              max: 20,
            })}
            <label class="field"><span>Botch results</span><input type="text" value="${escapeHtml(
              academyState.casting.botchResults,
            )}" data-academy-scope="casting" data-academy-field="botchResults"></label>
            <label class="check-inline"><input type="checkbox" data-academy-scope="casting" data-academy-field="canBotch"${checked(
              academyState.casting.canBotch,
            )}> <span>Situation can botch</span></label>`
      }
      ${numberInput('Spell level', academyState.casting.spellLevel, 'data-academy-scope="casting" data-academy-field="spellLevel"', {
        min: 1,
        max: 80,
      })}
      ${numberInput('Penetration bonus', academyState.casting.penetrationBonus, 'data-academy-scope="casting" data-academy-field="penetrationBonus"', {
        min: 0,
        max: 50,
      })}
      ${numberInput('Magic Resistance', academyState.casting.magicResistance, 'data-academy-scope="casting" data-academy-field="magicResistance"', {
        min: 0,
        max: 80,
      })}
      <label class="check-inline"><input type="checkbox" data-academy-scope="casting" data-academy-field="forceless"${checked(
        academyState.casting.forceless,
      )}> <span>Forceless casting cap</span></label>
    </div>
    ${renderToolResult('Casting score', score)}
    ${renderToolResult(academyState.casting.dieMode === 'calm' ? 'Simple die' : 'Stress die', die)}
    ${renderToolResult('Formulaic casting', formulaic)}
    ${penetrationOutput}
  </section>`;
}

function safeTool<T extends { readonly value: number; readonly explanations: readonly string[]; readonly warnings: readonly string[]; readonly citations: readonly RuleCitation[] }>(
  compute: () => T,
): { value: T } | { error: string } {
  try {
    return { value: compute() };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Unknown calculation error.' };
  }
}

function isFormulaicCastingResult(
  value: { readonly value: number },
): value is { readonly value: number; readonly total: number } {
  return 'total' in value && typeof value.total === 'number';
}

function parseDieSequence(value: string): number[] {
  const parts = value
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean);
  return parts.map((part) => Number(part));
}

function renderToolResult(
  title: string,
  result: { value: { readonly value: number; readonly explanations: readonly string[]; readonly warnings: readonly string[]; readonly citations: readonly RuleCitation[] } } | { error: string },
): string {
  if ('error' in result) {
    return `<div class="tool-result is-error"><h4>${escapeHtml(title)}</h4><p>${escapeHtml(result.error)}</p></div>`;
  }
  return `<div class="tool-result"><h4>${escapeHtml(title)}</h4><strong>${result.value.value}</strong><ul>${result.value.explanations
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join('')}${result.value.warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>${ruleCitationList(
    result.value.citations,
  )}</div>`;
}

function renderAcademyCheck(lesson: AcademyLesson): string {
  const answer = academyState.answers[lesson.id];
  const checkData = lesson.check;
  const feedback =
    answer === undefined
      ? ''
      : `<div class="feedback ${answer === checkData.correctAnswer ? 'is-correct' : 'is-wrong'}" role="status"><strong>${
          answer === checkData.correctAnswer ? 'Correct.' : 'Review.'
        }</strong> ${escapeHtml(checkData.explanation)}</div>`;
  return `<section class="knowledge-check" aria-labelledby="academy-check-${lesson.id}">
    <h3 id="academy-check-${lesson.id}">Knowledge check</h3>
    <p>${escapeHtml(checkData.question)}</p>
    <div class="choice-cluster">${checkData.options
      .map(
        (item, index) => `<button type="button" class="choice-button${answer === index ? ' is-selected' : ''}" data-academy-answer="${
          lesson.id
        }" data-answer-index="${index}">${escapeHtml(item)}</button>`,
      )
      .join('')}</div>
    ${feedback}
  </section>`;
}

function renderAtlas(): string {
  return `<section class="route atlas-route" aria-labelledby="atlas-route-title">
    <div class="route-hero compact-hero">
      <p class="kicker">Interactive atlas</p>
      <h1 id="atlas-route-title">Map player-safe Mythic Europe.</h1>
      <p>Tribunal labels, curated places, citations, search, filters, and clean print output.</p>
    </div>
    <div id="atlas-root" class="atlas-host" aria-live="polite"></div>
  </section>`;
}

function setDraft(next: CharacterDraft): void {
  draft = next;
  writeStored(storageKeys.forge, draft);
}

function updateDraft(patch: Partial<CharacterDraft>): void {
  setDraft(createDefaultDraft(draft.role, { ...draft, ...patch }));
}

function updateDraftField(field: string, rawValue: string): void {
  if (field === 'role') {
    const nextRole = rawValue as CharacterRole;
    const next = createDefaultDraft(nextRole, {
      name: draft.name,
      playerName: draft.playerName,
      sagaName: draft.sagaName,
      concept: draft.concept,
      notes: draft.notes,
      nativeLanguage: draft.nativeLanguage,
    });
    setDraft(next);
    forgeStep = 'identity';
    writeStored(storageKeys.forgeStep, forgeStep);
    return;
  }
  if (field === 'house') {
    updateDraft({ house: rawValue ? (rawValue as HouseId) : undefined });
    return;
  }
  if (field === 'age') {
    updateDraft({ age: Number(rawValue) });
    return;
  }
  if (field === 'name' || field === 'playerName' || field === 'sagaName' || field === 'concept' || field === 'nativeLanguage' || field === 'notes') {
    updateDraft({ [field]: rawValue } as Partial<CharacterDraft>);
  }
}

function updateCharacteristic(name: CharacteristicName, value: number): void {
  updateDraft({
    characteristics: {
      ...draft.characteristics,
      [name]: value as CharacteristicScore,
    },
  });
}

function updateXp<K extends string>(record: Partial<Record<K, number>>, id: K, rawValue: string): Partial<Record<K, number>> {
  const value = Math.max(0, Math.floor(Number(rawValue) || 0));
  const next = { ...record };
  if (value > 0) {
    next[id] = value;
  } else {
    delete next[id];
  }
  return next;
}

function toggleSelection<T extends string>(values: readonly T[], id: T, isChecked: boolean): T[] {
  const set = new Set(values);
  if (isChecked) {
    set.add(id);
  } else {
    set.delete(id);
  }
  return [...set];
}

function downloadJson(filename: string, data: unknown): void {
  const blob = new Blob([`${JSON.stringify(data, null, 2)}\n`], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

function updateAcademyValue(scope: string, field: string, rawValue: string, isChecked: boolean): void {
  if (scope === 'dice') {
    if (field === 'simpleRaw') academyState.dice.simpleRaw = Number(rawValue);
    if (field === 'stressSequence') academyState.dice.stressSequence = rawValue;
    if (field === 'botchDice') academyState.dice.botchDice = Number(rawValue);
    if (field === 'botchResults') academyState.dice.botchResults = rawValue;
    if (field === 'canBotch') academyState.dice.canBotch = isChecked;
  }
  if (scope === 'action') {
    if (field === 'characteristic') academyState.action.characteristic = Number(rawValue);
    if (field === 'ability') academyState.action.ability = Number(rawValue);
    if (field === 'dieRaw') academyState.action.dieRaw = Number(rawValue);
    if (field === 'easeFactor') academyState.action.easeFactor = Number(rawValue);
  }
  if (scope === 'casting') {
    if (field === 'technique') academyState.casting.technique = Number(rawValue);
    if (field === 'form') academyState.casting.form = Number(rawValue);
    if (field === 'stamina') academyState.casting.stamina = Number(rawValue);
    if (field === 'encumbrance') academyState.casting.encumbrance = Number(rawValue);
    if (field === 'aura') academyState.casting.aura = Number(rawValue);
    if (field === 'dieMode') academyState.casting.dieMode = rawValue === 'pressure' ? 'pressure' : 'calm';
    if (field === 'simpleRaw') academyState.casting.simpleRaw = Number(rawValue);
    if (field === 'stressSequence') academyState.casting.stressSequence = rawValue;
    if (field === 'botchDice') academyState.casting.botchDice = Number(rawValue);
    if (field === 'botchResults') academyState.casting.botchResults = rawValue;
    if (field === 'canBotch') academyState.casting.canBotch = isChecked;
    if (field === 'spellLevel') academyState.casting.spellLevel = Number(rawValue);
    if (field === 'penetrationBonus') academyState.casting.penetrationBonus = Number(rawValue);
    if (field === 'magicResistance') academyState.casting.magicResistance = Number(rawValue);
    if (field === 'forceless') academyState.casting.forceless = isChecked;
  }
  writeStored(storageKeys.academy, academyState);
}

function handleClick(event: MouseEvent): void {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  const action = target.closest<HTMLElement>('[data-action]');
  if (action?.dataset.action === 'toggle-theme') {
    theme = theme === 'night' ? 'day' : 'night';
    writeStored(storageKeys.theme, theme);
    render();
    return;
  }
  if (action?.dataset.action === 'download-character-json') {
    if (validateCharacterDraft(draft).errors.length > 0) {
      return;
    }
    downloadJson('ars-magica-character-draft.json', exportCharacterJson(draft));
    return;
  }
  if (action?.dataset.action === 'download-artifact') {
    if (validateCharacterDraft(draft).errors.length > 0) {
      return;
    }
    downloadJson('ars-magica-character-artifact.json', exportCharacterArtifactSpec(draft));
    return;
  }
  if (action?.dataset.action === 'print') {
    window.print();
    return;
  }
  if (action?.dataset.action === 'reset-character') {
    setDraft(createDefaultDraft(draft.role));
    render();
    return;
  }

  const roleButton = target.closest<HTMLElement>('[data-start-role]');
  if (roleButton?.dataset.startRole) {
    startState = { ...startState, role: roleButton.dataset.startRole as RoleId };
    writeStored(storageKeys.start, startState);
    render();
    return;
  }

  const chapterButton = target.closest<HTMLElement>('[data-chapter]');
  if (chapterButton?.dataset.chapter) {
    startState = { ...startState, chapterId: chapterButton.dataset.chapter };
    writeStored(storageKeys.start, startState);
    render();
    return;
  }

  const primerAnswer = target.closest<HTMLElement>('[data-primer-answer]');
  if (primerAnswer?.dataset.primerAnswer && primerAnswer.dataset.answerIndex) {
    startState = {
      ...startState,
      answers: {
        ...startState.answers,
        [primerAnswer.dataset.primerAnswer]: Number(primerAnswer.dataset.answerIndex),
      },
    };
    writeStored(storageKeys.start, startState);
    render();
    return;
  }

  const stepButton = target.closest<HTMLElement>('[data-forge-step]');
  if (stepButton?.dataset.forgeStep) {
    forgeStep = stepButton.dataset.forgeStep as ForgeStepId;
    writeStored(storageKeys.forgeStep, forgeStep);
    render();
    return;
  }

  const lessonButton = target.closest<HTMLElement>('[data-lesson]');
  if (lessonButton?.dataset.lesson) {
    academyState = { ...academyState, lessonId: lessonButton.dataset.lesson as AcademyLessonId };
    writeStored(storageKeys.academy, academyState);
    render();
    return;
  }

  const academyAnswer = target.closest<HTMLElement>('[data-academy-answer]');
  if (academyAnswer?.dataset.academyAnswer && academyAnswer.dataset.answerIndex) {
    academyState = {
      ...academyState,
      answers: {
        ...academyState.answers,
        [academyAnswer.dataset.academyAnswer]: Number(academyAnswer.dataset.answerIndex),
      },
    };
    writeStored(storageKeys.academy, academyState);
    render();
  }
}

function handleFormEvent(event: Event): void {
  const target = event.target;
  if (!(target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement)) {
    return;
  }
  const isChecked = target instanceof HTMLInputElement ? target.checked : false;

  if (target.dataset.field) {
    updateDraftField(target.dataset.field, target.value);
    scheduleRender();
    return;
  }
  if (target.dataset.characteristic) {
    updateCharacteristic(target.dataset.characteristic as CharacteristicName, Number(target.value));
    scheduleRender();
    return;
  }
  if (target.dataset.virtue) {
    updateDraft({ virtues: toggleSelection(draft.virtues, target.dataset.virtue as VirtueId, isChecked) });
    scheduleRender();
    return;
  }
  if (target.dataset.flaw) {
    updateDraft({ flaws: toggleSelection(draft.flaws, target.dataset.flaw as FlawId, isChecked) });
    scheduleRender();
    return;
  }
  if (target.dataset.ability) {
    updateDraft({ abilityXp: updateXp(draft.abilityXp, target.dataset.ability as AbilityId, target.value) });
    scheduleRender();
    return;
  }
  if (target.dataset.art) {
    updateDraft({ artXp: updateXp(draft.artXp, target.dataset.art as ArtId, target.value) });
    scheduleRender();
    return;
  }
  if (target.dataset.spell) {
    updateDraft({
      starterSpellIds: toggleSelection(
        draft.starterSpellIds,
        target.dataset.spell as StarterSpellId,
        isChecked,
      ),
    });
    scheduleRender();
    return;
  }
  if (target.dataset.academyScope && target.dataset.academyField) {
    updateAcademyValue(target.dataset.academyScope, target.dataset.academyField, target.value, isChecked);
    scheduleRender();
  }
}

window.addEventListener('hashchange', () => {
  render();
});
appRoot.addEventListener('click', handleClick);
appRoot.addEventListener('change', handleFormEvent);
appRoot.addEventListener('input', handleFormEvent);

if (!window.location.hash) {
  window.location.hash = '#start';
} else {
  render();
}
