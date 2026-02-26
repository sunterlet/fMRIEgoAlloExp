# Experiment requirements (derived from actual usage)

This document lists **only what you actually use** for the experiment, so we can keep those files and treat everything else as optional/archive.

---

## Your workflow (summary)

| Step | Where | What you run / use |
|------|--------|---------------------|
| **1. Practice** (outside scanner) | **Behavioral PC** (behavioral experiment rooms) | `practice_session.m`. |
| **2. In scanner** | **fMRI PC** (scanner computer) | Open `fixation.pptx`, then run `fmri_session.m`. |

**Machines and network:**

- **Mac** = development; you edit scripts here. Mac and **behavioral PC** are on the same network, so you can open/run the same project from both (e.g. shared drive or synced folder).
- **Behavioral PC** = runs **practice** only (`practice_session.m`); uses **exploration** (not exploration_trigger).
- **fMRI PC** = runs the **scanner session** only; not on the shared network, so you sync via LaCie (or copy) to get the latest scripts onto the fMRI PC. Uses **exploration_trigger** (and exploration for the snake).

Mac vs PC matters for paths and line endings (CRLF on Windows). Practice uses **exploration**; scanner uses **exploration_trigger** (and exploration for the snake).

---

## 1. Scanner session (PC) – source of truth: `Sun/fmri_session.m`

Everything below is required for the in-scanner protocol on the **PC**.

### 1.1 Entry point and display

| Item | Purpose |
|------|--------|
| `fmri_session.m` | Main script; runs the full fMRI protocol. |
| `fixation.pptx` | Shown between tasks (manual; open in PowerPoint). |

### 1.2 Directly called by `fmri_session.m`

| Call | Source | Notes |
|------|--------|-------|
| `run_snake_game('shimming', ...)` | Wrapper lives in **exploration_trigger**; inside it, `exploration_dir = fullfile(pwd, 'exploration')` and `cd(exploration_dir)` (see **exploration_trigger/run_snake_game.m** around lines 26–35), then runs the Python snake from there. | Scanner needs both **exploration_trigger** (for the .m wrapper) and **exploration** (the folder that gets cd’d into). |
| `PTSODfunc_SplitRuns_fMRI_New(...)` | `PTSOD/Code` | PTSOD task, run 1 and run 2. |
| `one_target_run(...)` | `exploration_trigger/one_target_run.m` | Calls Python in **exploration_trigger**. |
| `multi_target_run(...)` | `exploration_trigger/multi_target_run.m` | Calls Python in **exploration_trigger**. |
| `PlayMovie_Scaled(SubID, 'TheShining.mp4', ...)` | Root: `PlayMovie_Scaled.m` | Needs movies folder. |
| `PlayMovie_Scaled(SubID, 'MissionImpossible.mp4', ...)` | Same | |
| `combine_session_data(SubID)` | Root: `combine_session_data.m` | Runs after session. |

**To test (simplification):** Try running the Python snake from **exploration_trigger** instead of **exploration** in `exploration_trigger/run_snake_game.m` (change `exploration_dir = fullfile(current_dir, 'exploration')` to `fullfile(current_dir, 'exploration_trigger')` and `cd(exploration_dir)`). If that works, the scanner would only need **exploration_trigger** (no separate **exploration** folder), and the setup would be unified.



### 1.3 Paths added in `fmri_session.m` (all required on PC)

- `PTSOD/Code`
- `exploration_trigger`
- `sounds`

### 1.4 Other files/folders required on PC (from the calls above)

