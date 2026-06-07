# Handoff

Last updated: 2026-06-07

## Current Objective
Run the pokeemerald-wasm browser game locally on macOS/Chrome from a personal
fork, with persistent save state and a one-click launcher.

## Current State
- Forked to `yannickspiess/pokeemerald-wasm`; cloned to
  `~/Documents/daily app/pokeemerald-wasm` (`origin` = fork, `upstream` =
  `tripplyons/pokeemerald-wasm`).
- Local toolchain installed: `llvm` + `lld` (Homebrew) provide the wasm-capable
  clang and `wasm-ld` that `make wasm` needs on macOS — no env var overrides
  required, both resolve via `/opt/homebrew/bin` / `/opt/homebrew/opt/llvm/bin`.
- Fixed a build-system gap: `make wasm` failed on a clean checkout because the
  WASM data-asm rule for `maps.s`/`map_events.s` lacked prerequisites on the
  per-map `header.inc`/`events.inc`/`connections.inc` files (generated via
  `mapjson`). Fixed in `Makefile` (commit `ad0992b4b`).
- `make wasm` now builds successfully → `build/wasm/pokeemerald.wasm`
  (~12.2 MB, gitignored).
- Save-state persistence verified as already implemented: the app mirrors the
  in-game cartridge flash/SRAM (128 KB) to `localStorage` under
  `pokeemerald.wasm.flash.v1`, flushing on `beforeunload`/`pagehide`/hidden
  visibility, and restoring on load. No new work needed here — confirmed
  end-to-end with a write → forced-flush → reload → restore test.
- Added `launch_game.command` — a double-clickable launcher that builds if
  needed, starts `web/server.mjs` on port 8000, and opens the game in a
  chromeless Chrome app window (`chrome --app=http://localhost:8000`).
- Added project `CLAUDE.md` (operating rules, build commands, toolchain notes,
  Claude-in-Chrome→Playwright fallback note).
- Added the same Claude-in-Chrome→Playwright fallback note to the user's
  global `~/.claude/CLAUDE.md` (outside this repo, applies to all projects).

## Validation
- Commands run:
  - `brew install llvm lld`
  - `make wasm` — first run failed (`data/maps/PetalburgCity/header.inc`
    missing); succeeded after the Makefile fix
  - `node web/server.mjs` (port 8123, then 8000 via the launcher)
  - Playwright MCP: navigated to the served page, screenshotted the Game Freak
    intro and title screen, confirmed ~60 game FPS / 1.0x speed
  - Playwright MCP: wrote marker bytes `0xAB`/`0xCD` into emulated flash
    memory, dispatched `pagehide`, confirmed `localStorage` key
    `pokeemerald.wasm.flash.v1` populated (174,764 base64 chars), reloaded,
    confirmed bytes restored (`171, 205`) — proves save persistence works
  - `./launch_game.command` — server started, Chrome opened in
    `--app=http://localhost:8000` mode (verified via `ps aux`)
- Results: all passed. Test save data was cleared
  (`localStorage.removeItem('pokeemerald.wasm.flash.v1')`) and temporary
  server/Chrome processes were stopped afterward, leaving a clean state.

## Open Risks
- If Chrome's "clear cookies and site data when you close all windows" setting
  is ever turned on, the saved game in `localStorage` would be wiped on
  restart — not something to change without asking the user first.
- `make wasm` is a long build (~10+ minutes on this machine). The launcher
  runs it automatically when `build/wasm/pokeemerald.wasm` is missing, which
  could surprise someone expecting an instant launch the very first time.

## Next Steps
1. None required for the original ask — fork/clone, local build, save-state
   verification, and the one-click launcher are complete and pushed to
   `origin/master`.
2. If gameplay/runtime bugs surface later, see `AGENTS.md` for the headless
   replay/verification tool (`tools/wasm_replay.mjs`).
3. Periodically `git fetch upstream` and consider merging/rebasing upstream
   improvements into the fork if desired.
