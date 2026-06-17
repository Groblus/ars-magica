# Wizard-study integration handover

## Context

This work belongs inside the existing `Groblus/ars-magica` repository. The repository already contains static GitHub Pages under `docs/`, reviewed Ars Magica source material under `reviewed/`, Agent Skills under `skills/`, structured browser data in `docs/data/core-data.json`, and a local MCP server under `mcp/`.

The wizard study is an experimental browser surface and future character-builder UI. It is not a standalone repository and is not currently a new Agent Skill.

## Product intent

Create a browser experience that feels like stepping into a warm medieval painting: a magus's tower study, sunlit French landscape, writing desk, unfinished manuscript, quill, bread, and recently abandoned tea.

The painting should remain the dominant visual source. The target is a projection/reconstruction hybrid, not a conventional game environment assembled from low-poly assets.

## Integration layout

```text
Groblus/ars-magica/
├── AGENTS.md
├── reviewed/
├── skills/
├── mcp/
├── docs/
│   ├── index.html
│   ├── data/core-data.json
│   ├── design/wizard-study-handover.md
│   └── sanctum/
└── experiments/
    └── wizard-study/
        ├── AGENTS.md
        ├── README.md
        ├── generation/
        ├── reconstruction/
        ├── scripts/
        └── web/
```

## Architecture

1. Use one canonical generated painting as the visual source of truth.
2. Generate a controlled set of nearby viewpoints with explicit yaw, elevation, and distance metadata.
3. Review and approve consistent views before reconstruction.
4. Reconstruct the approved set using COLMAP/Nerfstudio or another multiview pipeline.
5. Render the resulting Gaussian splat in Three.js using Spark.
6. Add real Three.js meshes only for interactive objects such as the manuscript, quill, candles, and tea.
7. Keep camera movement constrained to preserve the illusion.
8. Reuse `docs/data/core-data.json` and the workflow in `skills/ars-magica-character-helper/SKILL.md` when character-building functionality is added.

## Current prototype scope

The experiment provides:

- controlled multiview image-generation tooling with a no-network dry-run mode;
- a resumable manifest recording planned camera views, prompts, filenames, references, status, and review state;
- candidate, approved, and rejected image lanes;
- an approval-only reconstruction input preparation script;
- a Three.js painting-fallback viewer with constrained parallax, hotspot focus points, and a placeholder manuscript panel;
- a GitHub Pages-aware Vite build targeting `/ars-magica/sanctum/`.

The canonical painting itself is intentionally not committed in this draft. Place it at:

```text
experiments/wizard-study/generation/hero.jpg
experiments/wizard-study/web/public/reference/hero.jpg
```

The viewer includes a lightweight SVG placeholder until the painting is supplied.

## First Codex milestone

1. Read the root `AGENTS.md`, this handover, and `experiments/wizard-study/AGENTS.md`.
2. Inspect `docs/index.html`, `docs/data/core-data.json`, and `skills/ars-magica-character-helper/SKILL.md`.
3. Run the experiment checks before editing.
4. Make generation planning pure and testable.
5. Add a `--dry-run` mode that requires no API key and performs no network calls.
6. Preserve existing manifest records when resuming.
7. Separate candidate, approved, and rejected views.
8. Ensure only approved views can feed reconstruction or neighbour references.
9. Add tests for ordering, filenames, prompts, neighbour selection, and manifest merging.
10. Run the GitHub Pages build into `docs/sanctum/`.
11. Add a restrained link from `docs/index.html` to `./sanctum/`.

## Acceptance criteria

- Existing corpus, skills, MCP tooling, and root instructions remain intact.
- Dry-run works without `.env` or API access.
- Existing manifest history survives resume.
- Reconstruction input is approval-only.
- Python and TypeScript checks pass.
- `docs/sanctum/index.html` is generated with `/ars-magica/sanctum/` asset paths.
- No paid image request or GPU-heavy reconstruction job runs during integration.

## WSL workflow

```bash
cd ~/src/ars-magica
git switch feat/wizard-study-sanctum
cd experiments/wizard-study
./scripts/bootstrap-wsl.sh
./scripts/check.sh
cd ../..
codex
```

Start Codex from the existing repository root so both root and nested `AGENTS.md` files apply.
