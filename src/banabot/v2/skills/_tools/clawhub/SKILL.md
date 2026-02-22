---
name: clawhub
description: "Use the ClawHub CLI to search, install, update, and publish agent skills from clawhub.com."
keywords: [clawhub, skill, install, publish, registry]
metadata:
  openclaw:
    requires:
      bins: ["clawhub"]
    install:
      - id: node
        kind: node
        package: clawhub
        bins: ["clawhub"]
        label: "Install ClawHub CLI (npm)"
---

# ClawHub CLI

Install:

```bash
npm i -g clawhub
```

Auth (publish):

```bash
clawhub login
clawhub whoami
```

Search:

```bash
clawhub search "postgres backups"
```

Install:

```bash
# Run from your workspace ROOT (where skills/ folder is)
cd ~/.banabot/workspace

# Install skill to current directory (NOT to skills/ subfolder)
clawhub install my-skill --dir .
clawhub install my-skill --dir . --version 1.2.3

# Alternative: use environment variable
CLAWHUB_WORKDIR=. clawhub install my-skill
```

Update (hash-based match + upgrade):

```bash
clawhub update my-skill
clawhub update my-skill --version 1.2.3
clawhub update --all
clawhub update my-skill --force
clawhub update --all --no-input --force
```

List:

```bash
clawhub list
```

Publish:

```bash
clawhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.2.0 --changelog "Fixes + docs"
```

Notes:

- Default registry: https://clawhub.com (override with CLAWHUB_REGISTRY or --registry)
- **IMPORTANT**: Always run from workspace ROOT, NOT from skills/ folder
- Use `--dir .` to install to current directory (NOT ./skills subfolder)
- Default workdir: cwd (falls back to workspace); install dir: ./skills
- Override with: --dir . or CLAWHUB_WORKDIR=.
- Update command hashes local files, resolves matching version, and upgrades to latest unless --version is set
