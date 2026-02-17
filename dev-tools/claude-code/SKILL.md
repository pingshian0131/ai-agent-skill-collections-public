---
name: claude-code
description: Use Anthropic Claude Code CLI via the `claude` command for coding tasks, refactors, debugging, tests, and repo-wide edits. Trigger when the user asks to use Claude Code, says "用 claude/claude code", or wants a task delegated to the local Claude CLI.
---

# Claude Code CLI Skill

Use the local Claude Code CLI through `exec`.

## Core rule

- Always invoke Claude Code with the `claude` command (not other wrappers).

## Fast workflow

1. Confirm CLI availability:
   - `which claude`
2. If missing, report clearly and stop.
3. Run Claude task with one-shot prompt in the project directory.
4. Return concise result + changed files + next step.

## Command patterns

### One-shot task

```bash
claude -p "<task prompt>"
```

### Safer deterministic run (recommended)

```bash
claude -p "<task prompt>" --output-format text
```

### Include repo context in prompt

State exact constraints in prompt (tests, style, no breaking changes, files to touch).

Example prompt text:

- "Fix failing tests in api/, keep behavior unchanged, then summarize modified files."
- "Refactor this function for readability without changing output; preserve type hints."

## Execution guidelines

- Run in the intended repo root via `exec.workdir`.
- For long tasks, run in background and stream logs via `process`.
- After Claude finishes, validate quickly (run tests/lint if requested).
- Do not claim success without command output.

## Failure handling

- If `claude` not found: suggest installation/login and stop.
- If auth/session errors occur: ask user to re-auth in terminal, then retry.
- If task is ambiguous: ask one focused clarification question.
