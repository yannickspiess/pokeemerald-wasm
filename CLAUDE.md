# pokeemerald-wasm — Agent Instructions

## Project

- Pokémon Emerald decompilation recompiled to WebAssembly with a browser frontend.
- Local project root: `/Users/yannickspiess/Documents/daily app/pokeemerald-wasm`
- Fork of `tripplyons/pokeemerald-wasm`. Remotes: `origin` = your fork
  (`yannickspiess/pokeemerald-wasm`), `upstream` = the original.

## Session Start

Read `AGENTS.md` first — it is the authoritative, detailed guide for this repo:
WASM port layout, implementation rules, replay/verification tooling
(`tools/wasm_replay.mjs`), and build/commit conventions. Follow it top-to-bottom
for anything touching the WASM port, browser glue, or original source.

## Build & Test

```bash
make wasm          # build build/wasm/pokeemerald.wasm
make serve-wasm    # build + serve the browser frontend (http://localhost:8000)
make modern        # native modern GBA build, for changes to shared/original source
make compare       # verify ROM-matching behavior when relevant
```

- Local toolchain note: macOS needs `llvm` (wasm-capable clang) and `lld`
  (provides `wasm-ld`) from Homebrew — `brew install llvm lld`. Both resolve via
  `/opt/homebrew/bin` and `/opt/homebrew/opt/llvm/bin` once installed; no
  further `WASM_CC`/`WASM_LD` overrides are needed.
- After WASM/browser changes, run `make wasm` (and `make serve-wasm` for runtime
  changes), then verify the served page reaches the intended flow — see
  `AGENTS.md` for the headless replay tool if a scripted check is useful.
- Don't claim a build or behavior works without having actually run it.
- To launch the game in Chrome with one click, double-click `launch_game.command`
  in Finder — it builds if needed, starts the local server, and opens the game
  in a Chrome app window.
- **Browser automation:** the Claude-in-Chrome MCP is sometimes not connected
  here. Don't retry it repeatedly — fall back to the Playwright MCP
  (`mcp__plugin_playwright_playwright__*`) to drive Chrome for verification.

## Operating Rules

- **Always work directly on `master`.** Do not create feature branches or git
  worktrees. This overrides any Superpowers or default agent preference for
  branching.
- **When using any Superpowers skill**, skip the "show in a web browser" offer.
  Assume the answer is always "no".
- **Commit and push to `origin` after every meaningful chunk of work.**
  `git add … && git commit … && git push origin master` in one sequence — never
  leave commits unpushed. Origin (your fork) is the backup; an unpushed commit
  is effectively lost if the machine dies.
- Follow `AGENTS.md`'s commit-message style and "verify before commit" guidance
  — these are project-specific and take precedence over generic habits.
