# Folder organization plan

Goal: keep only what the experiment needs; move test scripts and irrelevant files into an **archive** so the repo stays clear and we can sync Mac ↔ PC without clutter.

Reference: **EXPERIMENT_REQUIREMENTS.md** (what practice and fmri_session actually use).

---

## Mac vs PC – quick recap

| | **Mac (ramot)** | **PC (scanner, LaCie)** |
|---|----------------|------------------------|
| **Role** | Development + **practice** | **Scanner run** only |
| **Practice** | `practice_session.m` → uses **exploration** | Not run here |
| **Scanner** | Not used | `fixation.pptx` + `fmri_session.m` → uses **exploration_trigger** + **exploration** |
| **Line endings** | LF | CRLF (Windows) – Git can handle with `.gitattributes` |
| **Paths** | Unix-style | Windows (e.g. `C:\...`); MATLAB `fullfile` is fine |

So we organize **one logical layout** that works on both; the only difference is which entry point you run and that the PC has scanner-only files (e.g. PlayMovie_Scaled, fixation.pptx).

---

## Proposed clean structure (target)

Same structure on both Mac and PC, so Git sync is straightforward. Only the **contents** of some folders differ (e.g. scanner has exploration_trigger, Mac might not need it if you never run fmri_session on Mac).

```
fMRI/   (or Sun/ on PC – same layout)
├── practice_session.m          # Mac only: run for practice (not on PC)
├── fmri_session.m              # PC: run in scanner
├── combine_session_data.m
├── PlayMovie_Scaled.m          # PC only (or keep on both for sync)
├── fixation.pptx               # PC only (or keep on both)
├── setup_experiment.m          # If you use for setup
├── exploration/                # Required: snake/one_target/multi_arena (practice + snake on scanner)
├── exploration_trigger/        # Required on PC only (one_target_run, full_arena_run, trigger wrappers)
├── PTSOD/
│   ├── Code/
│   ├── Instructions_HE/
│   └── Stimuli/
├── sounds/
├── arenas_new_icons/
├── movies/                     # PC: TheShining.mp4, MissionImpossible.mp4
├── cross/                      # If used by PTSOD or display
├── Results/                    # Created at runtime; in .gitignore
├── README.md
├── EXPERIMENT_REQUIREMENTS.md
├── FOLDER_ORGANIZATION_PLAN.md
├── GIT_WORKFLOW.md
└── .gitignore
```

Optional but useful: scanner-only helpers in one place, e.g. `scanner_scripts/` with fix_overscan.m, select_screen_with_screenshots.*, so they’re in the repo but clearly “PC only”.

---

## What to KEEP (required for experiment)

Use **EXPERIMENT_REQUIREMENTS.md** as the authority. Summary:

### On both Mac and PC (for one shared repo)

