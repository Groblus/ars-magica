# Wizard-study experiment

Experimental painterly Three.js environment for the existing Ars Magica Agentic Reference Lab.

This is not a standalone repository. Source lives under `experiments/wizard-study/`; a static production build can be published to repository-root `docs/sanctum/` for GitHub Pages.

## Architecture

```text
canonical painting
  -> controlled generated nearby views
  -> human approval
  -> COLMAP registration
  -> Nerfstudio Splatfacto
  -> Gaussian splat
  -> Three.js + Spark
       + real interactive objects
       + future Ars Magica character-builder UI
```

The painting remains the visual source of truth. Conventional 3D assets should be limited to interactive objects, animation, raycasting, collision, or occlusion.

## Safe local setup

```bash
npm --prefix web ci
./scripts/check.sh
npm --prefix web run dev
```

## GitHub Pages build

```bash
npm --prefix web run build
npm --prefix web run build:pages
```

The Pages build writes to repository-root `docs/sanctum/` and uses `/ars-magica/sanctum/` as its base path.

## Existing integration points

- Browser data: `../../docs/data/core-data.json`
- Character workflow: `../../skills/ars-magica-character-helper/SKILL.md`
- Corpus search and citation policy: `../../skills/ars-magica-corpus-navigator/`
- Local MCP server: `../../mcp/ars_magica_server.py`

GitHub Pages cannot directly call the local MCP server. The first character-builder iteration should use static JSON.

## Generate candidate views

Place the canonical painting at `generation/hero.jpg`, then run:

```bash
python generation/generate_views.py --dry-run --preset quick
```

Dry-run requires no `.env`, no API key, and performs no network calls. It writes `generation/output/manifest.json` with planned views, prompts, stable filenames, and `candidate` review state.

Paid generation is explicit-only. To actually generate candidate images, place `generation/hero.jpg`, provide `OPENAI_API_KEY`, and run without `--dry-run`:

```bash
python generation/generate_views.py --preset quick
```

Generated views go to `generation/output/candidates/`. Review them manually and set `review_state` to `approved` or `rejected` in the manifest. Only `source` and `approved` records are valid reconstruction inputs.

## Reconstruction

```bash
python generation/prepare_reconstruction_inputs.py --clean
```

This copies only approved/source images into `reconstruction/input/`. Future COLMAP/Nerfstudio or Gaussian splat jobs should read from that folder, not from candidates.

When a splat exists, copy the exported file to `web/public/scene/room.ply`, then configure:

```dotenv
VITE_SPLAT_URL=scene/room.ply
```

A future real manuscript model can be configured with:

```dotenv
VITE_BOOK_MODEL_URL=models/book.glb
```
