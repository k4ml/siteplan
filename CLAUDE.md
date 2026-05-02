# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A local-first web app for reviewing markdown plans (typically AI-generated) with Google-Docs-style threaded comments anchored to text spans. The app exposes an HTTP API on `127.0.0.1:5173` so that Claude (or any other tool) can push docs in, wait for human comments, then pull the doc back with comments appended in a round-trippable footer block.

## Setup and commands

Toolchain pinned via `mise.toml` (Node 22, pnpm 10).

```bash
mise install            # one-time
pnpm install
pnpm dev                # starts Vite + the API middleware on 127.0.0.1:5173
pnpm typecheck          # tsc --noEmit
pnpm build              # tsc --noEmit && vite build
pnpm preview            # serve dist/
```

The CLI lives at `bin/mdr` (executable). Symlink it into PATH (`ln -s $(pwd)/bin/mdr ~/.local/bin/mdr`) and use it from anywhere:

```bash
mdr push plan.md          # PUT — slug defaults to filename without extension
mdr pull <slug>           # GET as markdown (body + comment footer)
mdr ls                    # tabular list of docs
mdr status <slug>         # JSON status
mdr watch <slug>          # block until openComments == 0
```

Override the API base with `MDR_BASE` (default `http://127.0.0.1:5173`).

## Architecture

### The single tricky problem: anchoring comments to source coordinates

Comments are stored as vi-style line/col coords on the *original markdown source*, but selection happens on the *rendered HTML*. The bridge:

1. **`src/lib/rehype-positions.ts`** — rehype plugin that walks the hast tree. It tags every Element that has source `position` info with `data-src-start` / `data-src-end` attributes (character offsets into the markdown source) and wraps every Text node outside `<pre>` blocks with `<span class="mdr-text" data-src-start data-src-end>`.
2. **`src/lib/selection.ts`** — converts a `window.getSelection()` Range to `{startLine, startCol, endLine, endCol, snippet}` by walking up to the nearest data-src-start ancestor and adding the offset within the text node.
3. **`src/lib/positions.ts`** — pure helpers: `buildLineStarts`, `offsetToLineCol`, `lineColToOffset`. The line-starts table is built per-render and reused for O(log n) coord conversion.
4. **`src/components/MarkdownRenderer.tsx`** — uses the **CSS Custom Highlight API** (`CSS.highlights.set(...)`) to paint precise sub-span highlights without DOM mutation. Wrapping spans only get `data-comment-ids` for click handling. Highlight names are `mdr-comment-open`, `mdr-comment-resolved`, `mdr-comment-orphan`, `mdr-comment-active`; styles are in `src/styles.css` under `::highlight(...)`.

If you need to change selection or highlight behavior, those four files are the entire surface.

### Round-trip format

`src/lib/export.ts` and `src/lib/import.ts` are the canonical implementations of the comment-footer format. Both the React app *and* the API middleware import them — do not duplicate the parser or you'll drift. The footer format:

```
<doc body>

--- THIS IS A COMMENT FROM MARKDOWN REVIEWER, DO NOT MODIFY ---

<startLine>/<startCol>:<endLine>/<endCol>: UNRESOLVED|RESOLVED

Me: <text>

Claude: <text>

-----
```

`parseImport` takes the round-trip markdown plus an array of existing comments. It diffs by `(startLine,startCol,endLine,endCol)` to preserve comment IDs across rounds, and re-anchors comments by snippet matching when the body changed: snippet still at coords → keep; snippet found uniquely elsewhere → resnap; otherwise → mark `status: 'orphaned'`. RESOLVED comments are never marked orphaned (they're already done).

### Backend: Vite middleware + flat-file storage

`vite-api.ts` is a Vite plugin (`apiPlugin()`) added to `vite.config.ts`. There is no separate backend process — the API runs inside the Vite dev server. Data lives at `~/.markdown-reviewer/docs/<slug>.json` (override with `MARKDOWN_REVIEWER_DATA_DIR`), one file per doc containing the full `FullDoc` shape.

Routes:
- `GET /api/docs` — list (returns `DocSummary[]`)
- `POST /api/docs?slug=<optional>` — create from raw markdown (body in request body)
- `GET /api/docs/:slug` — content negotiation: returns `text/markdown` (body + footer) by default, or JSON `FullDoc` with `Accept: application/json`
- `PUT /api/docs/:slug` — replace from raw markdown; respects `If-Unmodified-Since` for optimistic locking
- `PATCH /api/docs/:slug` — JSON `{body?, title?, comments?}` for granular React-app edits
- `DELETE /api/docs/:slug`
- `GET /api/docs/:slug/status` — cheap polling endpoint
- `GET /api/events` — Server-Sent Events stream of `{type: created|updated|deleted, slug, updatedAt, lastEditor}`

`X-Md-Reviewer-Editor` request header (`me` | `claude`) records who last touched the doc. The React app sends `me`; PUT defaults to `claude`; PATCH defaults to `me`. The soft lock fires only when `existing.lastEditor === "me"` AND the current PUT is from claude AND the doc was edited after `If-Unmodified-Since` — returns `409` with the current state in the body so the caller can re-pull and merge.

### Frontend: API-driven, SSE-refreshed

`src/lib/api-client.ts` wraps fetch. `src/App.tsx` holds `docs: DocSummary[]`, `activeSlug`, `activeDoc: FullDoc`, subscribes to `/api/events` via `EventSource`, and re-fetches the active doc on any matching event. Comment mutations from the UI go through `patchDoc()`; the only `localStorage` use that remains is `mdr:activeSlug` (which doc to open on cold load).

### Type vocabulary

`src/types.ts` defines three doc shapes — be careful which one a function consumes:
- `Doc` — id, slug, title, body, timestamps. The bare doc.
- `FullDoc extends Doc` — adds `comments: Comment[]` and `lastEditor`. What `getDoc` and `patchDoc` return.
- `DocSummary` — slug, title, comment counts, lastEditor, updatedAt. What `listDocs` returns.

`Editor` is `"me" | "claude"`. `CommentStatus` is `"open" | "resolved" | "orphaned"`.

### Skill

A skill lives at `~/.claude/skills/markdown-reviewer/SKILL.md` (outside this repo). It documents the push → wait → pull → resolve → push workflow for any Claude session. If you change the API or the round-trip format, update the skill in lockstep.

## Things that are deliberately simple

- No tests yet. Add them only if a regression actually bites.
- No backend process. The Vite plugin owns both routing and persistence.
- No router. Single-page app, single active doc at a time.
- Auth = none. The server binds `127.0.0.1` (in `vite.config.ts`); do not change that to `0.0.0.0` without adding auth.
- Data is plain JSON files. `cat ~/.markdown-reviewer/docs/<slug>.json` to debug state.
