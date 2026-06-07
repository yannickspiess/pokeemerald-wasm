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

## 2026-06-07 (session 2)
- Scope: Add speed-preset hotkeys, a keystroke-loop record/playback feature,
  trim the page header for more game space, and fix a battle-animation crash
  the user hit while using the new loop feature.
- Changes:
  - `web/app.js`, `web/index.html` — added `1`-`6` speed-preset hotkeys
    (1x/5x/10x/25x/1000x/unlimited) with an on-screen legend under the speed
    slider (commit `d4bd6cbed`)
  - `web/app.js`, `web/index.html`, `web/style.css` — added `Q`/`W` keystroke
    loop recording/playback (mutually exclusive, with a live status line and
    help text), and removed the "pokeemerald-wasm" title + GitHub link header
    plus its now-unused CSS (commit `405389f15`)
  - `src/battle_anim.c` — added a `#if WASM` bounds check in
    `RunAnimScriptCommand` (line ~330) so an out-of-range animation-script
    command byte ends the script gracefully (`Cmd_end`) instead of trapping
    with `RuntimeError: table index is out of bounds` (commit `de8a0162e`)
  - `docs/HANDOFF.md`, `docs/WORKLOG.md` — refreshed for this session
- Verification:
  - Playwright MCP -> confirmed speed-preset hotkeys 1-6 set `#speed-value`
    correctly; confirmed `Q`/`W` toggle recording/playback and `#loop-status`
    updates; confirmed `h1`/`.github-link` removed from the DOM
  - User reported the original crash: `RuntimeError: table index is out of
    bounds at pokeemerald.wasm.RunAnimScriptCommand -> OpponentDoMoveAnimation
    -> BattleMainCB1 -> WasmRunFrame`, triggered while using the new keystroke
    loop to mash up/down/a repeatedly during a wild battle
  - `rm -f build/wasm/obj/battle_anim.o && make wasm` -> succeeded after the
    `battle_anim.c` fix (`build/wasm/pokeemerald.wasm`, 12,202,417 bytes)
  - User is independently re-testing the same mashing pattern against the
    rebuilt wasm to confirm the fix prevents the crash (not yet confirmed by
    the agent — see `docs/HANDOFF.md` Validation/Next Steps)
- Follow-ups:
  - Confirm with the user whether the `battle_anim.c` fix resolves the crash;
    if a *different* out-of-bounds table trap surfaces from another
    script-dispatch table, apply the same `#if WASM` bounds-check pattern
    there (see `docs/HANDOFF.md` Open Risks)
