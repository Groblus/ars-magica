import { describe, expect, it } from "vitest";

import { actionTotal, formulaicCasting, penetrationTotal, simpleDie, stressDie } from "./rules";

describe("rules teaching helpers", () => {
  it("treats a simple die raw 0 as 10", () => {
    expect(simpleDie(0)).toMatchObject({ value: 10, botched: false });
  });

  it("doubles a stress die after an explosion", () => {
    expect(stressDie([1, 5])).toMatchObject({ value: 10, botched: false });
  });

  it("caps a botched action total at zero or its negative modifier", () => {
    const botch = stressDie([0], 1, [0]);

    expect(actionTotal(2, 3, botch, 0)).toMatchObject({
      value: 0,
      outcome: "botch",
      succeeds: false,
    });
  });

  it("compares an action total against its Ease Factor", () => {
    const die = simpleDie(5);

    expect(actionTotal(1, 2, die, 8)).toMatchObject({ outcome: "success", succeeds: true });
    expect(actionTotal(1, 2, die, 9)).toMatchObject({ outcome: "failure", succeeds: false });
  });

  it("applies Formulaic casting fatigue thresholds", () => {
    const die = simpleDie(5);

    expect(formulaicCasting(10, die, 15)).toMatchObject({
      spellCast: true,
      fatigueLevelsLost: 0,
    });
    expect(formulaicCasting(10, die, 16)).toMatchObject({
      spellCast: true,
      fatigueLevelsLost: 1,
    });
    expect(formulaicCasting(10, die, 26)).toMatchObject({
      spellCast: false,
      fatigueLevelsLost: 1,
    });
  });

  it("treats Formulaic botch Casting Total as zero for positive and negative Casting Score", () => {
    const botch = stressDie([0], 1, [0]);

    for (const result of [formulaicCasting(20, botch, 5), formulaicCasting(-5, botch, 5)]) {
      expect(result).toMatchObject({
        total: 0,
        margin: -5,
        spellCast: false,
        fatigueLevelsLost: 0,
        botched: true,
        botchCount: 1,
      });
      expect(result.citations).toContain(
        "reviewed/Ars Magica - Definitive Edition (Core Rules).md:9093-9093",
      );
    }
  });

  it("requires Penetration Total to strictly exceed Magic Resistance", () => {
    expect(penetrationTotal(20, 10, 0, 10).penetrates).toBe(false);
    expect(penetrationTotal(20, 10, 0, 9).penetrates).toBe(true);
  });
});
