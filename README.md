the paper instead of including LaTeX files.

# RL-Hasse-Clustering

This repository contains the code and data for our paper:  
**“From Reinforcement Learning Trajectories to Strategy Posets: Hasse-based Clustering of Dependency Matrices.”**  
📄 [Read the paper here](https://link-to-your-paper.com)  

We introduce a full pipeline that goes from reinforcement learning trajectories in custom puzzle environments to interpretable procedural strategies using a novel **Hasse diagram–based clustering algorithm**. We compare this to standard unsupervised learning (DBSCAN, hierarchical clustering) and test robustness under controlled data corruption.

---

## 🚀 Overview

**Pipeline at a glance:**

1. **Custom Puzzle Games**  
   - *Game v2*: one solution (explosive → rock → key → door).  
   - *Game v3*: two solutions (door path or treasure path).  

2. **Reinforcement Learning**  
   - PPO (Stable-Baselines3) with reward shaping + curriculum.  

3. **Data Mining**  
   - Clean logs → symbolic event codes → infinity-ratio analysis.  

4. **Dependency Matrices**  
   - Per winning episode, capture temporal relations among key events.  

5. **Unsupervised Machine Learning**  
   - **Hasse-based clustering (ours)**: consensus + high coverage combinations.  
   - **Baselines**: DBSCAN, hierarchical clustering.  
   - Robustness: format-preserving corruption of 10% episodes.  

6. **Findings**  
   - Hasse clustering is more accurate and robust: recovers true strategies even with corruption.  
   - Distance-based methods fragment into noisy clusters or drift.  

---

## 📂 Repository Layout

> Note: some large raw data files were compressed into `.zip` archives for upload.

```plaintext
rl-hasse-clustering/
├─ LICENSE
├─ paper_link.txt
├─ README.md
├─ requirements.txt
├─ .git
│
├─ clustering/
│  ├─ v2/
│  │  ├─ density based clustering.py
│  │  ├─ graphG.py
│  │  ├─ new clustering.py
│  │  ├─ posets_n4.json
│  │  └─ hasse/
│  │     ├─ graphG_hasse.py
│  │     ├─ hasse clustering.py
│  │     ├─ hasse_diagrams_n4.json
│  │     └─ hasse_diagrams_n5.json
│  └─ v3/
│     ├─ density based clustering.py
│     ├─ graphG.py
│     ├─ new clustering.py
│     ├─ posets_n5.json
│     └─ hasse/
│        ├─ graphG_hasse.py
│        ├─ hasse clustering.py
│        └─ hasse_diagrams_n5.json
│
├─ data/
│  ├─ v2/
│  │  ├─ corrupted/
│  │  │  └─ corrupted_medium_10pct.csv
│  │  ├─ processed/
│  │  │  ├─ sequence_of_sets_formatted.csv
│  │  │  └─ sequence_of_sets_formatted_Won.csv
│  │  └─ raw/
│  │     └─ final_run.json   # (compressed in .zip for upload if large)
│  └─ v3/
│     ├─ corrupted/
│     │  └─ corrupted_medium_10pct.csv
│     ├─ processed/
│     │  ├─ sequence_of_sets_formatted.csv
│     │  └─ sequence_of_sets_formatted_Won.csv
│     └─ raw/
│        └─ final_run.json   # (compressed in .zip for upload if large)
│
├─ dependency_matrices/
│  ├─ v2/
│  │  ├─ Alg_Most_Rel_W.py
│  │  ├─ newAlgV4.py
│  │  └─ outputs/
│  │     ├─ M_c_matrices_diagonal_1 ('e1', 'e2', 'e5', 'e6') corrupted10%.json
│  │     └─ M_c_matrices_diagonal_1 ('e1', 'e2', 'e5', 'e6') game_won.json
│  └─ v3/
│     ├─ Alg_Most_Rel_W.py
│     ├─ newAlgV4.py
│     └─ outputs/
│        ├─ M_c_matrices_diagonal_1 ('e1', 'e2', 'e5', 'e6', 'e11') corrupted10%.json
│        └─ M_c_matrices_diagonal_1 ('e1', 'e2', 'e5', 'e6', 'e11') game_won.json
│
├─ game/
│  ├─ v2/
│  │  ├─ alg 5 python.py
│  │  ├─ projectGame.py
│  │  ├─ projectGame2.py
│  │  ├─ rl_env.py
│  │  ├─ train_agent.py
│  │  ├─ train_continue.py
│  │  ├─ utils.py
│  │  ├─ interactable.py
│  │  ├─ item.py
│  │  ├─ player.py
│  │  ├─ coin.py
│  │  ├─ garden_maze.json
│  │  ├─ garden_maze.tmx
│  │  ├─ garden_maze.tsx
│  │  ├─ key.png / key_blue.png / key_green.png / key_purple.png / key_red.png
│  │  ├─ blue_door.png / green_door.png / purple_door.png / red_door.png
│  │  ├─ explosive.png / rock.png / coin_image.png / openDoor.png / cb.png
│  │  ├─ matrixfinder5.java
│  │  ├─ ppo_project_gamev4.zip
│  │  ├─ ppo_project_gamev5.zip
│  │  └─ game_data/
│  │     ├─ final_run_v5.json
│  │     ├─ legend1.png
│  │     ├─ player_data.json
│  │     └─ screenshot1.png
│  │
│  └─ v3/
│     ├─ projectGame3.py
│     ├─ rl_env.py
│     ├─ train_agent.py
│     ├─ train_continue.py
│     ├─ utils.py
│     ├─ interactable.py
│     ├─ item.py
│     ├─ player.py
│     ├─ coin.py
│     ├─ garden_maze.json
│     ├─ garden_maze.tmx
│     ├─ garden_maze.tsx
│     ├─ key.png / key_blue.png / key_green.png / key_purple.png / key_red.png
│     ├─ blue_door.png / green_door.png / purple_door.png / red_door.png
│     ├─ explosive.png / rock.png / coin_image.png / openDoor.png / cb.png
│     ├─ ppo_project_gamev1.zip
│     ├─ ppo_project_gamev5.zip
│     └─ game_data/
│        ├─ final_runv1.json
│        ├─ legend1.png
│        ├─ player_data.json
│        └─ screenshot1.png
│
├─ preprocessing/
│  ├─ v2/notebooks/
│  │  ├─ corruptData.ipynb
│  │  ├─ filterFailedINteractions.ipynb
│  │  ├─ removeTheMove.ipynb
│  │  ├─ removeTheSelectItem.ipynb
│  │  └─ seqOfSets.ipynb
│  └─ v3/notebooks/
│     ├─ corruptData.ipynb
│     ├─ filterFailedINteractions.ipynb
│     ├─ removeTheMove.ipynb
│     ├─ removeTheSelectItem.ipynb
│     └─ seqOfSets.ipynb
│
└─ training/
   ├─ checkpoints/
     ├─ v2/
     │  ├─ final_run_v4.json
     │  ├─ final_run_v5.json
     │  ├─ ppo_project_gamev4.zip
     │  └─ ppo_project_gamev5.zip
     │   
     └─ v3/
        ├─ final_runv1.json
        └─ ppo_project_gamev1.zip
        
---
## ⚙️ Requirements

- Python 3.10+  
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3)  
- [Gym / Gymnasium](https://gymnasium.farama.org/)  
- Pygame, pytmx (map rendering)  
- Numpy, Pandas, Scipy  
- Scikit-learn (DBSCAN, hierarchical)  
- NetworkX (graph + Hasse analysis)  
- Matplotlib  

Install dependencies with:

```bash
pip install -r requirements.txt
```
▶️ Quick Start
1. Train PPO agent
# Train Game v2
```bash
python training/train_ppo.py --env v2 --timesteps 5000000
```
# Train Game v3
```bash
python training/train_ppo.py --env v3 --timesteps 5000000
```
2. Preprocess logs
```bash
python preprocessing/seq_of_sets.py \
  --input data/v2/raw/final_run.json \
  --output data/v2/processed/sequence_of_sets_formatted.csv
```
4. Build dependency matrices
```bash
python dependency_matrices/new_alg_v4.py \
  --input data/v2/processed/sequence_of_sets_formatted_won.csv \
  --output dependency_matrices/outputs/v2/M_c_matrices_game_won.json
```
6. Run clustering
# Hasse clustering (ours)
```bash
python clustering/hasse/hasse_clustering.py --env v2
```
# DBSCAN
```bash
python clustering/dbscan_clustering.py --env v2 --eps 2.0
```
# Hierarchical
```bash
python clustering/hierarchical_clustering.py --env v2 --threshold 2.5
```
📊 Results (Summary)

Game v2: Hasse finds one consensus strategy (door). DBSCAN/hierarchical split into noisy sub-variants.

Game v3: Hasse separates both winning strategies (door + treasure). DBSCAN/hierarchical show variants but mis-handle incidental pickups.

Robustness: With 10% corrupted sequences, Hasse consensus unchanged. Distance-based methods fragment or degenerate.
