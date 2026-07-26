/**
 * Deterministic teaching helpers matching the audited Python rules subset.
 * No function generates random rolls: callers must supply every die result.
 */

const CORE_RULES = "reviewed/Ars Magica - Definitive Edition (Core Rules).md";

export const RULE_CITATIONS = {
  dice: `${CORE_RULES}:468-520`,
  actionTotals: `${CORE_RULES}:468-470`,
  castingScore: `${CORE_RULES}:9089-9089`,
  castingBotch: `${CORE_RULES}:9093-9093`,
  formulaicCasting: `${CORE_RULES}:9099-9115`,
  penetration: `${CORE_RULES}:9153-9161`,
  forceless: `${CORE_RULES}:9350-9354`,
} as const;

export type RuleCitation = (typeof RULE_CITATIONS)[keyof typeof RULE_CITATIONS];

export interface RuleComponent {
  label: string;
  value: number;
  citation: RuleCitation;
}

export interface AuditResult {
  value: number;
  components: readonly RuleComponent[];
  explanations: readonly string[];
  warnings: readonly string[];
  citations: readonly RuleCitation[];
}

export type DieTraceKind = "simple" | "stress_initial" | "stress_reroll" | "botch";

export interface DieTraceEntry {
  kind: DieTraceKind;
  roll: number;
  value: number;
  multiplier: number;
}

export interface DieResult extends AuditResult {
  botched: boolean;
  botchCount: number;
  trace: readonly DieTraceEntry[];
}

export interface ActionTotalResult extends AuditResult {
  modifier: number;
  easeFactor: number;
  outcome: "success" | "failure" | "botch";
  succeeds: boolean;
}

export interface FormulaicCastingResult extends AuditResult {
  total: number;
  margin: number;
  spellCast: boolean;
  fatigueLevelsLost: number;
  botched: boolean;
  botchCount: number;
}

export interface PenetrationTotalResult extends AuditResult {
  total: number;
  penetrates: boolean | null;
}

function integer(value: number, label: string): void {
  if (!Number.isInteger(value)) {
    throw new TypeError(`${label} must be an integer, got ${value}.`);
  }
}

function dieFace(value: number, label: string): void {
  integer(value, label);
  if (value < 0 || value > 9) {
    throw new RangeError(`Ars Magica dice are ten-sided and use rolls 0-9, got ${value}.`);
  }
}

function audit(
  value: number,
  components: readonly RuleComponent[],
  explanations: readonly string[],
  warnings: readonly string[],
  citations: readonly RuleCitation[],
): AuditResult {
  return { value, components, explanations, warnings, citations };
}

/** Resolve one simple die. A raw 0 counts as 10. */
export function simpleDie(raw: number): DieResult {
  dieFace(raw, "Simple die roll");
  const value = raw === 0 ? 10 : raw;

  return {
    ...audit(
      value,
      [{ label: "Simple die", value, citation: RULE_CITATIONS.dice }],
      [raw === 0 ? "Simple die raw 0 counts as 10." : "Simple die uses its rolled value."],
      [],
      [RULE_CITATIONS.dice],
    ),
    botched: false,
    botchCount: 0,
    trace: [{ kind: "simple", roll: raw, value, multiplier: 1 }],
  };
}

/**
 * Resolve stress die using supplied faces only.
 *
 * `sequence` contains initial face, then explosion rerolls. `botchResults`
 * contains faces for botch dice after an initial 0. Extra supplied faces are
 * ignored, matching Python helper consumption.
 */
