# AGENTS.md — `website/templates/visualizations/type/`

One page per visualization type: `cube.html`, `matrix.html`, and `network.html`. Each
lays out a single view for `../show.html` to use.

- The page names are the type's name; a new visualization type needs a template here
  and the matching name in the route that renders it, or the detail page has nothing to
  show.
- No test renders these templates; verify in a browser after editing.

Parent: [`../AGENTS.md`](../AGENTS.md).
