# Git Worktree Development Workflow

> All development on this repository **MUST** use isolated git worktrees to protect the `main` branch
> and other in-progress work. Direct edits on `main` are discouraged for non-trivial changes.

## Why Worktrees

A git worktree creates a detached working copy of the repository, allowing parallel branches
without stashing, reverting, or conflicting local changes. Benefits:

- **Isolation** — in-progress work never pollutes the `main` working tree
- **Parallel branches** — review a PR in one worktree while developing in another
- **Safe cleanup** — worktree directory + branch are removed atomically after merge

## Workflow Steps

| Step | Action | Tool |
|---|---|---|
| **1. Consent** | Before creating a worktree, ask the user for consent unless a preference is already declared | User prompt |
| **2. Create** | Use `EnterWorktree` (native tool) — handles directory placement, branch creation, and session switching | `EnterWorktree` tool |
| **3. Setup** | Auto-detect and run project setup (install dependencies, verify environment) | `pip install` / `uv install` |
| **4. Baseline** | Run tests to ensure a clean starting point before making changes | `pytest` / project-appropriate runner |
| **5. Develop** | Make all changes, commit, and push to the worktree branch | `git commit` + `git push` |
| **6. Merge** | Switch to `main`, merge worktree branch, push `main` | `git checkout main && git merge <branch> && git push origin main` |
| **7. Cleanup** | Use `LeaveWorktree` with `action="remove"` — deletes directory and branch atomically | `LeaveWorktree` tool |

## Rules

- **Detect first** — before creating, check if already in a linked worktree (`GIT_DIR != GIT_COMMON`); also verify not in a submodule via `git rev-parse --show-superproject-working-tree`. If already isolated, skip creation.
- **Prefer native tools** — always use `EnterWorktree` / `LeaveWorktree` over raw `git worktree add`. Native tools manage state the harness can track.
- **Verify `.gitignore`** — for project-local worktree directories (`.worktrees/`), confirm they are gitignored before creating to avoid committing worktree contents.
- **Baseline tests required** — never start development without verifying tests pass first. Report and handle failures before proceeding.
- **Clean up after merge** — always remove the worktree after the branch is merged. Use `LeaveWorktree` with `action="remove"` (and `force=true` only after user confirmation for unpushed commits on the worktree branch).
- **Branch naming** — the worktree branch name is auto-generated (e.g., `worktree-<name>`). No need to push this branch to remote; the merge to `main` carries the commits.

## Common Mistakes

### Fighting the harness

- **Problem:** Using `git worktree add` when the platform already provides isolation via `EnterWorktree`
- **Fix:** Always run detection first, then defer to native tools

### Skipping detection

- **Problem:** Creating a nested worktree inside an existing one or a submodule
- **Fix:** Run `GIT_DIR` / `GIT_COMMON` check and submodule detection before creating

### Skipping ignore verification

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always use `git check-ignore` before creating a project-local worktree

### Proceeding with failing tests

- **Problem:** Cannot distinguish new bugs from pre-existing issues
- **Fix:** Report baseline failures, get explicit permission to proceed

## Quick Reference

| Situation | Action |
|---|---|
| Already in a linked worktree | Skip creation (run detection first) |
| In a git submodule | Treat as normal repo (submodule guard) |
| `EnterWorktree` tool available | Use it (preferred over `git worktree add`) |
| `.worktrees/` directory exists | Use it (verify gitignored) |
| Directory not gitignored | Add to `.gitignore` + commit before proceeding |
| Baseline tests fail | Report failures + ask user before proceeding |
| Unpushed commits on worktree branch | Ask user for confirmation before `force=true` cleanup |