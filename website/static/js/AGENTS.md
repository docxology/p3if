# AGENTS.md — `website/static/js/`

`main.js`, the portal's hand-maintained browser script, served directly by Flask —
no bundler, no module build step.

- Edits take effect on reload; nothing regenerates this file, and it is unrelated to
  the generated `portal.js` under the repository's `assets/` folders.
- No test executes it. There is no browser test in this repository and CI never starts
  the server, so a JavaScript error is not caught by the gate.

Application guide: [`../AGENTS.md`](../AGENTS.md).
