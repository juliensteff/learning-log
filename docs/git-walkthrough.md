# Git Walkthrough — From Zero to Self-Sufficient

A practical reference for what we've set up and how to use it without help.
Started: June 23, 2026 — Day 2 of Week 1.

---

## 1. The mental model

Git tracks three layers locally, plus one remote:

1. **Working tree** — the actual files on disk you edit.
2. **Staging area** (also called "the index") — files you've marked as "ready to commit." A holding pen between editing and snapshotting.
3. **Repository (history)** — the permanent log of committed snapshots, stored in the hidden `.git/` folder.
4. **Remote** (called `origin` by default) — a copy of your repo living on GitHub.

Changes move left to right:

```
edit file → git add → git commit → git push
   ↑           ↑           ↑           ↑
working     staging     local repo   remote
```

The single most important command is `git status`. Run it constantly — before adding, after adding, before committing, after pushing. It is your map.

---

## 2. Daily workflow

After making any edit in this repo:

```bash
git status              # what changed?
git diff <file>         # what specifically changed in <file>?
git add <file>          # mark <file> as ready to commit
git commit -m "msg"     # snapshot the staged files with a message
git push                # send commits to GitHub
```

To stage everything modified at once: `git add .` (the dot means "current directory and everything under it").

### Commit messages

Short, imperative, present tense. Examples we've actually used:

- `cs50p: lecture 0 — hello.py`
- `chore: add .gitattributes for line ending normalization`
- `chore: normalize line endings to LF`

The prefix (`cs50p:`, `chore:`, `feat:`, `fix:`, `docs:`) makes `git log` scannable later. You don't need to follow this convention strictly, but be consistent.

---

## 3. Reading `git status`

Long form output:

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   cs50p/lecture0/hello.py

Untracked files:
  cs50p/lecture0/greet.py
```

Translation:

- **"Changes not staged"** — you edited the file but haven't `git add`-ed it yet.
- **"Untracked"** — git has never seen this file. You need to `git add` it to start tracking.
- **"Changes to be committed"** — staged, ready for the next `git commit`.

Short form (`git status -s`):

```
 M cs50p/lecture0/hello.py
