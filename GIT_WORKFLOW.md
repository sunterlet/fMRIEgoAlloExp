# Git workflow: fMRI experiment (PC ↔ scanner)

One repo, two places: **develop on your PC** (ramot), **run at the scanner** (LaCie). Git keeps them in sync so you stop copying by hand and avoid duplicate versions.

---

## The big picture

| Where        | Role                         | Git folder                          |
|-------------|------------------------------|-------------------------------------|
| **PC (ramot)** | Develop and edit scripts     | `/Volumes/ramot/sunt/Navigation/fMRI` |
| **Scanner (LaCie)** | Run experiments, small fixes | `/Volumes/LaCie/Sun`                 |

- **One GitHub repo**: `fMRIEgoAlloExp` (same on both).
- **One main branch**: `master` = shared code.
- **Optional**: a `scanner` branch for scanner-only tweaks (see below).

---

## Core idea (3 commands)

1. **Save your work** (PC): `git add` → `git commit` → `git push`
2. **Get latest code** (scanner): connect LaCie, then `git pull`
3. **Bring scanner changes back** (if you fix something at scanner): on LaCie `git add` → `commit` → `push`, then on PC `git pull`

No more manual copy-paste of whole folders.

---

## Step-by-step: On your PC (development)

### 1. See what changed

```bash
cd /Volumes/ramot/sunt/Navigation/fMRI
git status
```

- **Modified**: files you edited.
- **Untracked**: new files Git doesn’t know yet.

### 2. Stage the files you want to save

- Everything in current folder:
  ```bash
  git add .
  ```
- Or only specific files:
  ```bash
  git add exploration/snake.py fmri_session.m
  ```

### 3. Commit (save a snapshot with a message)

```bash
git commit -m "Add trigger handling for scanner display"
```

Use a short, clear message: what you did or why.

### 4. Push to GitHub (so the scanner can get it)

```bash
git push origin master
```

(You need internet. If you use a different branch, replace `master` with that branch name.)

---

## Step-by-step: At the scanner (LaCie)

### 1. Connect the LaCie drive and open terminal in the project

```bash
cd /Volumes/LaCie/Sun
```

### 2. Get the latest code from your PC (via GitHub)

```bash
git pull origin master
```

Do this **before** running an experiment if you changed anything on the PC. This replaces your scripts with the latest version from the repo.

### 3. If you fix something at the scanner and want to keep it

```bash
git add .
git commit -m "Scanner: fix screen selection for MRI display"
git push origin master
```

Then on your PC, next time:

```bash
cd /Volumes/ramot/sunt/Navigation/fMRI
git pull origin master
```

So the fix is now on both PC and LaCie.

---

## Handling “scanner-only” vs “dev-only” files

Some files exist only on the scanner (e.g. `fix_overscan.m`, `PlayMovie_Scaled.m`, `select_screen_with_screenshots.m`). You have two options.

### Option A (simplest): One branch, everything in the repo

- Put **all** scripts (including scanner-only ones) in the repo.
- On PC you have them but might not use them; at the scanner you use them.
- One branch (`master`), one history. Sync with `git pull` / `git push` as above.

To add scanner-only files from LaCie:

```bash
cd /Volumes/LaCie/Sun
git add fix_overscan.m PlayMovie_Scaled.m select_screen_with_screenshots.m select_screen_with_screenshots.py
git commit -m "Add scanner-specific scripts (display, triggers)"
git push origin master
```

Then on PC: `git pull origin master` — those files will appear in your fMRI folder too.

### Option B: Two branches (master + scanner)

- **master**: what you develop on the PC.
- **scanner**: same as master + scanner-specific changes (paths, display, triggers).

**On PC (after developing):**

```bash
git add .
git commit -m "Update practice session timing"
git push origin master
```

**To update the scanner computer:**  
On LaCie (or on PC with LaCie mounted), in the **same repo folder** (e.g. LaCie clone):

```bash
git checkout scanner
git merge master
git push origin scanner
```

**On LaCie at the lab:** use branch `scanner`:

```bash
git checkout scanner
git pull origin scanner
```

**If you fix something only at the scanner:** commit on `scanner`, push, then (if you want that fix in main code) merge `scanner` into `master` on PC and push.

Start with **Option A**; move to Option B only if you really need to keep scanner and dev versions different in a structured way.

---

## Quick reference

| Goal                         | Command (PC)                    | Command (LaCie)           |
|-----------------------------|----------------------------------|----------------------------|
| Save and upload my changes  | `git add .` then `git commit -m "msg"` then `git push origin master` | — |
| Get latest from PC         | —                                | `git pull origin master`   |
| Save scanner-only fix      | —                                | `git add .` then `commit` then `push` |
| Get scanner fix on PC      | `git pull origin master`         | —                          |
| See what’s modified         | `git status`                     | `git status`                |
| See history                | `git log --oneline -10`          | same                       |

---

## Important notes

1. **Results and data**: Your `.gitignore` already ignores `Results/`, `*.csv`, `*.mat`, etc. So `git add .` won’t put subject data in the repo — only code and docs. That’s what you want.
2. **Conflict**: If both you and the scanner changed the same file, `git pull` may say “merge conflict”. Open the file, fix the conflict markers, then `git add <file>` and `git commit`.
3. **Remote URL**: Prefer not storing passwords/tokens in the remote URL. Use SSH (`git@github.com:sunterlet/fMRIEgoAlloExp.git`) or the Git credential helper. If you ever pasted a token in the URL, rotate that token in GitHub (Settings → Developer settings → Personal access tokens) and switch the remote to SSH or HTTPS without the token.

---

## Summary

- **One repo**, same on PC and LaCie.
- **PC**: develop → `git add` → `git commit` → `git push`.
- **LaCie**: before running → `git pull`; after a fix → `git add` → `commit` → `push`.
- Put all scripts (including scanner-only) in the repo so everything is documented and in one place.

If you tell me whether you prefer Option A (one branch) or Option B (scanner branch), the next step can be: “first commit on PC” and “first pull on LaCie” with exact file lists.
