# Contributing to Claude CEO-Suite Plugin

Thanks for your interest in improving this plugin.

## Current release focus: v1.4 / v1.5 — Feature Freeze

**v1.4 ("Consistency Pass")** and **v1.5 ("Maintainability Pass")** are
**feature-freeze releases**. During this period:

- ❌ **No new role commands** will be added (no CHRO, CTOO, CRO, etc.)
- ✅ **Maintainer utility commands** (e.g., `/audit`) may be added if
  they support governance, conformance, or release workflows. These
  are exempt from role-specific conventions.
- ✅ **Router commands** (e.g., `/ask`) that dispatch to existing roles
  without introducing a new perspective may be added. They satisfy
  nearly all role conventions but have no Review Mode by design — see
  `AUDIT.md` for the router conformance subset.
- ✅ Bug fixes, documentation improvements, governance/compliance work,
  and internal refactors are welcome
- ✅ Cross-reference graph adjustments to existing roles are welcome

New role proposals will be re-opened for discussion in **v1.6** once
the existing 13 roles have stabilized.

Why this freeze: the plugin scaled rapidly from 6 to 13 roles, and the
current focus is on consolidating consistency, governance, and
maintainability before adding more surface area.

## Development workflow

This plugin is pure markdown — no build step, no tests to run, no
dependencies to install. To contribute:

1. Fork the repository
2. Make your changes to files under `commands/`, `README.md`, or the
   `.claude-plugin/` metadata
3. Test the affected commands locally with your installed Claude Code
4. Open a pull request against `main`

## Style guide for command files

When editing or adding to a command file, please match the existing
conventions:

### Required sections (in order)

1. **Frontmatter** — `description` and `arguments` block
2. **`## Trust boundary`** — keep verbatim across all commands
3. **`## Mode detection`** (or `## Role` for `/ceo`)
4. **`## Question Mode`** — handles natural-language questions
5. **`## Review Mode`** — handles scope-keyword reviews
6. **Cross-reference section** — references peer CxOs and the PhD Panel
7. **Footer** — the `## Do NOT execute...` line and the AI disclaimer

### Argument convention

All commands accept a single optional `input` argument that is either:

- A natural-language question (routes to Question Mode)
- A scope keyword like `full`, `deps`, `auth` (routes to Review Mode)
- Empty (defaults to `full`)

Commands must **not** accept `owner/repo` style arguments — they always
operate on the current working directory's repository.

### Cross-reference graph

Each role declares exactly **3 primary collaborators** (its "Top 3").
If you change a role's Top 3, update the matrix in `README.md` and the
edges referenced in `commands/ceo.md`.

## Reporting bugs

Open an issue at https://github.com/gaebalai/claude-ceo-suite-plugin/issues
with:

- Which command was affected
- The exact arguments you used
- The unexpected behavior
- Your Claude Code version and the model you were running

For security-related reports, see [SECURITY.md](./SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed
under the project's [MIT License](./LICENSE).