export function stressDie(
  sequence: readonly number[],
  botchDice: number = 1,
  botchResults: readonly number[] = [],
  canBotch: boolean = true,
): DieResult {
  integer(botchDice, "Botch dice");
  if (botchDice < 0) {
    throw new RangeError("Botch dice must be non-negative.");
  }
  if (sequence.length === 0) {
    throw new RangeError("Stress die needs an initial supplied roll.");
  }

  let sequenceIndex = 0;
  let botchIndex = 0;
  const takeSequence = (): number => {
    if (sequenceIndex >= sequence.length) {
      throw new RangeError("Not enough supplied stress rolls.");
    }
    const roll = sequence[sequenceIndex++];
    dieFace(roll, "Stress die roll");
    return roll;
  };
  const takeBotch = (): number => {
    if (botchIndex >= botchResults.length) {
      throw new RangeError("Not enough supplied botch rolls.");
    }
    const roll = botchResults[botchIndex++];
    dieFace(roll, "Botch die roll");
    return roll;
  };

  const initial = takeSequence();
  const trace: DieTraceEntry[] = [
    { kind: "stress_initial", roll: initial, value: initial, multiplier: 1 },
  ];

  if (initial === 0) {
    const warnings: string[] = [];
    if (!canBotch || botchDice === 0) {
      if (!canBotch) warnings.push("This stress roll was marked as unable to botch.");
      if (botchDice === 0) warnings.push("No botch dice were supplied, so roll cannot botch.");
      return {
        ...audit(
          0,
          [{ label: "Stress die", value: 0, citation: RULE_CITATIONS.dice }],
          ["Initial stress die 0 produces zero when no botch check applies."],
          warnings,
          [RULE_CITATIONS.dice],
        ),
        botched: false,
        botchCount: 0,
        trace,
      };
    }

    let botchCount = 0;
    for (let index = 0; index < botchDice; index += 1) {
      const roll = takeBotch();
      if (roll === 0) botchCount += 1;
      trace.push({ kind: "botch", roll, value: roll, multiplier: 1 });
    }
    return {
      ...audit(
        0,
        [{ label: "Stress die", value: 0, citation: RULE_CITATIONS.dice }],
        [
          botchCount > 0
            ? `Initial 0 and ${botchCount} botch die result(s) of 0: botch.`
            : "Initial 0, but no botch die result was 0.",
        ],
        [],
        [RULE_CITATIONS.dice],
      ),
      botched: botchCount > 0,
      botchCount,
      trace,
    };
  }

  if (initial !== 1) {
    return {
      ...audit(
        initial,
        [{ label: "Stress die", value: initial, citation: RULE_CITATIONS.dice }],
        ["Stress die uses non-zero, non-one initial value."],
        [],
        [RULE_CITATIONS.dice],
      ),
      botched: false,
      botchCount: 0,
      trace,
    };
  }

  let multiplier = 2;
  while (true) {
    const roll = takeSequence();
    if (roll === 1) {
      trace.push({ kind: "stress_reroll", roll, value: 0, multiplier });
      multiplier *= 2;
      continue;
    }
    const rerollValue = roll === 0 ? 10 : roll;
    const value = rerollValue * multiplier;
    trace.push({ kind: "stress_reroll", roll, value, multiplier });
    return {
      ...audit(
        value,
        [{ label: "Stress die", value, citation: RULE_CITATIONS.dice }],
        [`Stress die exploded; final face ${rerollValue} multiplied by ${multiplier}.`],
        [],
        [RULE_CITATIONS.dice],
      ),
      botched: false,
      botchCount: 0,
      trace,
    };
  }
}

/** Calculate Characteristic + Ability + die against an Ease Factor. */
export function actionTotal(
  characteristic: number,
  ability: number,
  die: DieResult,
  easeFactor: number,
): ActionTotalResult {
  integer(characteristic, "Characteristic");
  integer(ability, "Ability");
  integer(easeFactor, "Ease Factor");
  const modifier = characteristic + ability;
  const value = die.botched ? Math.min(0, modifier) : modifier + die.value;
  const succeeds = !die.botched && value >= easeFactor;
  const outcome = die.botched ? "botch" : succeeds ? "success" : "failure";
  const warnings = die.botched
    ? ["Roll botched; storyguide decides consequences beyond capped total.", ...die.warnings]
    : [...die.warnings];

  return {
    ...audit(
      value,
      [
        { label: "Characteristic", value: characteristic, citation: RULE_CITATIONS.actionTotals },
        { label: "Ability", value: ability, citation: RULE_CITATIONS.actionTotals },
        { label: "Die", value: die.value, citation: RULE_CITATIONS.actionTotals },
      ],
      [
        die.botched
          ? `Botch caps total at min(0, Characteristic + Ability) = ${value}.`
          : `Compare action total ${value} with Ease Factor ${easeFactor}.`,
      ],
      warnings,
      [RULE_CITATIONS.actionTotals, ...die.citations],
    ),
    modifier,
    easeFactor,
    outcome,
    succeeds,
  };
}

/** Calculate Technique + Form + Stamina - Encumbrance + Aura Modifier. */
export function castingScore(
  technique: number,
  form: number,
  stamina: number,
  encumbrance: number = 0,
  auraModifier: number = 0,
): AuditResult {
  integer(technique, "Technique");
  integer(form, "Form");
  integer(stamina, "Stamina");
  integer(encumbrance, "Encumbrance");
  integer(auraModifier, "Aura Modifier");
  const value = technique + form + stamina - encumbrance + auraModifier;

  return audit(
    value,
    [
      { label: "Technique", value: technique, citation: RULE_CITATIONS.castingScore },
      { label: "Form", value: form, citation: RULE_CITATIONS.castingScore },
      { label: "Stamina", value: stamina, citation: RULE_CITATIONS.castingScore },
      { label: "Encumbrance", value: -encumbrance, citation: RULE_CITATIONS.castingScore },
      { label: "Aura Modifier", value: auraModifier, citation: RULE_CITATIONS.castingScore },
    ],
    ["Casting Score = Technique + Form + Stamina - Encumbrance + Aura Modifier."],
    [],
    [RULE_CITATIONS.castingScore],
  );
}

