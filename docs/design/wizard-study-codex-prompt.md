# Initial Codex prompt

```text
This is an integration task inside the existing Groblus/ars-magica repository, not a standalone project.

Read, in order:
1. repository-root AGENTS.md;
2. docs/design/wizard-study-handover.md;
3. experiments/wizard-study/AGENTS.md;
4. experiments/wizard-study/README.md;
5. skills/ars-magica-character-helper/SKILL.md;
6. the relevant parts of docs/index.html and docs/data/core-data.json.

Work only on the first milestone in docs/design/wizard-study-handover.md.

Important boundaries:
- do not overwrite the root AGENTS.md or README.md;
- do not reorganize reviewed/, skills/, mcp/, or existing docs pages;
- do not create a new Agent Skill for the renderer;
- do not make OpenAI API calls;
- do not run COLMAP, Nerfstudio, or GPU-heavy tooling;
- do not initialize a new repository;
- keep the browser deployment static and compatible with GitHub Pages at /ars-magica/sanctum/.

First inspect the repository and run existing checks. Then:
- make generation dry-runnable, resumable, and approval-aware;
- add focused tests;
- build the painting-fallback viewer into docs/sanctum/;
- add a restrained link from docs/index.html;
- preserve existing functionality and visual language.

At the end report:
1. files changed;
2. behavior added;
3. exact commands and tests run;
4. whether docs/sanctum/ was generated successfully;
5. any assumptions or unresolved integration risks.
```
