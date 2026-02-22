---
name: obsidian
description: "Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli."
keywords: [obsidian, notes, vault, markdown, knowledge-base]
metadata:
  openclaw:
    emoji: "💎"
    requires:
      bins: ["obsidian-cli"]
    install:
      - id: brew
        kind: brew
        formula: yakitrak/yakitrak/obsidian-cli
        bins: ["obsidian-cli"]
        label: "Install obsidian-cli (brew)"
---

# Obsidian

Obsidian vault = a normal folder on disk.

## Vault structure (typical)

- Notes: `*.md` (plain text Markdown; edit with any editor)
- Config: `.obsidian/` (workspace + plugin settings)
- Canvases: `*.canvas` (JSON)
- Attachments: whatever folder you chose in Obsidian settings

## Find the active vault(s)

Obsidian desktop tracks vaults here:

- `~/Library/Application Support/obsidian/obsidian.json`

## Quick start

Set a default vault (once):
```bash
obsidian-cli set-default "<vault-folder-name>"
obsidian-cli print-default --path-only
```

## Search

```bash
obsidian-cli search "query"           # note names
obsidian-cli search-content "query"   # inside notes; shows snippets
```

## Create

```bash
obsidian-cli create "Folder/New note" --content "..." --open
```

## Move/rename

```bash
obsidian-cli move "old/path/note" "new/path/note"
```
Updates `[[wikilinks]]` and Markdown links across the vault.

## Delete

```bash
obsidian-cli delete "path/note"
```

## Tips

- Multiple vaults common (iCloud vs ~/Documents, work/personal)
- Don't guess; read `obsidian.json` for vault paths
- Prefer direct edits when appropriate: edit `.md` file directly
