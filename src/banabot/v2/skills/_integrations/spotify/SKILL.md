---
name: spotify
description: "Terminal Spotify playback/search via spogo (macOS only)."
keywords:
  [spotify, music, player, playback, musica, reproduccion, cancion, artista]
metadata:
  openclaw:
    emoji: "🎵"
    os: [darwin]
    requires:
      anyBins: ["spogo", "spotify_player"]
    install:
      - id: brew
        kind: brew
        formula: spogo
        tap: steipete/tap
        bins: ["spogo"]
        label: "Install spogo (brew) - macOS only"
      - id: brew
        kind: brew
        formula: spotify_player
        bins: ["spotify_player"]
        label: "Install spotify_player (brew) - macOS only"
---

# Spotify (spogo / spotify_player)

Use `spogo` **(preferred)** for Spotify playback/search. Fall back to `spotify_player` if needed.

## Requirements

- Spotify Premium account
- Either `spogo` or `spotify_player` installed

## Setup

Import cookies from browser:

```bash
spogo auth import --browser chrome
```

## Common commands (spogo)

```bash
# Search
spogo search track "query"

# Playback
spogo play
spogo pause
spogo next
spogo prev

# Devices
spogo device list
spogo device set "<name|id>"

# Status
spogo status
```

## Commands (spotify_player fallback)

```bash
spotify_player search "query"
spotify_player playback play|pause|next|previous
spotify_player connect
spotify_player like
```

## Notes

- Config folder: `~/.config/spotify-player`
- For Spotify Connect, set `client_id` in config
- TUI shortcuts available via `?`
