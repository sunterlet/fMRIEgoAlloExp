# Syncing Mac ↔ LaCie ↔ fMRI PC with Git

Step-by-step: one repo, reset to relevant files only, then keep Mac and LaCie in sync. (Exploration folders are left aside for now.)

---

## Overview

| Location | Role |
|----------|------|
| **Mac** `/Volumes/ramot/sunt/Navigation/fMRI` | Develop and edit; **source of truth** for the repo |
| **LaCie** `/Volumes/LaCie/Sun` | Clone of the repo; copy this folder to the fMRI PC |
| **fMRI PC** (scanner) | Run experiments; **replace** its experiment folder with LaCie’s `Sun` when you update |

**Flow:** Mac (edit → commit → push) → GitHub → LaCie (pull) → copy LaCie/Sun to fMRI PC.

---

## Part 1: Decide what goes in the repo (relevant files only)

**Include (tracked):**

- **Root:** `practice_session.m`, `fmri_session.m`, `combine_session_data.m`, `setup_experiment.m`, `PlayMovie_Scaled.m`, `fixation.pptx`, `install_dependencies.py`, `requirements.txt`, `README.md`, `EXPERIMENT_REQUIREMENTS.md`, `FOLDER_ORGANIZATION_PLAN.md`, `GIT_WORKFLOW.md`, `NEXT_STEPS_PLAN.md`, `SYNC_MAC_LACIE_GIT.md`, fixation images used by code (`fixation_cross_black_on_white.png`, `fixation_cross_white_on_black.png` if used), `.gitignore`
- **Folders:** `PTSOD/` (Code, Instructions_HE, Stimuli), `sounds/`, `movies/` (structure; large .mp4 can stay ignored), `cross/` if used, **exploration/** and **exploration_trigger/** for now (you can trim later)

**Exclude (do not track):**

- `Results/`, `archive/`, `__pycache__/`, `.DS_Store`, `*.mat`, `*.csv`, `*.xlsx`, `*.mp4` (already in `.gitignore`)

So: “reset and push only relevant files” = make sure only these are tracked and everything else is ignored.

---

## Part 2: Merge Mac and LaCie into one layout (before reset)

Right now Mac and LaCie have **duplicates** (e.g. `fmri_session.m`, `PTSOD/`) and **unique** files (e.g. Mac: `practice_session.m`, some docs; LaCie: `exploration_trigger/`, `PlayMovie_Scaled.m`, `fixation.pptx`). We make **Mac** the single source of truth by copying LaCie-only stuff into Mac, then we’ll push that.

**On the Mac (with LaCie mounted):**

1. **Copy from LaCie → Mac** anything that exists only on LaCie or that you want to take from LaCie:
   - `exploration_trigger/` (whole folder) → into Mac’s fMRI folder (so Mac has `.../fMRI/exploration_trigger/`)
   - `PlayMovie_Scaled.m` → Mac `fMRI/`
   - `fixation.pptx` → Mac `fMRI/`
   - `combine_session_data.m` → Mac `fMRI/` (overwrite if you want the LaCie version)
   - Fixation images LaCie uses (e.g. `fixation_cross_black_on_white.png`, `fixation_cross_white_on_black.png`) → Mac `fMRI/`
   - `movies/` (folder structure; actual .mp4 can stay out of Git if ignored)

2. **Copy from Mac → LaCie** anything that exists only on Mac and should be on LaCie:
   - `practice_session.m` → LaCie `Sun/` (so scanner-side clone has it for reference; practice is run on behavioral PC from Mac/shared drive, but having it in the repo is fine)
   - Any Mac-only docs you want in the repo (e.g. `NEXT_STEPS_PLAN.md`, `SYNC_MAC_LACIE_GIT.md`) are already on Mac; they’ll get to LaCie when we pull after reset.

After this, **Mac’s fMRI folder** should contain everything you want in the repo (practice + scanner scripts, exploration + exploration_trigger for now). LaCie will later get the same content via Git.

---

## Part 3: Reset the repo and push only relevant files (on Mac)

Do this **on the Mac** in `/Volumes/ramot/sunt/Navigation/fMRI`.

### Step 1: Ensure .gitignore is correct

Your `.gitignore` should ignore at least:

- `Results/`, `archive/`, `__pycache__/`, `*.mp4`, `*.mat`, `*.csv`, `*.xlsx`, `.DS_Store`

If something “relevant” is currently ignored (e.g. a small script), add an exception with `!path/to/file`.

### Step 2: Stop tracking junk (keep files on disk, only remove from Git)

```bash
cd /Volumes/ramot/sunt/Navigation/fMRI

# If archive/ or other big folders were ever committed, remove from index only (files stay on disk)
git rm -r --cached archive/ 2>/dev/null || true
git rm -r --cached Results/ 2>/dev/null || true
# Add any other folder you want to untrack:
# git rm -r --cached path/to/folder 2>/dev/null || true
```

### Step 3: Add only what you want in the repo

```bash
git add .
```

Because of `.gitignore`, only non-ignored files will be staged. Review:

```bash
git status
```

If something unwanted is staged, unstage and add to `.gitignore`:

```bash
git reset HEAD path/to/unwanted
echo "path/to/unwanted" >> .gitignore
```

### Step 4: One clean commit (option A: keep history)

```bash
git commit -m "Sync repo: single layout for Mac and scanner (practice + fmri_session, exploration + exploration_trigger)"
git push origin master
```

### Step 4 (alternative): Reset history and push only this state (option B: clean history)

If you want the remote to **forget old history** and only have this state:

```bash
git commit -m "Sync repo: single layout for Mac and scanner (practice + fmri_session, exploration + exploration_trigger)"
git push origin master --force
```

**Or** start from a fresh history (orphan branch):

```bash
git checkout --orphan clean-main
git add .
git commit -m "Initial clean sync: Mac + scanner layout, relevant files only"
git branch -D master
git branch -m master
git push origin master --force
```

Use **option B** only if you’re sure no one else depends on the old history. Otherwise use option A.

---

## Part 4: Make LaCie a clean clone (so it matches Mac)

After the repo on GitHub has only the relevant files, make LaCie match it.

**Option A – LaCie already has a clone (e.g. Sun was cloned from the same repo):**

```bash
cd /Volumes/LaCie/Sun
git fetch origin
git checkout master
git reset --hard origin/master
git clean -fd
```

This makes LaCie’s `Sun` **exactly** what’s on `origin/master`. Any local files not in the repo (e.g. old exploration_trigger-only content) will be removed by `git clean -fd` unless they’re ignored. **Back up** anything on LaCie you care about before running `git clean -fd`.

**Option B – Start fresh on LaCie (safest if Sun is a mess):**

1. Rename current Sun so you don’t lose it:
   ```bash
   cd /Volumes/LaCie
   mv Sun Sun_backup_$(date +%Y%m%d)
   ```
2. Clone the repo into a new `Sun`:
   ```bash
   git clone https://github.com/sunterlet/fMRIEgoAlloExp.git Sun
   cd Sun
   git checkout master
   ```
3. Copy back from `Sun_backup_*` anything that **must** live on LaCie but is not in the repo (e.g. large movies, local config). Prefer putting scripts and small assets in the repo so you don’t need this.

Now **Mac and LaCie are synced**: same repo, same branch, same files (excluding ignored and local-only).

---

## Part 5: Day-to-day sync Mac ↔ LaCie ↔ fMRI PC

### On the Mac (after editing)

```bash
cd /Volumes/ramot/sunt/Navigation/fMRI
git add .
git status
git commit -m "Short description of what you changed"
git push origin master
```

### On LaCie (before going to the scanner)

Connect LaCie, then:

```bash
cd /Volumes/LaCie/Sun
git pull origin master
```

If you fixed something on LaCie and want it in the repo:

```bash
cd /Volumes/LaCie/Sun
git add .
git commit -m "Scanner: describe fix"
git push origin master
```

Then on the Mac:

```bash
cd /Volumes/ramot/sunt/Navigation/fMRI
git pull origin master
```

### On the fMRI PC (scanner)

- **Yes:** Replace the experiment folder on the fMRI PC with the contents of **LaCie’s Sun** (or a copy of it). So: after `git pull` on LaCie, copy the whole `Sun` folder (or its contents) to the fMRI PC and replace the existing experiment folder.
- That way the scanner always runs the same code that’s on LaCie, which is in sync with the repo via pull.

---

## Quick answers

| Question | Answer |
|----------|--------|
| Can we reset the repo and push only relevant files? | Yes. Use `.gitignore` + `git rm --cached` for anything already tracked that you want to drop, then `git add .` and commit. Optionally force-push or use an orphan branch for a clean history. |
| How to sync Mac (fMRI) and LaCie (Sun)? | Make Mac the source of truth: copy LaCie-only files (e.g. exploration_trigger, PlayMovie_Scaled.m, fixation.pptx) into Mac, then commit and push. On LaCie, `git pull` (or reset to `origin/master` / fresh clone). After that, both are synced. |
| When synced, replace fMRI PC folder with LaCie/Sun? | Yes. After pulling on LaCie, replace the fMRI PC experiment folder with the contents of `/Volumes/LaCie/Sun`. |
| Exploration folders for now? | Left as-is: both exploration and exploration_trigger can live in the repo until you consolidate (see NEXT_STEPS_PLAN.md). |

---

## Checklist (first-time setup)

- [ ] LaCie mounted. Copy LaCie-only files (exploration_trigger, PlayMovie_Scaled.m, fixation.pptx, etc.) into Mac’s fMRI folder.
- [ ] Copy Mac-only files (practice_session.m, docs) to LaCie if you want them there before the pull (optional; they’ll come with pull).
- [ ] On Mac: `git rm -r --cached archive/ Results/` (and any other dirs to untrack), then `git add .`, check `git status`, commit, push.
- [ ] On LaCie: backup if needed, then `git fetch` + `git reset --hard origin/master` (or fresh clone into new `Sun`).
- [ ] At scanner: replace fMRI PC experiment folder with LaCie’s `Sun` contents.

After that, use “Part 5” for daily sync.
