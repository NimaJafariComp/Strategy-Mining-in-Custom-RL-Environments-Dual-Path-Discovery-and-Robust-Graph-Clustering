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

5. **Clustering & Analysis**  
   - **Hasse-based clustering (ours)**: consensus + high coverage combinations.  
   - **Baselines**: DBSCAN, hierarchical clustering.  
   - Robustness: format-preserving corruption of 10% episodes.  

6. **Findings**  
   - Hasse clustering is more accurate and robust: recovers true strategies even with corruption.  
   - Distance-based methods fragment into noisy clusters or drift.  

---

## 📂 Repository Layout

```plaintext
game-rl-hasse/
├─ README.md
├─ .gitignore
├─ requirements.txt
│
├─ game/                   # Environments, assets, utils
│  ├─ v2/                  # Game v2 env + reward shaping
│  └─ v3/                  # Game v3 env + reward shaping
│
├─ training/               # PPO training + checkpoints
│  ├─ train_ppo.py
│  ├─ continue_training.py
│  ├─ eval_policy.py
│  └─ checkpoints/
│     ├─ v2/
│     └─ v3/
│
├─ data/                   # Raw + processed logs
│  ├─ v2/
│  │  ├─ raw/
│  │  ├─ processed/
│  │  └─ corrupted/
│  └─ v3/
│     ├─ raw/
│     ├─ processed/
│     └─ corrupted/
│
├─ preprocessing/          # Cleaning logs, seqOfSets, corruption
│  ├─ seq_of_sets.py
│  ├─ corrupt_data.py
│  ├─ sort_by_outcome.py
│  └─ notebooks/
│     ├─ removeTheMove.ipynb
│     ├─ removeTheSelectItem.ipynb
│     ├─ filterFailedInteractions.ipynb
│     └─ corruptData.ipynb
│
├─ dependency_matrices/    # Build M_c matrices
│  ├─ new_alg_v4.py
│  ├─ outputs/
│  │  ├─ v2/
│  │  └─ v3/
│  └─ notebooks/
│     └─ newAlgV4_demo.ipynb
│
├─ clustering/             # Clustering algorithms
│  ├─ hasse/
│  │  ├─ hasse_clustering.py
│  │  ├─ consensus_and_coverage.py
│  │  └─ figures/
│  ├─ dbscan_clustering.py
│  ├─ hierarchical_clustering.py
│  ├─ custom_graph_clustering.py
│  └─ outputs/
│     ├─ v2/
│     └─ v3/
│
├─ figures/                # Screenshots + clustering figures
│  ├─ v2/
│  └─ v3/
│
└─ paper_link.txt          # Link to the published paper



> Note: *Game v2 with move* is intentionally excluded.

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
