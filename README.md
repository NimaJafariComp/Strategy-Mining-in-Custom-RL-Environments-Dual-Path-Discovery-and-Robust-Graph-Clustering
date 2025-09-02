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

```plaintext
rl-hasse-clustering/
├─ README.md
├─ LICENSE
├─ requirements.txt
├─ paper_link.txt
├─ .gitignore
│
├─ game/
│  ├─ v2/
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
│  │  ├─ assets/
│  │  │  ├─ tiles/      # garden_maze.tmx, .tsx, .json
│  │  │  └─ sprites/    # doors, keys, rock, explosive, coin, openDoor, player, cb.png
│  │  └─ game_data/
│  │     ├─ screenshot1.png
│  │     ├─ legend1.png
│  │     └─ player_data.json
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
│     ├─ assets/
│     │  ├─ tiles/      # garden_maze.tmx, .tsx, .json
│     │  └─ sprites/    # doors, keys, rock, explosive, coin, openDoor, player, cb.png
│     └─ game_data/
│        ├─ screenshot1.png
│        ├─ legend1.png
│        └─ player_data.json
│
├─ training/
│  ├─ checkpoints/
│  │  ├─ v2/
│  │  │  ├─ ppo_project_gamev4.zip
│  │  │  ├─ ppo_project_gamev5.zip
│  │  │  └─ runs/ (final_run_v4.json, final_run_v5.json)
│  │  └─ v3/
│  │     ├─ ppo_project_gamev1.zip
│  │     ├─ ppo_project_gamev5.zip
│  │     └─ runs/ (final_runv1.json)
│
├─ data/
│  ├─ v2/
│  │  ├─ raw/        (final_run.json)
│  │  ├─ processed/  (sequence_of_sets_formatted.csv, sequence_of_sets_formatted_Won.csv)
│  │  └─ corrupted/  (corrupted_medium_10pct.csv)
│  └─ v3/
│     ├─ raw/        (final_run.json)
│     ├─ processed/  (sequence_of_sets_formatted.csv, sequence_of_sets_formatted_Won.csv)
│     └─ corrupted/  (corrupted_medium_10pct.csv)
│
├─ preprocessing/
│  ├─ v2/notebooks/
│  │  ├─ removeTheMove.ipynb
│  │  ├─ removeTheSelectItem.ipynb
│  │  ├─ filterFailedINteractions.ipynb
│  │  ├─ seqOfSets.ipynb
│  │  └─ corruptData.ipynb
│  └─ v3/notebooks/
│     ├─ removeTheMove.ipynb
│     ├─ removeTheSelectItem.ipynb
│     ├─ filterFailedINteractions.ipynb
│     ├─ seqOfSets.ipynb
│     └─ corruptData.ipynb
│
├─ dependency_matrices/
│  ├─ v2/
│  │  ├─ Alg_Most_Rel_W.py
│  │  ├─ newAlgV4.py
│  │  └─ outputs/
│  │     ├─ M_c_matrices_e1_e2_e5_e6_game_won.json
│  │     └─ M_c_matrices_e1_e2_e5_e6_corrupted10pct.json
│  └─ v3/
│     ├─ Alg_Most_Rel_W.py
│     ├─ newAlgV4.py
│     └─ outputs/
│        ├─ M_c_matrices_e1_e2_e5_e6_e11_game_won.json
│        └─ M_c_matrices_e1_e2_e5_e6_e11_corrupted10pct.json
│
└─ clustering/
   ├─ v2/
   │  ├─ dbscan.py
   │  ├─ custom_clustering.py
   │  ├─ graphG.py
   │  ├─ posets_n4.json
   │  └─ hasse/
   │     ├─ hasse.py
   │     ├─ graphG_hasse.py
   │     ├─ hasse_diagrams_n4.json
   │     └─ hasse_diagrams_n5.json
   └─ v3/
      ├─ dbscan.py
      ├─ custom_clustering.py
      ├─ graphG.py
      ├─ posets_n5.json
      └─ hasse/
         ├─ hasse.py
         ├─ graphG_hasse.py
         └─ hasse_diagrams_n5.json
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
