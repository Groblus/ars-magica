import { describe, expect, it } from "vitest";

import {
  CHARACTER_SCHEMA_ID,
  createDefaultDraft,
  exportCharacterArtifactSpec,
  exportCharacterJson,
  parseCharacterDraft,
  validateCharacterDraft,
} from "./character";

describe("character draft model", () => {
  it("parses an untouched default draft without normalization", () => {
    const draft = createDefaultDraft();
    const parsed = parseCharacterDraft(draft);

    expect(parsed.changed).toBe(false);
    expect(parsed.draft).toEqual(draft);
  });

  it("allows the seven-point characteristic budget", () => {
    const base = createDefaultDraft("companion");
    const draft = createDefaultDraft("companion", {
      characteristics: {
        ...base.characteristics,
        intelligence: 3,
        perception: 1,
      },
    });
    const validation = validateCharacterDraft(draft);

    expect(validation.totals.characteristicPoints).toBe(7);
    expect(validation.errors.map((issue) => issue.code)).not.toContain(
      "characteristics.budget.exceeded",
    );
  });

  it("requires a House for a magus", () => {
    const validation = validateCharacterDraft(createDefaultDraft("magus"));

    expect(validation.errors.map((issue) => issue.code)).toContain("magus.house.required");
  });

  it("requires virtues and flaws to balance", () => {
    const validation = validateCharacterDraft(
      createDefaultDraft("companion", { virtues: ["book-learner"], flaws: [] }),
    );

    expect(validation.totals).toMatchObject({ virtuePoints: 1, flawPoints: 0 });
    expect(validation.errors.map((issue) => issue.code)).toContain("virtuesFlaws.balance");
  });

  it("rejects forbidden grog choices", () => {
    const validation = validateCharacterDraft(
      createDefaultDraft("grog", { virtues: ["the-gift"], flaws: ["enemy"] }),
    );
    const codes = validation.errors.map((issue) => issue.code);

    expect(codes).toContain("grog.gift.forbidden");
    expect(codes).toContain("grog.storyFlaw.forbidden");
  });

  it("exports definitive citations and renderable publishing artifact data", () => {
    const draft = createDefaultDraft("companion", {
      name: "Aelia",
      concept: "Covenant envoy",
      abilityXp: { charm: 10 },
    });
    const json = exportCharacterJson(draft, { exportedAt: "1220-01-01T00:00:00.000Z" });
    const artifact = exportCharacterArtifactSpec(draft, { audience: "player", paper: "a4" });

    expect(json).toMatchObject({
      schema: CHARACTER_SCHEMA_ID,
      version: 1,
      kind: "character-draft",
      exportedAt: "1220-01-01T00:00:00.000Z",
      data: draft,
    });
    expect(json.sourceRefs).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          title: "Ars Magica - Definitive Edition (Core Rules)",
          citation: expect.stringMatching(
            /^reviewed\/Ars Magica - Definitive Edition \(Core Rules\)\.md:\d+(?:-\d+)?$/,
          ),
        }),
      ]),
    );
    expect(artifact).toMatchObject({
      template: "companion-grog-sheet",
      theme: "clear-ledger",
      preset: "home-a4",
      audience: "player",
      content: {
        identity: { name: "Aelia", role: "Companion" },
        characteristics: draft.characteristics,
        abilities: [expect.objectContaining({ name: "Charm", notes: "10 XP allocated in this draft" })],
      },
    });
    expect(artifact.source_references.length).toBeGreaterThan(0);
    expect(artifact.source_references).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          citation: expect.stringMatching(
            /^reviewed\/Ars Magica - Definitive Edition \(Core Rules\)\.md:\d+(?:-\d+)?$/,
          ),
        }),
      ]),
    );
  });
});
