# Worklog

## 2026-06-07
- Scope: Fork and clone pokeemerald-wasm locally, get `make wasm` building on
  macOS, verify the browser game runs in Chrome, confirm/explain save-state
  persistence, and add a one-click launcher.
- Changes:
  - `Makefile` — added a prerequisite rule so `make wasm` generates the
    per-map header/event/connection includes it needs (commit `ad0992b4b`)
  - `CLAUDE.md` — new project agent-instructions file (commits `c4c3aae46`,
    `53c29e25b`)
  - `launch_game.command` — new double-click launcher that builds, serves,
    and opens the game in a Chrome app window (commit `53c29e25b`)
  - `docs/HANDOFF.md`, `docs/WORKLOG.md`, `docs/DECISIONS.md` — created
  - `~/.claude/CLAUDE.md` (outside this repo) — added a Claude-in-Chrome MCP →
    Playwright MCP fallback note
- Verification:
  - `make wasm` -> succeeded, produced `build/wasm/pokeemerald.wasm`
  - `node web/server.mjs` + Playwright MCP -> game boots through the intro to
    the title screen and overworld, runs at ~60 FPS
  - marker-byte write -> `pagehide` flush -> reload -> restore test via
    Playwright -> confirmed `localStorage['pokeemerald.wasm.flash.v1']` save
    persistence already works as-is
  - `./launch_game.command` -> server + Chrome app-mode window launched
    correctly (verified via `ps aux`)
- Follow-ups:
  - none blocking; see `docs/HANDOFF.md` Open Risks for minor caveats
