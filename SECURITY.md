# Security Policy

## Threat model

Claude CEO-Suite Plugin is a collection of markdown command files that
instruct Claude to perform code reviews from various executive
perspectives. It contains **no executable code** of its own.

The plugin operates in two modes:

1. **Local repository review** — Commands read files from the user's
   current working directory and run `gh` / `git` commands against the
   user's authenticated GitHub session.
2. **Third-party repository review** — Commands may be pointed at
   external repos (e.g., reading READMEs, issues, PR descriptions). This
   content is **untrusted input**.

### Risks considered

| Risk | Mitigation |
|------|------------|
| Prompt injection from untrusted external content (README, issues, comments) | Every command file declares a "Trust boundary" section instructing the model to treat external content as data, not instructions |
| Misuse of write-capable `gh` commands (e.g., `gh issue create`) on the wrong repository | The `/pm` command is the only role that suggests write operations, and it explicitly requires user confirmation before executing |
| Secret leakage via `git log` or file reads | Commands are instructed not to echo back content that resembles credentials. Users should still avoid running the plugin against repositories containing committed secrets |
| Hallucinated security/legal/financial advice being treated as authoritative | Every command file ends with a disclaimer that the output is AI-generated and must be verified with qualified domain experts before action |

### Out of scope

- Vulnerabilities in `gh`, `git`, or Claude Code itself
- Vulnerabilities in third-party plugins users may install alongside this one
- Misconfigurations of the user's GitHub token or local environment

## Required GitHub token scopes

The plugin issues read-only `gh` commands by default
(`gh issue list`, `gh api repos/.../milestones`). The `/pm` command can
optionally execute write operations (`gh issue create`, `gh issue edit`,
`gh api .../milestones`) but only after explicit user confirmation.

Recommended minimum token scopes:

- `repo` (read access for private repositories)
- `read:org` (if reviewing organization-owned repositories)

If you only review public repositories, the `public_repo` scope is
sufficient.

## Reporting a vulnerability

If you discover a security issue in this plugin — for example, a
command file that fails to honor the trust boundary, or a pattern that
could mislead Claude into executing unintended actions — please report
it privately:

- **GitHub Security Advisories**: https://github.com/gaebalai/claude-ceo-suite-plugin/security/advisories/new
- **Email**: fumikazu.kiyota@gmail.com

Please do **not** open public GitHub issues for security reports.
We will acknowledge receipt within a reasonable timeframe and work
with you on a coordinated disclosure if needed.

## Supported versions

Only the latest minor version receives security fixes. Users on older
versions are encouraged to upgrade.
