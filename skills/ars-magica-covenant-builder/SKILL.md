---
name: ars-magica-covenant-builder
description: Build Ars Magica Definitive Edition covenants. Use when choosing covenant concept, season, aura, site, Boons, Hooks, governance, resources, library, vis, labs, covenfolk, or first saga pressures with citations from core and Covenants.
---

# Ars Magica Covenant Builder

Use this skill for covenant creation and covenant-centered saga prep. It depends on `ars-magica-corpus-navigator`.

## Workflow

1. Establish saga tone, tribunal/region, covenant season, and group preferences.
2. Use Definitive Edition core for baseline covenant rules.
3. Use `Covenants` as the primary 5e support book.
4. Search structured data first:
   - `docs/data/core-data.json` bucket: `covenant_boons_hooks`.
   - `python3 skills/ars-magica-corpus-navigator/scripts/search.py "boons hooks covenant"`.
5. Build a covenant dossier:
   - premise, site, aura, mundane cover
   - Boons and Hooks
   - governance model
   - library, vis, wealth, labs, covenfolk
   - first 6 story pressures
6. Cite every rules-bearing recommendation.

## Guardrails

- Balance Boons with Hooks for player covenants unless the user asks for an NPC covenant.
- Prefer evocative story pressure over optimization.
- Do not use 3e/4e material except in a separate legacy conversion pass.
