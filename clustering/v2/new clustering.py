import os
import numpy as np
import pandas as pd
import json
import networkx as nx
from collections import deque
from graphG import build_graph
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from collections import defaultdict
from newAlgV4 import method2ForProcessed as M2
from pprint import pprint

script_dir = os.path.dirname(os.path.abspath(__file__))
directed_csv_path = os.path.join(script_dir, "shortest_path_directed-posets_n4.csv") #this should be changede too
df_directed = pd.read_csv(directed_csv_path, index_col=0)
directed_paths = df_directed.values

print("Precomputed directed shortest path matrix shape:", directed_paths.shape)

mc_json_path = os.path.join(script_dir, "M_c_matrices_diagonal_1 ('e1', 'e2', 'e5', 'e6') corrupted10%.json")
with open(mc_json_path, "r") as f:
    mc_matrices = json.load(f)
mc_matrices_np = [np.array(entry["M_c"]) for entry in mc_matrices]
num_mc = len(mc_matrices_np)
print("Number of M_c matrices loaded:", num_mc)

G, G_reduced = build_graph()
G_t = G_reduced

mc_to_node = {}
for idx, mc in enumerate(mc_matrices_np):
    found = False
    for node, data in G.nodes(data=True):
        if np.array_equal(mc, data['matrix']):
            mc_to_node[idx] = node
            found = True
            break
    if not found:
        raise ValueError(f"M_c matrix at index {idx} was not found in the graph G!")

print("Mapping of M_c matrices to node ids:")
print(mc_to_node)

def custom_distance_with_candidate(M_i_node, M_j_node, G_t):
    """Compute custom distance between two nodes and return the best candidate node."""
    reachable_from_Mi = set(nx.descendants(G_t, M_i_node))
    reachable_from_Mi.add(M_i_node)
    reachable_from_Mj = set(nx.descendants(G_t, M_j_node))
    reachable_from_Mj.add(M_j_node)
    candidates = reachable_from_Mi.intersection(reachable_from_Mj)
    if not candidates:
        return float('inf'), None
    min_dist = float('inf')
    best_candidate = None
    for N in candidates:
        try:
            d1 = directed_paths[M_i_node, N]
            d2 = directed_paths[M_j_node, N]
            total = d1 + d2
            if total < min_dist:
                min_dist = total
                best_candidate = N
        except nx.NetworkXNoPath:
            continue
    return min_dist, best_candidate

clusters = {}
for idx in range(num_mc):
    node = mc_to_node[idx]
    clusters[idx] = {
        'rep_node': node,
        'rep_matrix': G.nodes[node]['matrix'],
        'indices': [idx]
    }

def merge_clusters(clusters, G_t):
    """Merge clusters based on custom distances."""
    cluster_keys = list(clusters.keys())
    best_pair = None
    best_distance = float('inf')
    best_candidate = None
    for i in range(len(cluster_keys)):
        for j in range(i+1, len(cluster_keys)):
            key_i = cluster_keys[i]
            key_j = cluster_keys[j]
            rep_i = clusters[key_i]['rep_node']
            rep_j = clusters[key_j]['rep_node']
            distance, candidate = custom_distance_with_candidate(rep_i, rep_j, G_t)
            if distance < best_distance:
                best_distance = distance
                best_pair = (key_i, key_j)
                best_candidate = candidate
    #print(best_candidate)
    return best_pair, best_distance, best_candidate


clusters = {i: {'rep_node': mc_to_node[i], 'indices':[i]} 
            for i in range(num_mc)}
cluster_sizes = {i: 1 for i in range(num_mc)}
linkage_rows = []


