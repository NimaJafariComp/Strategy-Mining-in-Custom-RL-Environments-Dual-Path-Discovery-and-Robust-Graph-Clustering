import os
import json
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict
from newAlgV4 import method2ForProcessed as M2
from sklearn.metrics import pairwise_distances


# a neighbor of a point p is any other point whose distance to p is ≤ ε (the radius eps).
# Density-based clustering groups points that have at least min_samples neighbors within a radius(“eps”), marking points with too few neighbors as noise

script_dir = os.path.dirname(__file__)
mc_json = os.path.join(script_dir, "M_c_matrices_diagonal_1 ('e1', 'e2', 'e5', 'e6') game_won.json")
with open(mc_json, "r") as f:
    mc_matrices = json.load(f)
    
X = np.array([np.array(entry["M_c"]).reshape(-1) for entry in mc_matrices])

# may need to experiment
eps = 1.0      # max L1-distance to be considered neighbors
min_samples = 1  # at least 2 points to form a dense region

db = DBSCAN(eps=eps, min_samples=min_samples, metric='manhattan')
labels = db.fit_predict(X)

print("DBSCAN cluster labels:")
for idx, lbl in enumerate(labels):
    print(f"  M_c index {idx:2d} → cluster {lbl}")

# display clus
clusters = defaultdict(list)
for idx, lbl in enumerate(labels):
    clusters[lbl].append(idx)

print("\nDensity-based clusters (–1 is noise):")
for lbl, members in clusters.items():
    print(f"  Cluster {lbl:2d}: M_c indices {members}")
    
# Print pairwise L1 distances inside each non-noise cluster
for lbl, members in clusters.items():
    if lbl == -1 or len(members) <= 1:
        continue  # skip noise / singletons (no pairs)

    # use the same representation DBSCAN saw (your flattened X)
    X_cluster = X[members]
    D = pairwise_distances(X_cluster, metric='manhattan')

    print(f"\nPairwise L1 distances within Cluster {lbl} (indices {members}):")
    # pretty-print full matrix
    with np.printoptions(linewidth=120, suppress=True):
        print(D)

    # also list out pair distances one per line (optional)
    for i in range(len(members)):
        for j in range(i+1, len(members)):
            print(f"  dist(M_c[{members[i]}], M_c[{members[j]}]) = {D[i, j]}")

    # check if *all* matrices in the cluster are exactly the same (distance 0 between every pair)
    # (off-diagonal zeros)
    if np.all(D[np.triu_indices_from(D, k=1)] == 0):
        print(f"  ✅ All {len(members)} matrices in Cluster {lbl} are EXACTLY identical.")
    else:
        print(f"  ❌ Not all matrices in Cluster {lbl} are identical. "
              f"Max intra-cluster L1 distance = {D[np.triu_indices_from(D, 1)].max()}")

#Cluster –1 (noise): Points that never had ≥ min_samples neighbors within eps, so they couldn’t join any dense region.

# convert loaded JSON P back into usable set form
for cluster_id, indices in clusters.items():
    print(f"\nProcessing Cluster {cluster_id} ({len(indices)} M_c entries):")

    # Prepare input for method2
    processed = [
        (
            mc_matrices[i]["M_c"],
            {k: set(v) for k, v in mc_matrices[i]["P"].items()}
        )
        for i in indices
    ]
    
    # Run method2 and display results
    M_result = M2(processed)
    print(f"Resulting matrix for cluster {cluster_id}:")
    for row in M_result:
        print(" ", row)