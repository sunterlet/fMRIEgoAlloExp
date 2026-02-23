# exploration_trigger: files needed for fMRI vs archive

Derived from what **fmri_session.m** actually calls: `run_snake_game`, `one_target_run`, `full_arena_run`.

---

## KEEP (required for fMRI)

### MATLAB (called by fmri_session.m)
- **run_snake_game.m** – shimming / snake
- **one_target_run.m** – one-target run
- **full_arena_run.m** – full arena run

### Python (run by the .m files or by the run scripts)
- **snake.py** – snake game (shimming: `snake.py shimming`; fmri: via snake_in.py; practice: snake_out.py)
- **snake_in.py** – snake trial in fMRI run
- **snake_out.py** – snake practice
- **one_target_run.py** – orchestrates one-target run (calls snake.py + one_target.py)
- **full_arena_run.py** – orchestrates full-arena run (calls snake.py + multi_arena.py)
- **one_target.py** – one-target task
- **multi_arena.py** – multi-arena task

### Python modules (imported by the above)
- **fixation_utils.py** – fixation cross (loads images from project root)
- **trigger_utils.py** – trigger handling
- **sound_paths.py** – unified paths for beep.wav and target.wav (exploration_trigger/sounds/)

### Data
- **Final111_New_Arenas.csv** – used by multi_arena.py
- **Final_New_Arenas.csv**, **Arenas.csv** – keep for compatibility / reference

### Assets
- **Instructions-he/** – instruction images
- **sounds/** – beep.wav, target.wav, **sounds/arenas/<name>/** for multi_arena
- **fonts/** – Gisha.ttf (one_target.py)

### Config
- **requirements.txt**
- **sound_paths.py** – single source for beep/target paths: `SOUNDS_DIR`, `BEEP_SOUND_PATH`, `TARGET_SOUND_PATH` all point to **exploration_trigger/sounds/** (snake, one_target, multi_arena import from here).

### Runtime (can be empty)
- **results/** – output dir (gitignore in repo)

---

## ARCHIVE (not needed to run fMRI)

Moved to **exploration_trigger/archive/**.

- **Docs:** README.md, README_*.md, BLOCK_DESIGN_SUMMARY.md, UNIFIED_LOGGING_README.md
- **MATLAB:** add_paths.m, combine_logs.m, full_sequence_snake_multi_arena.m, run_multi_arena.m, run_one_target.m, run_trigger_digit_test.m, trigger_manager.m, test_log_output.m, test_screen_integration.m
- **Python – generation / analysis:** check_dor_targets.py, combine_logs.py, fix_target_overlaps.py, generate_fixation_crosses.py, generate_hebrew_audio.py, generate_new_arenas.py, generate_target_locations.py, update_new_arenas.py, visualize_arenas.py
- **Python – utilities / test:** identify_screens.py, name_input.py, name_input_gui.py, play_all_hebrew_sounds.py, setup.py, snake_in_venv.py, test_*.py, test_*.m, test_*.csv, trigger_digit_test.py, unified_logging.py
- **screen_utils.py** – optional; scripts have fallback if missing. Restore from archive if you need screen-selection helper.
- **Python – legacy/io wrappers:** multi_arena_in.py, multi_arena_orig.py, multi_arena_out.py, one_target_in.py, one_target_out.py
- **Output/test data:** arena_visualizations/, test_participant_one_target_run_timing*.csv

Do not move: **.venv**, **__pycache__** (can be recreated; add to .gitignore if needed).
