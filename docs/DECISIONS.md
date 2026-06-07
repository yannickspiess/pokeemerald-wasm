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