iteration = 0
while len(clusters) > 1:
    iteration += 1
    pair, dist, candidate = merge_clusters(clusters, G_t)
    if pair is None:
        break
    if candidate is None:
        break
    #print(candidate)
    key1, key2 = pair
    print(f"Iteration {iteration}: merging clusters {key1} and {key2} with distance {dist} via candidate node {candidate}")
    new_key = max(clusters.keys()) + 1
    new_indices = clusters[key1]['indices'] + clusters[key2]['indices']
    new_rep_node = candidate
    new_rep_matrix = G.nodes[new_rep_node]['matrix']
    clusters[new_key] = {
        'rep_node': new_rep_node,
        'rep_matrix': new_rep_matrix,
        'indices': new_indices
    }
    
    size1 = cluster_sizes[key1] 
    size2 = cluster_sizes[key2]
    new_size = size1 + size2

    linkage_rows.append([ key1, key2, dist, new_size ])
    cluster_sizes[new_key] = new_size

    del clusters[key1], clusters[key2]
    del cluster_sizes[key1], cluster_sizes[key2]

    
    print(f"New cluster {new_key} contains M_c indices: {new_indices}")
    
    # Stop algorithm
    if iteration == 80: #at 77 we have 3 clusters
        # Merge ALL remaining clusters at once
        # keys = list(clusters.keys())
        # merged_indices = []
        # total_size = 0
        # for key in keys:
        #     merged_indices += clusters[key]['indices']
        #     total_size += cluster_sizes[key]
        
        # # Pick arbitrary rep_node (e.g., from first cluster)
        # rep_node = clusters[keys[0]]['rep_node']
        # new_key = max(clusters.keys()) + 1

        # # Record this big merge manually in linkage
        # # (merge the last two clusters together first, if needed)
        # while len(keys) > 1:
        #     k1 = keys.pop()
        #     k2 = keys.pop()
        #     merged_size = cluster_sizes[k1] + cluster_sizes[k2]
        #     linkage_rows.append([k1, k2, 0.0, merged_size])  # Force distance=0

        #     new_temp_key = max(clusters.keys()) + 1
        #     clusters[new_temp_key] = {
        #         'rep_node': rep_node,
        #         'rep_matrix': G.nodes[rep_node]['matrix'],
        #         'indices': clusters[k1]['indices'] + clusters[k2]['indices']
        #     }
        #     cluster_sizes[new_temp_key] = merged_size
        #     del clusters[k1], clusters[k2]
        #     del cluster_sizes[k1], cluster_sizes[k2]
        #     keys.append(new_temp_key)

        break  # Exit loop after merging everything
    
    

print("\nFinal clustering result:")
for key, cluster in clusters.items():
    print(f"Cluster {key}: indices {cluster['indices']}")

# generate matrices M2 of resulting clusters
def build_processed(indices):
    """Build the exact input format M2 expects for a given list of M_c indices."""
    return [
        (
            mc_matrices[i]["M_c"],
            {k: set(v) for k, v in mc_matrices[i]["P"].items()}
        )
        for i in indices
    ]

print("\n=== M2 results per final cluster ===")
for cid, cluster in clusters.items():
    indices = cluster['indices']
    processed = build_processed(indices)
    try:
        M_result = M2(processed)
        print(f"\nCluster {cid} | indices={indices}")
        print("M2 output:")
        pprint(M_result)
    except Exception as e:
        print(f"\nCluster {cid} | indices={indices}")
        print(f"M2 raised {type(e).__name__}: {e}")

    
# dendogram    
Z = np.array(linkage_rows)
leaf_labels = [str(i) for i in range(num_mc)]
plt.figure(figsize=(12,6))
dendrogram(
  Z,
  labels=leaf_labels,
  leaf_rotation=90,
  color_threshold=0  # or whatever cut
)
plt.xlabel("M_c matrix index")
plt.ylabel("Custom distance")
plt.title("Dendrogram of your custom clustering")
plt.tight_layout()
plt.show()
    
clusters_test = {
        10 : {
        'rep_node': mc_to_node[10],
        'rep_matrix': G.nodes[mc_to_node[10]]['matrix'],
        'indices': [10]
    },
        0 : {
        'rep_node': mc_to_node[0],
        'rep_matrix': G.nodes[mc_to_node[0]]['matrix'],
        'indices': [0]
    }
}


#s, r, candid = merge_clusters(clusters_test,G_t)
#print(candid)

# ----------------hierarchail with L1 norm------------------

vectors = np.array([mat.flatten() for mat in mc_matrices_np])
condensed_l1 = pdist(vectors, metric='cityblock')  # L1 distance vector
num_mc = len(vectors)
full_l1 = squareform(condensed_l1)

thresh = 3.0
labels = fcluster(Z, t=thresh, criterion='distance')

Z = linkage(condensed_l1, method='average')  # or 'single','complete',etc.


plt.figure(figsize=(10,5))
dendrogram(Z, labels=[str(i) for i in range(len(vectors))], leaf_rotation=90)
plt.title("Hierarchical Clustering with L1 Distance")
plt.xlabel("M_c index")
plt.ylabel("L1 distance")
plt.show()

# Print clusters
clusters_l1 = defaultdict(list)
for idx, lbl in enumerate(labels):
    clusters_l1[lbl].append(idx)

print(f"\nFinal clustering into {len(clusters_l1)} clusters (L₁ metric):\n")
for lbl, member_list in sorted(clusters_l1.items()):
    print(f"Cluster {lbl}: indices {member_list}")
    print()
    
for cluster_id in sorted(clusters_l1.keys()):
    indices = clusters_l1[cluster_id]
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