- **exploration/** – used by practice (Mac) and by run_snake_game on scanner (PC).
- **PTSOD/Code**, **PTSOD/Instructions_HE**, **PTSOD/Stimuli**
- **sounds/**, **arenas_new_icons/**
- **practice_session.m**, **fmri_session.m**, **combine_session_data.m**
- **setup_experiment.m** (if you use it)
- Docs: README, EXPERIMENT_REQUIREMENTS, FOLDER_ORGANIZATION_PLAN, GIT_WORKFLOW

### PC only (scanner)

- **exploration_trigger/** – all of it (MATLAB wrappers + Python for one_target_run, full_arena_run; run_snake_game wrapper lives here but runs Python in exploration).
- **PlayMovie_Scaled.m**, **movies/** (TheShining.mp4, MissionImpossible.mp4)
- **fixation.pptx**
- Optional: **fix_overscan.m**, **select_screen_with_screenshots.m/.py**, **cross/** if used

### Mac only (for practice)

- Nothing extra beyond the shared list; practice uses **exploration** and PTSOD/sounds/arenas.

### Data (do not put in Git)

- **Results/** – keep on disk, ignore in Git (already in .gitignore).

---

## What to ARCHIVE (move out of the way, don’t delete yet)

Move these into an **archive** folder (or a separate archive repo) so the main folder stays clean. You can add `archive/` to `.gitignore` if you don’t want to sync it.

### On Mac (ramot)

| Item | Reason |
|------|--------|
| **pythontry/** | Test scripts, old versions, improved_navigation, PsychoPy tries, etc. Not used by practice_session or fmri_session. |
| **Analysis/** | Post-hoc analysis; not needed to run the experiment. |
| **FMRI_dep/** | Likely old dependencies or copies. |
| **fMRI_codes/** | If it’s duplicate or legacy code. |
| Root-level test/duplicate scripts | e.g. multiple `*_backup*.m`, `*_orig*.m`, one-off `analyze_*.m`, `visualize_*.py` that aren’t called by practice_session or fmri_session. |
| **.qodo/** | Tool-specific; can be ignored or archived. |

### On PC (Sun)

| Item | Reason |
|------|--------|
| **fMRIEgoAlloExp/** | Looks like an old clone or extracted zip; redundant if Sun is the clone. |
| **fMRIEgoAlloExp-FMRI_dependencies/** | Same. |
| **fMRIEgoAlloExp-master.zip**, **fMRIEgoAlloExp-FMRI_dependencies.zip** | Old archives; keep elsewhere if needed. |
| **scripts/** | If it’s duplicate or one-off scripts not used by fmri_session. |
| **screen_identification_output/**, **exploration_annotation_trajectories.png**, **volume_analysis*** | Outputs/analyses; not needed to run the session. |
| Root-level analysis/visualization scripts | Same as Mac – keep in archive if you want to preserve them. |

### In exploration/ or exploration_trigger/

- **Test files**: e.g. `test_*.py`, `test_*.m` that are not called by the main flow.
- **Legacy/duplicate**: e.g. `*_orig.py`, `*_copy.m`, `multi_arena_orig.py` (keep one canonical version).
- **Vector/other experiments**: e.g. exploration/vection_experiment if not part of the main protocol.

Don’t delete these yet – move to **archive/** (or archive/exploration, archive/pythontry, etc.) and only remove after you’re sure you don’t need them.

---

## Step-by-step organization (suggested order)

### 1. Create archive on Mac (ramot)

```bash
cd /Volumes/ramot/sunt/Navigation/fMRI
mkdir -p archive
# Move large optional folders (don’t delete)
mv pythontry archive/  2>/dev/null || true
mv Analysis archive/  2>/dev/null || true
mv FMRI_dep archive/  2>/dev/null || true
# Add archive/ to .gitignore if you don’t want it in the repo
echo "archive/" >> .gitignore
```

Then run **practice_session** once to confirm nothing breaks.

### 2. Create archive on PC (Sun)

When LaCie is connected (or on the fMRI computer):

```bash
cd /Volumes/LaCie/Sun   # or D:\Sun or wherever the project lives on PC
mkdir -p archive
mv fMRIEgoAlloExp archive/  2>/dev/null || true
mv fMRIEgoAlloExp-FMRI_dependencies archive/  2>/dev/null || true
mv fMRIEgoAlloExp-master.zip fMRIEgoAlloExp-FMRI_dependencies.zip archive/  2>/dev/null || true
# Optionally move analysis outputs
# mv screen_identification_output archive/  2>/dev/null || true
```

Run **fmri_session** in test mode (e.g. SubID='test', scanning=false) to confirm.

### 3. Unify and trim exploration vs exploration_trigger (optional, later)

- On PC, **exploration_trigger** is the one used by fmri_session for one_target and full_arena; **exploration** is used by run_snake_game (it cd’s there). So both folders are required on PC.
- On Mac, only **exploration** is required for practice.
- If you want, we can later add a short note at the top of run_snake_game.m (on PC) to clarify that it uses the exploration folder.

### 4. .gitignore

Ensure these are ignored so the repo stays small and clean:

- `Results/`
- `archive/`
- `*.csv`, `*.mat`, `*.xlsx` (data)
- `__pycache__/`, `*.pyc`
- `.DS_Store`, `Thumbs.db`
- Large media (e.g. `*.mp4`) if you don’t want them in Git; otherwise keep movies in repo for reproducibility.

---

## After organization

- **Mac**: Only practice-related and shared code in the main tree; run practice and confirm.
- **PC**: Only scanner-related and shared code in the main tree; run fmri_session (test mode) and confirm.
- **Git**: One repo, same layout; sync with push (Mac) and pull (PC). See **GIT_WORKFLOW.md**.

### Mac (ramot) organization completed

- **archive/** already contained: pythontry, Analysis, FMRI_dep, fMRI_codes, arenas_new_icons.
- **archive/root_extra/** was created and all other root-level extras were moved there: extra docs (INSTALLATION_GUIDE, START_HERE, etc.), analysis/visualization scripts, legacy MATLAB (PlayMovie.m, select_screen.m, etc.), paradigm/snapshot figures, questionnaire files, data files (xlsx, csv, mat), duplicate fixation images, .qodo, cross.pptx. Root now keeps only: practice_session.m, fmri_session.m, combine_session_data.m, setup_experiment.m, install_dependencies.py, requirements.txt, README.md, EXPERIMENT_REQUIREMENTS.md, FOLDER_ORGANIZATION_PLAN.md, GIT_WORKFLOW.md, exploration/, PTSOD/, sounds/, movies/, cross/, Results/, archive/, .git, .gitignore.
