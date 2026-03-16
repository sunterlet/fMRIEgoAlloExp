# Path and directory flow – fmri_session and vection runs

## Directory layout (relevant parts)

```
U:\sunt\Navigation\fMRI\
├── fmri_session.m              % Main session script (run from here or from exploration)
├── PlayMovie_Scaled.m          % In fMRI root; must be on path after any cd()
├── exploration_trigger_vection\   % Vection (3D first-person) scripts
│   ├── one_target_run.m        % MATLAB wrapper → calls one_target_run.py
│   ├── multi_target_run.m      % MATLAB wrapper → calls multi_target_run.py
│   ├── one_target_run.py       % Orchestrates 6 snake + 6 one_target trials
│   ├── multi_target_run.py     % Orchestrates snake + multi_target trials (run 1/2)
│   ├── snake_vection.py
│   ├── one_target_vection.py
│   ├── multi_target_vection.py
│   ├── run_snake_vection.m, run_one_target_vection.m, run_multi_target_vection.m
│   └── Instructions-he\, sounds\, fonts\, ...
├── exploration_trigger\        % Non-vection (2D) scripts; also has wrappers
│   ├── one_target_run.m        % Same name → can shadow vection wrapper if path order wrong
│   ├── multi_target_run.m
│   ├── one_target_run.py       % Uses snake.py, one_target.py (or "vection_experiment\" subpath if vection)
│   ├── multi_target_run.py     % Uses script_name = "vection_experiment\snake_vection.py" when vection
│   ├── snake.py, one_target.py, multi_target.py
│   └── (no vection_experiment folder – vection scripts live in exploration_trigger_vection)
├── PTSOD\Code\
└── sounds\
```

## Why the error happened

- **exploration_trigger\multi_target_run.py** (wrong one when vection=true) builds:
  `vection_experiment\snake_vection.py` (relative path). That folder does not exist under exploration_trigger.
- **exploration_trigger_vection\multi_target_run.py** (correct one) builds:
  `SCRIPT_DIR + "snake_vection.py"` (absolute path), with SCRIPT_DIR = dir of the running Python script.

So the wrong script runs when MATLAB resolves `multi_target_run` to **exploration_trigger\multi_target_run.m** (e.g. if that block is run alone and exploration_trigger is first on the path). That .m does `cd(exploration_trigger)` and runs `python multi_target_run.py`, which then looks for `vection_experiment\snake_vection.py` and fails.

## Logic flow: path adding (fmri_session.m)

1. **Session root**
   - `sessionRoot = fileparts(mfilename('fullpath'))` → directory of fmri_session.m (e.g. `U:\...\fMRI`).

2. **Path order (critical for vection)**
   - `addpath(sessionRoot)` → so PlayMovie_Scaled etc. are found after any `cd()`.
   - `addpath(exploration_trigger_vection, '-begin')` → vection wrappers and their Python scripts must be found first.
   - Then: PTSOD/Code, sounds. **exploration_trigger is not added** – the session runs only from exploration_trigger_vection.

3. **If only a section is run (e.g. Multi Target Run 2)**
   - The “Add Relevant Paths” block may not have run.
   - Then `which('multi_target_run')` can point to **exploration_trigger\multi_target_run.m**.
   - So we re-assert at the start of each vection block: ensure `sessionRoot` and put `exploration_trigger_vection` at the beginning of the path.

## Logic flow: cd() and Python cwd

1. **one_target_run.m / multi_target_run.m (in exploration_trigger_vection)**
   - `exploration_dir = fileparts(which('one_target_run'))` or `which('multi_target_run')` → must be exploration_trigger_vection.
   - `cd(exploration_dir)` → MATLAB pwd = exploration_trigger_vection.
   - ProcessBuilder / subprocess: working directory for Python = exploration_dir (exploration_trigger_vection).
   - Command: `python one_target_run.py ...` or `python multi_target_run.py ...` (relative name; resolved from cwd).
   - So the Python script that runs is exploration_trigger_vection\*.py.

2. **Python (one_target_run.py / multi_target_run.py)**
   - `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` → exploration_trigger_vection.
   - `script_path = os.path.join(SCRIPT_DIR, "snake_vection.py")` etc. → absolute path inside exploration_trigger_vection.
   - Subprocess for each trial: same Python, script = that absolute path → always runs exploration_trigger_vection\snake_vection.py etc.

3. **After the run**
   - MATLAB wrappers do `cd(current_dir)` in finally/on exit → pwd restored.
   - PlayMovie_Scaled and other root scripts still work because sessionRoot is on the path.

## Summary

| Step | Who | Path / directory |
|------|-----|------------------|
| Start fmri_session | MATLAB | pwd = wherever user started; sessionRoot = dir of fmri_session.m |
| Add paths | fmri_session | sessionRoot, then exploration_trigger_vection (-begin), then others |
| Vection block (One/Multi Target Run) | fmri_session | Re-assert: addpath(exploration_trigger_vection, '-begin') so which() finds vection wrappers |
| Call one_target_run(...) / multi_target_run(...) | MATLAB | which() → exploration_trigger_vection\*.m |
| Inside wrapper | .m | exploration_dir = fileparts(which(...)); cd(exploration_dir) |
| Launch Python | ProcessBuilder | cwd = exploration_dir (exploration_trigger_vection) |
| Python main script | one_target_run.py / multi_target_run.py | __file__ in exploration_trigger_vection; SCRIPT_DIR = that dir |
| Python subprocess (trial) | subprocess | sys.executable -u &lt;absolute script_path&gt; → exploration_trigger_vection\snake_vection.py etc. |
| After run | .m | cd(current_dir) |
| Movie / PTSOD | MATLAB | pwd may be exploration_trigger_vection; PlayMovie_Scaled found via addpath(sessionRoot) |

## Fix applied

- At the start of each vection block (One Target Run, Multi Target Run 1, Multi Target Run 2) in fmri_session.m:
  - Ensure `sessionRoot` is set (for section-only runs).
  - `addpath(fullfile(sessionRoot, 'exploration_trigger_vection'), '-begin')`.
- So even when only that block is run, `which('one_target_run')` and `which('multi_target_run')` resolve to exploration_trigger_vection, and the correct Python scripts run.
