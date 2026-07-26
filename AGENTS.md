- When committing, add details commit messages. Do not attribute.
- All text shown in UI should be wrapped for translation.

## Markdown Reviewer

The markdown-reviewer app lives in `ext-src/markdown-reviewer/` and is used for reviewing plans with threaded comments.

### Setup
Dependencies are installed via pnpm (already done). To start the dev server:
```bash
cd ext-src/markdown-reviewer && pnpm dev
```
App runs at `http://127.0.0.1:5173`.

### CLI
The `mdr` CLI is symlinked to `~/.local/bin/mdr`. Usage:
- `mdr push <file> --slug <name>` - push a markdown doc
- `mdr pull <slug> --out <file>` - pull doc with comments
- `mdr ls` - list all docs
- `mdr --help` - full reference

### Skill
The Claude Code skill is symlinked at `.claude/skills/markdown-reviewer` (relative path, committed to repo). This enables "send to markdown reviewer" and "pull my comments" workflows.

### Workflow
1. Push plan: `mdr push plan.md --slug my-plan`
2. User reviews at `http://127.0.0.1:5173/my-plan`
3. Pull with comments: `mdr pull my-plan --out /tmp/my-plan.md`
4. Address UNRESOLVED comments, push back

The skill (`.claude/skills/markdown-reviewer/SKILL.md`) has the full workflow details.
