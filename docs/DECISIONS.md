# Decisions

## 2026-06-07 - Fork instead of read-only clone
- Context: User wanted their own local copy of pokeemerald-wasm to run and be
  able to push fixes/changes (build fix, launcher, docs) to their own git.
- Decision: Forked to `yannickspiess/pokeemerald-wasm` via `gh repo fork`,
  cloned that fork as `origin`, and added the original `tripplyons/pokeemerald-wasm`
  as `upstream`.
- Consequences: User has push access to `origin` for any future changes;
  `upstream` stays available for pulling updates from the original project.

## 2026-06-07 - Fix the wasm build by mirroring native-build prerequisites
- Context: `make wasm` failed on a clean checkout because `data/maps.s` and
  `data/map_events.s` `#include` per-map `header.inc`/`events.inc`/
  `connections.inc` files. The native build generates these as prerequisites
  of `data/maps.o`/`data/map_events.o` (in `map_data_rules.mk`), but the wasm
  object rule only had an order-only dependency on the generic `generated`
  target, which doesn't cover these per-map files.
- Decision: Added a small, targeted rule —
  `$(WASM_OBJ_DIR)/maps.o $(WASM_OBJ_DIR)/map_events.o: | $(MAP_HEADERS) $(MAP_EVENTS) $(MAP_CONNECTIONS)`
  — placed after `include map_data_rules.mk` (so those variables are defined),
  rather than restructuring `AUTO_GEN_TARGETS` or duplicating generation logic.
  This keeps the change minimal and isolated, per `AGENTS.md` guidance to
  prefer small WASM adapters at the build-rule boundary.
- Consequences: `make wasm` now works from a clean checkout without first
  running `make`/`make modern`. Minimal diff; no behavior change to the
  native GBA build path.

## 2026-06-07 - One-click launcher via Chrome app-mode window, not a packaged PWA
- Context: User wanted a clickable way to launch the game in Chrome and
  mentioned "Chrome web app" mode specifically.
- Decision: Created `launch_game.command` (a double-clickable shell script)
  that builds if needed, starts `web/server.mjs`, and opens Chrome with
  `--app=http://localhost:8000` for a chromeless, app-style window — instead
  of building a true installable PWA manifest or an Automator `.app` wrapper.
- Consequences: Zero changes to the served app; works immediately with the
  existing dev server; trivially editable for a different port/browser.
  Trade-off: requires Chrome and the local Node server to be available — it's
  not a fully standalone installed application.

## 2026-06-07 - Fix the battle-animation WASM trap with a narrow #if WASM bounds check, not a broader rewrite
- Context: The user hit `RuntimeError: table index is out of bounds at
  pokeemerald.wasm.RunAnimScriptCommand` while using the new keystroke-loop
  feature to mash up/down/a repeatedly during a wild battle. Root cause:
  `RunAnimScriptCommand` (`src/battle_anim.c:330`) dispatches animation-script
  commands via `sScriptCmdTable[sBattleAnimScriptPtr[0]]()`. Input arriving far
  faster/denser than the original hardware (60 Hz sampling, human reflexes)
  ever produced can leave `sBattleAnimScriptPtr` pointing at a garbage byte
  outside the table. On real hardware that reads garbage memory as a function
  pointer and limps along; in WASM, function pointers are indirect-call-table
  indices, so an out-of-range one traps and halts the whole emulator.
- Decision: Added a small `#if WASM`-guarded check directly at the dispatch
  site — `if (sBattleAnimScriptPtr[0] >= ARRAY_COUNT(sScriptCmdTable))
  { Cmd_end(); return; }` — that ends the broken animation gracefully instead
  of trapping (commit `de8a0162e`). Considered alternatives: throttling input
  rate from the keystroke-loop/speed-multiplier JS layer (would blunt the
  automation feature's usefulness and not address the root inconsistency), or
  rewriting the battle-animation state machine to be provably reentrant-safe
  (large, invasive, against `AGENTS.md`'s "avoid broad rewrites of game logic"
  guidance).
- Consequences: Converts a hard crash into a gracefully-ended animation;
  never triggers during normal play (the condition is only reachable once the
  engine state is already inconsistent). Trade-off: it treats the *symptom*
  (the WASM trap), not the underlying "engine reached an inconsistent state
  from superhuman input rates" condition — a glitchy/skipped animation can
  still occur where a crash used to. If similar traps surface from other
  script-dispatch tables (field scripts, AI scripts, battle scripts proper),
  the same narrow pattern is the template — apply and verify per site rather
  than blanket-patching.
