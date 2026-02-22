---
name: gifgrep
description: "Search GIF providers (Tenor/Giphy) with CLI/TUI, download results, and extract stills/sheets."
keywords: [gif, tenor, giphy, media, image]
metadata:
  openclaw:
    emoji: "🧲"
    requires:
      bins: ["gifgrep"]
    install:
      - id: brew
        kind: brew
        formula: steipete/tap/gifgrep
        bins: ["gifgrep"]
        label: "Install gifgrep (brew)"
      - id: go
        kind: go
        module: github.com/steipete/gifgrep/cmd/gifgrep@latest
        bins: ["gifgrep"]
        label: "Install gifgrep (go)"
---

# gifgrep

Search GIF providers, browse in TUI, download results, extract stills or sheets.

## Quick start

```bash
gifgrep cats --max 5
gifgrep cats --format url | head -n 5
gifgrep search --json cats | jq '.[0].url'
gifgrep tui "office handshake"
gifgrep cats --download --max 1 --format url
```

## TUI + previews

```bash
gifgrep tui "query"    # Interactive TUI
gifgrep cats --thumbs  # Still frame previews (Kitty/Ghostty only)
```

## Download + reveal

```bash
gifgrep query --download --max 1     # Saves to ~/Downloads
gifgrep query --reveal               # Show last download in Finder
```

## Extract stills/sheets

```bash
gifgrep still ./clip.gif --at 1.5s -o still.png
gifgrep sheet ./clip.gif --frames 9 --cols 3 -o sheet.png
```

Sheets = single PNG grid of sampled frames (great for docs, PRs, chat).

Options:
- `--frames` (count)
- `--cols` (grid width)
- `--padding` (spacing)

## Providers

```bash
--source auto|tenor|giphy
```

- `GIPHY_API_KEY` required for `--source giphy`
- `TENOR_API_KEY` optional (demo key used if unset)

## Output formats

```bash
--json   # Array with id, title, url, preview_url, tags, width, height
--format url  # Pipe-friendly (url, title, preview_url)
```

## Environment

```bash
GIFGREP_SOFTWARE_ANIM=1   # Force software animation
GIFGREP_CELL_ASPECT=0.5   # Tweak preview geometry
```
