# Markdown Reviewer

A local-first web app for reviewing the long markdown plans that Claude / Codex / etc. generate, with **threaded comments anchored to specific text spans** — like Google Docs comments, but on a plain markdown file.

It exposes a small HTTP API on `127.0.0.1:5173` so the AI tool that wrote the plan can push it in, wait for your comments, then pull it back with replies attached. No copy-paste shuffle, no dropped context.

```text
┌────────────┬────────────────────────────────────┬──────────────────┐
│ Docs       │  Document title                    │  Comments (3)    │
│            │  ────────────────────────────────  │                  │
│ • Plan A ● │  # Big heading                     │  ┌────────────┐  │
│ • Plan B   │                                    │  │ Me: ...    │  │
│ • Notes    │  Body prose with proper typography │  │ Claude:... │  │
│            │  ░░highlighted span░░              │  │ [reply][✓] │  │
│ [+ New]    │                                    │  └────────────┘  │
│ [Paste]    │                                    │                  │
└────────────┴────────────────────────────────────┴──────────────────┘
```

## Why?

You ask Claude for a plan. You start reading. Halfway in you spot something that needs clarification. You highlight the sentence, paste it back into the chat with your question, ask for context — and now the plan is somewhere up-thread, your question is below, and the rest of the plan no longer flows as a doc you can read.

This app inverts that: the plan is the document, your questions live as side-comments anchored to the exact text. When you're done commenting, the AI pulls the plan back with the comments embedded in a footer it knows how to read, addresses each one (reply or apply the change), and pushes it back. You see Claude's responses inline next to your original questions, keep iterating, and the document body stays a clean, readable plan throughout.

## Requirements

- [mise](https://mise.jdx.dev) (manages Node 22 and pnpm 10 — pinned in `mise.toml`)
- A modern browser with [CSS Custom Highlight API](https://caniuse.com/css-custom-highlight) support (Chrome ≥ 105, Safari ≥ 17.2, Firefox ≥ 140)

## Install and run

```bash
git clone https://github.com/<you>/markdown-reviewer.git
cd markdown-reviewer
mise install            # one-time, gets node + pnpm
pnpm install
pnpm dev                # http://127.0.0.1:5173
```

Leave `pnpm dev` running. Open `http://127.0.0.1:5173` in a browser tab.

### Install the `mdr` CLI on your `$PATH`

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/bin/mdr" ~/.local/bin/mdr
# add ~/.local/bin to PATH if it isn't already, then:
mdr --help
```

### Install the Claude Code skill (optional but recommended)

If you use [Claude Code](https://claude.ai/code), symlink the bundled skill so any session can push docs into the reviewer:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/markdown-reviewer" ~/.claude/skills/markdown-reviewer
```

After this, in any Claude Code session you can say things like *"Push this plan to the markdown reviewer"* and Claude will invoke `mdr push` itself.

## Workflow

### As a human, manually

1. Click **+ New from paste** in the sidebar.
2. Paste the markdown of a plan you want to review.
3. Highlight any text in the rendered doc → click the floating **Comment** button → write your question.
4. When done, click **Export current** in the sidebar → copy the result (body + comment footer) → paste into your AI chat. The AI sees a doc with your comments appended in a `--- THIS IS A COMMENT FROM MARKDOWN REVIEWER, DO NOT MODIFY ---` block.
5. The AI replies — either as `Claude: <reply>` lines or by editing the body and marking comments `RESOLVED`. Paste the result back via **Replace current with paste**. The footer parses back into threads; replies appear inline.

### With Claude Code (the integrated path)

If you've installed the skill above, the loop is:

1. In a Claude Code session, after Claude generates a plan, say *"send this to the markdown reviewer"*. Claude runs `mdr push` itself.
2. The doc appears in your browser tab automatically (via Server-Sent Events). Comment freely — highlight text, threaded replies, mark resolved.
3. When done, switch back to the Claude session and say *"pull my comments and address them"*. Claude runs `mdr pull`, reads each `UNRESOLVED` comment, replies or applies the change, and pushes back. Your browser refreshes live.
4. Repeat.

## `mdr` CLI reference

```text
mdr push <file> [--slug NAME] [--if-unmodified-since ISO]
    Send a markdown file to the reviewer. Slug defaults to the filename
    without extension. Use '-' for stdin: `mdr push - --slug NAME`.

mdr pull <slug> [--out FILE]
    Fetch the doc + comment footer as markdown. Prints to stdout, or
    writes to FILE.

mdr status [<slug>]
    Without slug: list every doc with open/total counts and last editor.
    With slug:    JSON status for that doc.

mdr ls
    Same as `mdr status` with no argument.

mdr watch <slug> [--interval SECONDS]
    Block until the doc has zero open comments. Default poll: 3s.

mdr open <slug>
    Print a URL that opens the doc in the running browser tab.

mdr backfill <slug>
    Populate context fields on legacy comments and re-anchor any
    orphans whose text can now be re-found.

Environment:
  MDR_BASE   API base URL (default http://127.0.0.1:5173)
```

## App features

- **Three-pane layout**: doc list (left), document (middle), comment threads (right). Both side panels are resizable (drag the dividers, double-click to reset) and hideable (chevron buttons in the toolbar).
- **Mobile responsive**: below 768px width, side panels become slide-out drawers; touch-friendly hit targets; bottom-anchored "Comment" bar appears when text is selected.
- **Edit your own comments** until Claude has replied to them. Pencil icon on hover (always visible on mobile).
- **Comment statuses**:
  - `open` — yellow highlight; you're waiting for Claude
  - `resolved` — dashed underline; Claude responded inline
  - `applied` — no highlight; Claude resolved by editing the body, original anchor text is gone but the thread is kept as audit trail
  - `orphaned` — red highlight; the anchor text is gone and couldn't be re-found
- **Smart re-anchoring**: when Claude inserts or removes sections that shift line numbers, comments re-anchor by their stored snippet + ~30 chars of surrounding context. Survives typical edit cycles.
- **Markdown in messages**: replies render fully (code blocks, tables, lists, bold).
- **Frontmatter renders as a Properties block**, not as garbled headings.
- **Rendered / Raw view toggle** in the toolbar.
- **Persistent UI state**: panel widths, doc selection, and per-thread collapsed state survive reloads.

## Data location

Docs live as plain JSON files at `~/.markdown-reviewer/docs/<slug>.json` (override with `MARKDOWN_REVIEWER_DATA_DIR`). UI preferences (active doc, panel widths, collapsed-thread state) live in `localStorage`.

To start fresh: `rm -rf ~/.markdown-reviewer/docs`.

## Security

The dev server is bound to `127.0.0.1` on purpose — there is **no authentication**. Don't expose it to your LAN (`--host` or `0.0.0.0`) without putting it behind something.

## Development

See [CLAUDE.md](./CLAUDE.md) for the architecture overview, file layout, and the position-anchoring approach.

```bash
pnpm dev          # vite dev server with the API middleware
pnpm typecheck    # tsc --noEmit
pnpm build        # production build
```

The skill at `skills/markdown-reviewer/SKILL.md` is the source of truth — if you change the API surface or the round-trip footer format, update the skill in lockstep so any installed copy stays in sync.

## License

MIT — do whatever you want with it.