?? cs50p/lecture0/greet.py
```

| Symbol | Meaning |
|---|---|
| ` M` | Modified, not staged |
| `M ` | Modified, staged |
| `??` | Untracked |
| `A ` | Added (newly staged for first time) |
| `D ` | Deleted |
| `R ` | Renamed |

The space matters — the left column is the staged state, the right column is the working tree state.

---

## 4. The CRLF problem (the one we just fixed)

Windows saves files with `\r\n` line endings; Linux/Mac use `\n`. Git treats these as different bytes, so every line of a re-saved file looks "modified" even when content is identical. This pollutes your diffs and makes commits unreviewable.

### Fix applied once per machine

```bash
git config --global core.autocrlf true
```

Tells git: "convert LF to CRLF on checkout, convert back to LF on commit." You only ever do this once on a new machine.

### Fix that ships with the repo

A `.gitattributes` file at the repo root containing:

```
* text=auto eol=lf
```

This tells git to normalize all text files to LF inside the repo, regardless of which OS the author is on. Because the file is committed, anyone who clones gets the same rules automatically.

After adding `.gitattributes`, renormalize the tracked files:

```bash
git add --renormalize .
git commit -m "chore: normalize line endings to LF"
```

If `.py` or `.md` files later show as "modified" with no content change, check that `.gitattributes` still exists in the repo root.

---

## 5. The `index.lock` problem

Error: `fatal: Unable to create '.git/index.lock': File exists`

**What's happening:** every time git modifies the staging area, it creates `.git/index.lock` to prevent two git processes from corrupting each other. When the operation finishes cleanly, git deletes the lock. If a previous command crashed, got killed, or something else is touching git in the background (VS Code's source control panel is a common culprit), the lock stays.

**Fix:**

```bash
rm .git/index.lock
```

Then retry your command.

If it returns immediately: close VS Code's Source Control sidebar, delete the lock again, run your git commands from the terminal only.

---

## 6. When you mess up

### "I changed a file but want to throw away the change"

```bash
git restore <file>
```

Discards unstaged changes. The file goes back to its last committed state.

### "I `git add`-ed a file but want to unstage it"

```bash
git restore --staged <file>
```

Unstages but keeps your changes in the working tree.

### "I committed something but want to undo (locally, before pushing)"

```bash
git reset --soft HEAD~1     # undo last commit, keep changes staged
git reset --mixed HEAD~1    # undo last commit, keep changes unstaged (default)
git reset --hard HEAD~1     # undo last commit AND delete changes — be careful
```

`HEAD~1` means "one commit before the current one."

**Rule:** never `--hard` reset something you've already pushed. It rewrites history that other people may have pulled.

### "I want to see what I'm about to commit"

```bash
git diff --staged
```

---

## 7. Reading history

```bash
git log                     # full history (press q to quit)
git log --oneline           # one line per commit, scannable
git log --oneline -10       # last 10 commits
git log --stat              # which files changed in each commit
git log --graph --oneline   # ASCII branch graph
```

---

## 8. Your two-account SSH setup (reference)

You have two GitHub accounts:

- `juliensteff` — used for `~/Documents/dev/*` (this repo)
- `sciencecoherence` — used for `~/Documents/research/*`

Your `~/.ssh/config` defines aliases so each repo can use a different SSH key:

```
Host github.com-juliensteff
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_juliensteff

Host github.com-research
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_research
```

Your `~/.gitconfig` uses `includeIf` to auto-set commit author based on folder:

```
[includeIf "gitdir:~/Documents/dev/"]
  path = ~/.gitconfig-dev
[includeIf "gitdir:~/Documents/research/"]
  path = ~/.gitconfig-research
```

This means when you commit from `learning-log`, git automatically signs the commit as `juliensteff`. From the research folder, it signs as the research identity. You never have to remember.

Remotes use the SSH host alias instead of plain `github.com`:

```bash
git remote -v
# origin  git@github.com-juliensteff:juliensteff/learning-log.git
```

---

## 9. `.gitignore` — telling git what to ignore

A `.gitignore` file (already in your repo) lists patterns of files git should never track. Common entries:

```
# Python
__pycache__/
*.pyc
.venv/

# Editor
.vscode/
.idea/

# Secrets — NEVER commit these
.env
*.key
```

If you ever realize you committed a secret (API key, password), assume it's compromised and rotate it. Git history is forever, even if you delete the file in a later commit.

---

## 10. Glossary

| Term | Meaning |
|---|---|
| Working tree | The actual files on disk you edit. |
| Index / staging area | Files marked as ready for the next commit. |
| Commit | A snapshot of staged files with a message and author. |
| HEAD | A pointer to the current commit you're on. |
| `origin` | Conventional name for the default remote (your GitHub repo). |
| Branch | A named pointer to a sequence of commits. You're on `main`. |
| `main` | The default branch name (used to be `master`). |
| Pull | Fetch commits from the remote and merge into your current branch. |
| Push | Send your local commits to the remote. |
| Fetch | Download remote commits without merging. |
| Clone | Download an existing repo from a remote. |
| `.git/` | Hidden folder containing the entire repo history. Don't touch it directly. |

---

## 11. Habits to build

1. **Run `git status` constantly.** Before every action, after every action. It is free and prevents 80% of mistakes.
2. **Commit small, commit often.** One logical change per commit. "Add login form" not "Add login form, fix typo in README, refactor utils."
3. **Write commit messages future-you can read in a hurry.** Imagine reading `git log --oneline` six months from now.
4. **Never commit secrets.** Use `.gitignore` and environment variables.
5. **Push at least once per session.** Your work isn't backed up until it's on the remote.
6. **When something feels broken, run `git status` first.** Most "git problems" are just a clear status message you haven't read yet.

---

## 12. Cheat sheet — the 12 commands you'll use 95% of the time

```bash
git status                          # what's the state?
git diff <file>                     # what's changed in this file?
git diff --staged                   # what am I about to commit?
git add <file>                      # stage a file
git add .                           # stage everything in the current dir tree
git restore <file>                  # discard unstaged changes
git restore --staged <file>         # unstage a file
git commit -m "message"             # snapshot staged files
git push                            # send commits to GitHub
git pull                            # get commits from GitHub
git log --oneline -10               # see last 10 commits
git remote -v                       # confirm where origin points
```

Master these twelve. Everything else can be looked up when needed.
