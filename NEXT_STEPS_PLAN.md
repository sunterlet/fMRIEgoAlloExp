# Next steps (plan for tomorrow)

Two main tasks, in order.

---

## 1. Consolidate to exploration_trigger (behavioral PC + scanner)

**Goal:** Use a single folder (**Sun/exploration_trigger/**) for both practice and scanner, so **exploration/** can be removed.

### 1.1 On the behavioral PC

- Check whether **fMRI/practice_session.m** can run using scripts from **Sun/exploration_trigger/** instead of **fMRI/exploration/**.
  - Currently: `practice_session.m` does `addpath(fullfile(pwd, 'exploration'))` and calls `run_snake_game`, etc. Those MATLAB wrappers live in **exploration** on Mac (or would need to come from exploration_trigger).
  - To test: point practice to **exploration_trigger** (e.g. addpath exploration_trigger, and ensure the same entry points exist there: `run_snake_game`, and any one_target/full_arena wrappers if practice uses them).
- Ensure the **shimming snake** call in **Sun/fmri_session.m** runs the snake from **Sun/exploration_trigger/** (not exploration).
  - Currently: **Sun/exploration_trigger/run_snake_game.m** does `exploration_dir = fullfile(current_dir, 'exploration')`, then `cd(exploration_dir)` and runs `snake.py` from there. So the Python snake is still in **exploration**.
  - Change needed: in **run_snake_game.m**, use **exploration_trigger** as the working directory and run **exploration_trigger/snake.py** (so no dependency on exploration/).

**If both work:** you can delete the **exploration** directory and keep only **exploration_trigger** for all tasks (practice + scanner, snake + one_target + full_arena).

---

## 2. Apply 3D first-person (vection) paradigm to exploration_trigger

**Goal:** Use the 3D first-person view arena from the vection experiment in the main exploration_trigger tasks.

- **Source:** **fMRI/exploration/vection_experiment/**
  - **snake_vection.py** – vection + target game, first-person movement in darkness with floor dot grid; **no trigger handling**.
  - **snake_copy.py**, **run_vection.py**, **run_vection_pygame.py** – supporting/alternative runners.
  - README, requirements, sounds, results.
- **Target:** Apply the 3D first-person view arena to:
  - **Sun/exploration_trigger/snake.py**
  - **Sun/exploration_trigger/one_target.py**
  - **Sun/exploration_trigger/multi_arena.py**

So: merge the vection/3D first-person rendering and arena logic from **vection_experiment** (e.g. snake_vection.py) into the exploration_trigger scripts, and keep/add **trigger handling** in those scripts (snake, one_target, multi_arena) so they remain usable in the scanner.

---

## Summary

| Step | What | Outcome |
|------|------|--------|
| 1.1 | Behavioral PC: practice_session.m with Sun/exploration_trigger | One folder for practice + scanner |
| 1.2 | Sun/fmri_session shimming snake uses Sun/exploration_trigger/snake.py | run_snake_game.m uses exploration_trigger, not exploration |
| 1.3 | If 1.1 & 1.2 OK | Delete **exploration** directory |
| 2   | Port vection 3D first-person to exploration_trigger (snake, one_target, multi_arena) | New paradigm in scanner-ready scripts with trigger handling |
