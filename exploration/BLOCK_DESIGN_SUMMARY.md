# Block Design Summary: Snake and Multi-Arena Experiment

## 🎯 Overview

This document summarizes the updated block design for the fMRI experiment combining Snake and Multi-Arena tasks, now incorporating the new arenas from `Final_New_Arenas.csv`.

## 📊 Arena Assignments

### 🏠 Practice Arenas (Outside Magnet)
- **Garden**: Rose, Butterfly, Pond, Gazebo, Bush
- **Beach**: Shell, Seagull, Wave, Sandcastle, Crab  
- **Village**: House, Church, Shop, Street, Lamp

### 🧠 fMRI Arenas (Inside Magnet)
- **Ranch**: Sheep, Donkey, Shed, Gate, Straw
- **Zoo**: Lion, Elephant, Gorilla, Giraffe, Seal
- **School**: Blackboard, Book, Teacher, Playground, Cafeteria
- **Hospital**: Doctor, Bed, Medicine, Stethoscope, Ambulance
- **Bookstore**: Bookshelf, Clerk, Computer, Chair, Magazine
- **Gym**: Treadmill, Weights, Trainer, Pool, Basketball

## 🔄 Block Design Sequence

### Practice Session (Outside Magnet)
1. **Snake Practice**: Game up to score of 7
2. **Multi-Arena Practice**: 3 arenas (Garden, Beach, Village)
   - Each arena: 1 training trial, 2 dark training trials, 3 test trials

### fMRI Session (Inside Magnet) - 6 Blocks
1. **Block 1**: Snake (Score target: 3)
2. **Block 2**: Multi-Arena - Ranch
3. **Block 3**: Snake (Score target: 3)
4. **Block 4**: Multi-Arena - Zoo
5. **Block 5**: Snake (Score target: 3)
6. **Block 6**: Multi-Arena - School

## 📁 File Structure

```
exploration/
├── full_sequence_snake_multi_arena.m    # Updated block design script
├── Final_New_Arenas.csv                 # New arena data
├── multi_arena.py                       # Updated to use new arenas
├── snake.py                             # Snake game script
├── sounds/
│   └── arenas/                          # New sound directory structure
│       ├── garden/
│       ├── beach/
│       ├── village/
│       ├── ranch/
│       ├── zoo/
│       ├── school/
│       ├── hospital/
│       ├── bookstore/
│       ├── gym/
│       ├── museum/
│       ├── airport/
│       └── market/
└── arena_visualizations/                # Arena layout visualizations
    ├── all_arenas_overview.jpg
    ├── garden_arena.jpg
    ├── beach_arena.jpg
    └── ... (all arena visualizations)
```

## 🎮 Key Features

### ✅ Arena Separation
- **Practice arenas** are completely different from **fMRI arenas**
- No overlap between practice and test environments
- Ensures participants don't have prior exposure to test arenas

### ✅ Block Design
- **6 total blocks** in fMRI session
- **Alternating pattern**: Snake → Multi-Arena → Snake → Multi-Arena → Snake → Multi-Arena
- **Progress tracking**: Shows "1/6", "2/6", etc. for each block

### ✅ Multi-Arena Features
- **5 targets per arena** with unique Hebrew audio
- **3.3m diameter circular arenas**
- **Practice mode**: 1 training + 2 dark training + 3 test trials
- **fMRI mode**: 1 test trial per block

### ✅ Snake Features
- **Practice mode**: Score target of 7
- **fMRI mode**: Score target of 3
- **Continuous logging**: Tracks exploration path and target locations

## 🎵 Audio System

### Sound Files
- **Format**: `.wav` files (converted from `.mp3`)
- **Content**: Hebrew speech for each target
- **Location**: `sounds/arenas/<arena_name>/`
- **Naming**: `<target_name>.wav` (e.g., `rose.wav`, `sheep.wav`)

### Audio Channels
- **Single channel system**: All sounds (beep + target) use same audio channel
- **Consistent routing**: Ensures sounds play on same screen
- **Reserved channel**: `pygame.mixer.set_reserved(1)`

## 📊 Data Logging

### Continuous Logging
- **Snake**: Player position, target locations, collection events
- **Multi-Arena**: Player movement, target interactions, annotation data

### Discrete Logging
- **Trial summaries**: Completion times, accuracy, performance metrics
- **File naming**: `<participant>_<mode>_log.csv`

## 🚀 Usage Instructions

### Running the Experiment

1. **Start MATLAB** in the fMRI directory
2. **Run the block design**:
   ```matlab
   full_sequence_snake_multi_arena
   ```
3. **Enter participant ID** when prompted
4. **Complete practice sessions** (outside magnet)
5. **Press Enter** to start fMRI sessions
6. **Follow block sequence** automatically

### Arena Customization

To change arena assignments, edit `full_sequence_snake_multi_arena.m`:

```matlab
% Practice arenas
practice_arenas = {'garden', 'beach', 'village'};

% fMRI arenas  
fmri_arenas = {'ranch', 'zoo', 'school', 'hospital', 'bookstore', 'gym'};
```

## 🔧 Technical Updates

### Multi-Arena Script Updates
- **CSV loading**: Now uses `Final_New_Arenas.csv` with fallback to original
- **Sound loading**: Updated to use `sounds/arenas/` directory structure
- **4-column support**: Handles theme, target, coords, hebrew_name format
- **Backward compatibility**: Still works with old 3-column format

### Arena Data Format
```csv
theme,target,coords,hebrew_name
garden,Rose,(0.11; 0.63),ורד
garden,Butterfly,(-0.70; 0.19),פרפר
...
```

## 📈 Expected Outcomes

### Practice Session
- **Duration**: ~15-20 minutes
- **Arenas**: 3 practice arenas (Garden, Beach, Village)
- **Trials**: 18 total trials (6 per arena)

### fMRI Session  
- **Duration**: ~30-45 minutes
- **Blocks**: 6 blocks total
- **Arenas**: 3 fMRI arenas (Ranch, Zoo, School)
- **Trials**: 6 total trials (1 per block)

## 🎯 Quality Assurance

### ✅ Verified Components
- [x] All 12 arenas load correctly
- [x] Sound files available for all targets
- [x] Practice and fMRI arenas are different
- [x] Block design sequence is correct
- [x] Progress tracking works
- [x] Audio routing is consistent
- [x] Data logging is functional

### 🔄 Available Arenas
- **Used in design**: 6 arenas (3 practice + 3 fMRI)
- **Remaining available**: 6 arenas (Hospital, Bookstore, Gym, Museum, Airport, Market)
- **Future expansion**: Can easily add more blocks or change arena assignments

---

**Last Updated**: Block design incorporates new arenas with complete separation between practice and fMRI sessions. 