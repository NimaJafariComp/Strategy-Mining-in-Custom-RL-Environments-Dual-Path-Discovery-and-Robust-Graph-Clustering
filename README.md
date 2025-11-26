# Strategy Mining in Custom RL Environments: Dual-Path Discovery and Robust Clustering via Hasse Diagrams

This repository contains the code and data for our paper:  
**“FROM DATA TO CONCEPTS VIA WIRING DIAGRAMS.”** by Mohammadnima Jafari and Jason Lo  
📄 [main pre-print here](https://arxiv.org/abs/2511.20138))  
📄 [Data note paper 1](https://doi.org/10.5281/zenodo.17315846), [Data note paper 2](https://doi.org/10.5281/zenodo.17315753)

We introduce a full pipeline that goes from reinforcement learning trajectories in custom puzzle environments to interpretable procedural strategies using a novel **Hasse diagram–based clustering algorithm**. We compare this to standard unsupervised learning (DBSCAN, hierarchical clustering) and test robustness under controlled data corruption.

---

## 🚀 Overview

**Pipeline at a glance:**

1. **Custom Puzzle Games**  
   - *Game v2*: one solution (explosive → rock → key → door).  
   - *Game v3*: two solutions (door path or treasure path).  

2. **Reinforcement Learning**  
   - PPO (Stable-Baselines3) with reward shaping + curriculum.  
   - Train from scratch using files under `game/v2/` or `game/v3/`.  
   - Alternatively, use provided training runs and checkpoints under `training/checkpoints/`.  

3. **Data Mining (Preprocessing)**  
   - Clean logs, filter events, convert to symbolic sequences (`seqOfSets`).  
   - Implemented in Jupyter notebooks under `preprocessing/`.  

4. **Dependency Matrices**  
   - Built with `newAlgV4.py` under `dependency_matrices/v2/` or `dependency_matrices/v3/`.  
   - Requires processed sequence CSVs from preprocessing.  

5. **Unsupervised Machine Learning (Clustering)**  
   - **Hasse-based clustering (ours)**: consensus + coverage filtering.  
   - **Baselines**: DBSCAN, hierarchical, custom clustering.  
   - Scripts are under `clustering/v2/` and `clustering/v3/`.  

6. **Findings**  
   - Hasse clustering is more accurate and robust: recovers true strategies even with corruption.  
   - Distance-based methods fragment into noisy clusters or drift.  

---

## 📂 Repository Layout

> Note: some large raw data files were compressed into `.zip` archives for upload.

```plaintext
rl-hasse-clustering/
├─ game-rl-strategy-mining-v2.pdf
├─ game-rl-strategy-mining-v3.pdf
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
│  │     └─ final_run.json
│  └─ v3/
│     ├─ corrupted/
│     │  └─ corrupted_medium_10pct.csv
│     ├─ processed/
│     │  ├─ sequence_of_sets_formatted.csv
│     │  └─ sequence_of_sets_formatted_Won.csv
│     └─ raw/
│        └─ final_run.json
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
   └─ checkpoints/
      ├─ v2/
      │  ├─ final_run_v4.json
      │  ├─ final_run_v5.json
      │  ├─ ppo_project_gamev4.zip
      │  └─ ppo_project_gamev5.zip
      └─ v3/
         ├─ final_runv1.json
         └─ ppo_project_gamev1.zip
```
⚙️ Requirements
```
Python 3.10+

Stable-Baselines3

Gym / Gymnasium

Pygame, pytmx (map rendering)

Numpy, Pandas, Scipy

Scikit-learn (DBSCAN, hierarchical)

NetworkX (graph + Hasse analysis)

Matplotlib

Jupyter Notebook (for preprocessing scripts)
```
Install dependencies with:
```
bash
Copy code
pip install -r requirements.txt
```
▶️ Usage Notes
```
Most scripts are interdependent:

To train from scratch, bring together the files in game/v2 (or game/v3) with PPO training scripts (train_agent.py, train_continue.py).

To skip training, use pre-generated logs/checkpoints under training/checkpoints/ or raw/processed data under data/.

To run preprocessing, use the Jupyter notebooks under preprocessing/ (they clean raw logs and produce sequence CSVs).

To generate dependency matrices, run newAlgV4.py under dependency_matrices/. These expect processed sequences as input.

To run clustering, first ensure dependency matrices are generated. Then run the clustering scripts under clustering/v2 or clustering/v3.

Pipeline order (from scratch):

Train agent (game/v2/train_agent.py or game/v3/train_agent.py) → produces logs.

Preprocess logs (preprocessing/v*/notebooks/seqOfSets.ipynb) → produces sequences.

Build dependency matrices (dependency_matrices/v*/newAlgV4.py) → produces M_c JSONs.

Run clustering (clustering/v*/density based clustering.py, clustering/v*/new clustering.py, clustering/v*/hasse/hasse clustering.py).

If you only want to experiment with clustering, you can use the precomputed data in data/ and dependency_matrices/outputs/.
```

📊 Results (Summary)
```
Game v2: Hasse finds one consensus strategy (door). DBSCAN/hierarchical split into noisy sub-variants. 

Game v3: Hasse separates both winning strategies (door + treasure). DBSCAN/hierarchical show variants but mis-handle incidental pickups.

Robustness: With 10% corrupted sequences, Hasse consensus unchanged. Distance-based methods fragment or degenerate.
```



## Acknowledgements

This project is based upon work supported by the Air Force Office of Scientific Research under award number FA9550-24-1-0268.


