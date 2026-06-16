# Wizard-study experiment instructions

This file applies only within `experiments/wizard-study/`. The repository-root `AGENTS.md` remains authoritative for the Ars Magica corpus, edition policy, citations, skills, generated reference data, and MCP tooling.

## Mission

Develop the painterly wizard-study environment as an experimental browser surface for the existing Ars Magica Agentic Reference Lab. It should eventually become a character-creation interface, while preserving the supplied painting as the visual source of truth.

## Repository integration boundaries

- Keep source code, image-generation tooling, reconstruction scripts, and local outputs inside `experiments/wizard-study/`.
- Publish only the static web build to `docs/sanctum/`, because the repository already serves GitHub Pages from `docs/`.
- Do not overwrite or replace the root `AGENTS.md`, `README.md`, `skills.sh.json`, `reviewed/`, `skills/`, `mcp/`, or existing `docs/` pages.
- Do not create a new Agent Skill merely for rendering or asset generation.
- Reuse `docs/data/core-data.json`, `skills/ars-magica-character-helper/`, and `skills/ars-magica-corpus-navigator/` rather than creating a parallel rules corpus.
- GitHub Pages is static. Prefer static JSON for the first browser integration.

## Visual architecture

1. Preserve `generation/hero.jpg` as the canonical painting.
2. Generate nearby, geometrically consistent views only through explicit commands.
3. Curate views before reconstruction.
4. Reconstruct an optional Gaussian splat.
5. Render with Three.js and Spark.
6. Use ordinary meshes or DOM only for interactive elements.
7. Keep camera motion constrained.

## Hard constraints

- Never make paid image-generation calls unless Oliver explicitly requests them in the current session.
- Never start Nerfstudio or another long GPU job unless explicitly requested.
- Never commit `.env`, keys, candidate generations, training outputs, splat exports, `node_modules`, or local build output.
- Avoid cheerful low-poly, cartoon, generic fantasy, or Elder Scrolls visual language.
- Preserve room identity between generated views.
- Keep LF line endings.

## Web conventions

- Source app: `experiments/wizard-study/web/`.
- `npm run build` creates `web/dist/`.
- `npm run build:pages` publishes to `docs/sanctum/` with base path `/ars-magica/sanctum/`.
- Resolve assets through `import.meta.env.BASE_URL`.
- Preserve the painting fallback.
- Keep TypeScript strict.

## Validation

```bash
./scripts/check.sh
npm --prefix web run build:pages
```

## Current bounded milestone

1. Integrate this experiment without disrupting existing pages or skills.
2. Make image generation dry-runnable, resumable, and approval-aware without API calls.
3. Add focused Python tests.
4. Build a static painting-fallback page into `docs/sanctum/`.
5. Add a restrained link from `docs/index.html` to `./sanctum/`.
6. Do not run paid generation or reconstruction.