/** Resolve Formulaic casting success and fatigue from a casting score and die. */
export function formulaicCasting(
  castingScoreTotal: number,
  die: DieResult,
  spellLevel: number,
): FormulaicCastingResult {
  integer(castingScoreTotal, "Casting Score");
  integer(spellLevel, "Spell Level");
  const total = die.botched ? 0 : castingScoreTotal + die.value;
  const margin = total - spellLevel;
  let spellCast: boolean;
  let fatigueLevelsLost: number;
  let explanation: string;
  const warnings = [...die.warnings];

  if (die.botched) {
    spellCast = false;
    fatigueLevelsLost = 0;
    explanation =
      "Formulaic botch: Casting Total is treated as zero; consequences need Storyguide adjudication.";
    warnings.unshift("Formulaic casting botch sets the Casting Total to zero before other effects.");
    warnings.unshift("Formulaic botch consequences are not deterministic in this helper.");
  } else if (margin >= 0) {
    spellCast = true;
    fatigueLevelsLost = 0;
    explanation = "Casting Total meets or exceeds spell level: spell succeeds without Fatigue.";
  } else if (margin >= -10) {
    spellCast = true;
    fatigueLevelsLost = 1;
    explanation = "Casting Total is within 10 below spell level: spell succeeds and loses one Fatigue level.";
  } else {
    spellCast = false;
    fatigueLevelsLost = 1;
    explanation = "Casting Total is more than 10 below spell level: spell fails and loses one Fatigue level.";
  }

  return {
    ...audit(
      total,
      [
        { label: "Casting Score", value: castingScoreTotal, citation: RULE_CITATIONS.formulaicCasting },
        { label: "Die Roll", value: die.value, citation: RULE_CITATIONS.formulaicCasting },
        { label: "Spell Level", value: -spellLevel, citation: RULE_CITATIONS.formulaicCasting },
      ],
      [explanation],
      warnings,
      [
        ...(die.botched ? [RULE_CITATIONS.castingBotch] : []),
        RULE_CITATIONS.formulaicCasting,
        ...die.citations,
      ],
    ),
    total,
    margin,
    spellCast,
    fatigueLevelsLost,
    botched: die.botched,
    botchCount: die.botchCount,
  };
}

/** Calculate Penetration Total and optionally compare Magic Resistance. */
export function penetrationTotal(
  castingTotal: number,
  spellLevel: number,
  penetrationBonusTotal: number,
  magicResistance: number | null = null,
  forceless: boolean = false,
): PenetrationTotalResult {
  integer(castingTotal, "Casting Total");
  integer(spellLevel, "Spell Level");
  integer(penetrationBonusTotal, "Penetration Bonus");
  if (magicResistance !== null) integer(magicResistance, "Magic Resistance");

  const rawTotal = castingTotal + penetrationBonusTotal - spellLevel;
  const capped = forceless && rawTotal > 0;
  const total = capped ? 0 : rawTotal;
  const penetrates = magicResistance === null ? null : total > magicResistance;
  const citations: RuleCitation[] = [RULE_CITATIONS.penetration];
  const warnings: string[] = [];
  if (capped) {
    citations.push(RULE_CITATIONS.forceless);
    warnings.push("Forceless casting caps Penetration Total at 0 by caller choice.");
  }

  return {
    ...audit(
      total,
      [
        { label: "Casting Total", value: castingTotal, citation: RULE_CITATIONS.penetration },
        { label: "Penetration Bonus", value: penetrationBonusTotal, citation: RULE_CITATIONS.penetration },
        { label: "Spell Level", value: -spellLevel, citation: RULE_CITATIONS.penetration },
      ],
      [
        capped
          ? "Forceless cap applies after calculating raw Penetration Total."
          : "Penetration Total = Casting Total + Penetration Bonus - Spell Level.",
        magicResistance === null
          ? "No Magic Resistance supplied; penetration comparison omitted."
          : total > magicResistance
            ? `Penetration Total ${total} exceeds Magic Resistance ${magicResistance}.`
            : `Penetration Total ${total} does not exceed Magic Resistance ${magicResistance}.`,
      ],
      warnings,
      citations,
    ),
    total,
    penetrates,
  };
}
