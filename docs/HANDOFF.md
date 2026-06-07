# Handoff

Last updated: 2026-06-07

## Current Objective
Run the pokeemerald-wasm browser game locally on macOS/Chrome from a personal
fork, with persistent save state, a one-click launcher, and an increasingly
TAS-style control surface (speed presets, keystroke-loop recording/playback).

## Current State
- Forked to `yannickspiess/pokeemerald-wasm`; cloned to
  `~/Documents/daily app/pokeemerald-wasm` (`origin` = fork, `upstream` =
  `tripplyons/pokeemerald-wasm`). Branch `master`, all work pushed to
  `origin/master`. Latest commit: `de8a0162e`.
- Local toolchain: `llvm` + `lld` (Homebrew) provide the wasm-capable clang and
  `wasm-ld`; `make wasm` builds cleanly (~12.2 MB `build/wasm/pokeemerald.wasm`,
  gitignored, ~10 minute build).
- Save-state persistence verified working: mirrors cartridge flash/SRAM to
  `localStorage['pokeemerald.wasm.flash.v1']`, flushing on
  `beforeunload`/`pagehide`/hidden visibility.
- `launch_game.command` — double-click launcher that builds if needed, serves
  on port 8000, and opens a chromeless Chrome app window.
- **Speed presets** (`web/app.js`): pressing `1`–`6` jumps emulation speed
  directly to 1x/5x/10x/25x/1000x/unlimited via the existing
  `speedToExponent`/`setSpeedFromExponent` slider machinery. Legend shown under
  the speed slider in `web/index.html`.
- **Keystroke loop recording/playback** (`web/app.js`): `Q` toggles recording
  of button presses (with relative timing via `performance.now()`), `W` toggles
  looped playback of the recorded sequence via `setTimeout` scheduling.
  Recording and playback are mutually exclusive — starting one stops the other
  — to prevent played-back presses from being recorded into a new loop. A live
  status line (`#loop-status` in `web/index.html`) shows current state
  (idle/recording/ready/playing); a static help line explains the keys.
- **Header removed**: dropped the "pokeemerald-wasm" title + GitHub link from
  `web/index.html` (and the now-unused `.masthead`/`h1`/`.github-link` CSS from
  `web/style.css`) to free vertical space for the game display.
- **Battle-animation crash fix** (`src/battle_anim.c:326`, commit `de8a0162e`):
  added a `#if WASM`-guarded bounds check in `RunAnimScriptCommand` —
  `if (sBattleAnimScriptPtr[0] >= ARRAY_COUNT(sScriptCmdTable)) { Cmd_end(); return; }`
  before the `sScriptCmdTable[...]()` indirect call. Rapid scripted/looped
  input (e.g. mashing up/down/a in battle via the new keystroke-loop feature,
  especially at high speed) can leave `sBattleAnimScriptPtr` pointing at a
  garbage byte outside the command table. On real hardware that limps along by
  jumping to garbage; in WASM, function pointers are indirect-call-table
  indices, so an out-of-range one traps with `RuntimeError: table index is out
  of bounds` and halts the whole emulator. The guard converts that hard crash
  into a gracefully ended animation (`Cmd_end`) and never triggers during
  normal play.

## Validation
- Commands run this session:
  - `rm -f build/wasm/obj/battle_anim.o && make wasm` — succeeded
    (`build/wasm/pokeemerald.wasm`, 12,202,417 bytes, exit 0)
  - `node web/server.mjs` (port 8000) + Playwright MCP — confirmed:
    - Speed presets 1–6 set `#speed-value` to 1.0x/5.0x/10x/25x/1000x/unlimited
    - `Q` starts/stops loop recording (`#loop-status` updates, event count
      increments); `W` plays the loop on repeat and stops it
    - `h1`/`.github-link` are gone from the DOM after the header removal
- **Not yet independently re-verified by the agent**: whether the
  `battle_anim.c` bounds-check fix actually prevents the originally reported
  crash. The user is testing this themselves (mashing up/down/a in a wild
  battle via the keystroke loop, the same way the original crash occurred —
  screenshot showed `RuntimeError: table index is out of bounds at
  pokeemerald.wasm.RunAnimScriptCommand → OpponentDoMoveAnimation →
  BattleMainCB1 → WasmRunFrame`).

## Open Risks
- If Chrome's "clear cookies and site data when you close all windows" setting
  is ever turned on, the saved game in `localStorage` would be wiped on
  restart — not something to change without asking the user first.
- `make wasm` is a long build (~10 minutes). The launcher runs it automatically
  when `build/wasm/pokeemerald.wasm` is missing.
- The `battle_anim.c` fix addresses the *symptom* (the WASM trap) of an
  underlying "engine reached an inconsistent state from being mashed faster
  than human/hardware input rates allow" condition — the broken state itself
  can still occur; the fix just stops it from being a hard crash. If similar
  `table index is out of bounds` traps surface from *other* script-dispatch
  tables (e.g. field/overworld scripts, battle scripts proper in
  `battle_script_commands.c`, AI scripts), the same defensive-bounds-check
  pattern guarded by `#if WASM` is the template to follow — but each site
  should be verified independently rather than blanket-patched.

## Next Steps
1. User is testing whether the `battle_anim.c` fix (commit `de8a0162e`)
   actually prevents the crash when reproducing the original mashing pattern
   (up/down/up/down.../a/a/a... loop in a wild battle). If it crashes again
   with a *different* out-of-bounds table trap (different function/script
   table), apply the same `#if WASM` bounds-check pattern at that dispatch
   site.
2. Periodically `git fetch upstream` and consider merging/rebasing upstream
   improvements into the fork if desired.