| Path | Purpose |
|------|--------|
| **exploration_trigger/** | MATLAB wrappers (run_snake_game.m, one_target_run.m, multi_target_run.m) and Python scripts for one_target and multi_target. |
| **exploration/** | Used by run_snake_game (it does `cd` into `exploration` to run the snake Python). So scanner needs this folder too. |
| **PTSOD/Code** | PTSOD experiment code. |
| **PTSOD/Instructions_HE** | Instruction images (e.g. instructions_practice_fmri1/*.png). |
| **PTSOD/Stimuli** | Stimulus images (memory_screens_HE, nomemory_screens_HE, etc.). |
| **sounds/** | Audio used by tasks. |
| **movies/** | At least `TheShining.mp4`, `MissionImpossible.mp4` for PlayMovie_Scaled. |
| **Results/** | Created at runtime; centralized results dir. |

### 1.5 Scanner-only scripts (PC)

These exist only (or mainly) on the scanner and are needed there:

- `PlayMovie_Scaled.m` (used by fmri_session)
- `fixation.pptx`

### 1.6 Software dependencies (PC)

- **MATLAB** (with Psychtoolbox)
- **Python** (used by exploration_trigger and exploration; e.g. `py` or `python` on Windows)
- **Serial port** (for scanner trigger; `com` in fmri_session, e.g. `'com4'`)
- **PowerPoint** (or equivalent) for fixation.pptx

---

## 2. Practice session (behavioral PC) – entry point: `practice_session.m`

Practice runs on the **behavioral PC** in the behavioral experiment rooms (not on the Mac or the fMRI computer). Mac and behavioral PC share the same network, so you can open the same scripts on both; the fMRI PC is not on that network, so it gets scripts via LaCie. The following is what practice needs on the **behavioral PC** (same layout as the project on Mac/network).

### 2.1 Entry point

| Item | Purpose |
|------|--------|
| `practice_session.m` | Runs all practice (snake, PTSOD, one target, multi-arena). |

### 2.2 Paths added in `practice_session.m` (behavioral PC)

- `PTSOD/Code`
- **exploration** (not exploration_trigger)
- `sounds`

### 2.3 Functions called from practice (Mac)

- `run_snake_game('practice', ...)` — from **exploration** (Mac has no exploration_trigger).
- `PTSODfunc_SplitDays_fMRI_New(...)` or `PTSODfunc_SplitRuns_fMRI_New(...)` (depending on which practice_session.m you actually use).
- `run_one_target('practice', ...)` — from exploration.
- `run_multi_target('practice', ...)` — from exploration.

So on **Mac** you need:

- **exploration/** (with run_snake_game, run_one_target, run_multi_target and their Python scripts)
- **PTSOD/Code**, **PTSOD/Instructions_HE**, **PTSOD/Stimuli**
- **sounds/**
- **Results/** (practice writes here)

Practice is run on the behavioral PC only; the fMRI PC does not have (or need) `practice_session.m`.

---

## 3. Summary: minimal required layout

### On the **scanner (PC)** – for `fmri_session.m` + fixation.pptx

```
Sun/  (or same structure on PC)
├── fmri_session.m
├── combine_session_data.m
├── PlayMovie_Scaled.m
├── fixation.pptx
├── exploration_trigger/     # MATLAB wrappers + Python for one_target, multi_target
├── exploration/             # Used by run_snake_game for snake
├── PTSOD/
│   ├── Code/
│   ├── Instructions_HE/
│   └── Stimuli/
├── sounds/
├── movies/
│   ├── TheShining.mp4
│   └── MissionImpossible.mp4
└── Results/                 # Created at run time
```

Optional on PC: `fix_overscan.m`, `select_screen_with_screenshots.*` if you use them.

### On the **behavioral PC** (and Mac if opening from network) – for `practice_session.m`

```
fMRI/
├── practice_session.m
├── exploration/             # Same logical content as scanner’s exploration (for snake/one_target/multi_arena)
├── PTSOD/
│   ├── Code/
│   ├── Instructions_HE/
│   └── Stimuli/
├── sounds/
└── Results/
```

---

## 4. What we can derive for “organization”

- **Keep**: Everything listed above (per machine).
- **Optional / archive**: Anything not referenced by `practice_session.m` (behavioral PC) or `fmri_session.m` (fMRI PC), e.g.:
  - Old copies of scripts (e.g. `fmri_session.m` on Mac if you never run it there).
  - Test scripts, analysis scripts that are not run during the live experiment.
  - `pythontry/`, duplicate or legacy versions of tasks.
  - One-off docs/figures that are not needed to run practice or scanner.

Next step: **FOLDER_ORGANIZATION_PLAN.md** will list concrete folders/files to **keep** vs **archive** and a single clean structure you can aim for on both Mac and PC (with Mac vs PC differences noted where relevant).
