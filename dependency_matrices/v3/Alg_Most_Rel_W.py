import ast
import pandas as pd
import os
from collections import defaultdict


script_dir = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(script_dir, "sequence_of_sets_formattedV3.csv")
OUTPUT_FILE = os.path.join(script_dir, "event_pair_ordering_ratios.csv")
LABEL_COLUMN = "label"  # contains "won" or "lost"


def parse_sequence(seq_str):
    try:
        parsed = ast.literal_eval(seq_str)
        return parsed if isinstance(parsed, list) else []
    except:
        return []

# build full event set from both data
def extract_event_set(df):
    event_set = set()
    for s in df["sequence"]:
        parsed = parse_sequence(s)
        for t in parsed:
            elements = list(t) if isinstance(t, tuple) else [t]
            event_set.update(elements)
    return event_set

# identify win/loss
def is_winning_episode(seq_str):
    parsed = parse_sequence(seq_str)
    if not parsed:
        return False
    last_term = parsed[-1]
    last_events = list(last_term) if isinstance(last_term, tuple) else [last_term]
    return any(e in last_events for e in ["e9", "e12"])

# check if e_i occurs before e_j in a sequence
def occurs_before(seq, e_i, e_j):
    seen_i, seen_j = None, None
    for idx, term in enumerate(seq):
        elements = list(term) if isinstance(term, tuple) else [term]
        if e_i in elements and seen_i is None:
            seen_i = idx
        if e_j in elements and seen_j is None:
            seen_j = idx
    return (seen_i is not None and seen_j is not None and seen_i < seen_j)


df_all = pd.read_csv(CSV_FILE)
df_all["episode_won"] = df_all["sequence"].apply(is_winning_episode)
df_won = df_all[df_all["episode_won"] == True]
df_lost = df_all[df_all["episode_won"] == False]


X = sorted(list(extract_event_set(df_all)))
m = len(X)
event_index = {e: i for i, e in enumerate(X)}

# count W_ij and L_ij
W, L = defaultdict(int), defaultdict(int)

def count_orderings(df, counter_dict):
    for row in df["sequence"]:
        seq = parse_sequence(row)
        for i in range(m):
            for j in range(m):
                if i != j and occurs_before(seq, X[i], X[j]):
                    counter_dict[(i, j)] += 1

count_orderings(df_won, W)
count_orderings(df_lost, L)

total_won = len(df_won)
total_lost = len(df_lost)

# compute R_ij = W_ij / L_ij
records = []
for i in range(m):
    for j in range(m):
        if i == j:
            continue
        w_ij = W.get((i, j), 0) / total_won if total_won else 0
        l_ij = L.get((i, j), 0) / total_lost if total_lost else 0
        if l_ij == 0:
            R = float("inf") if w_ij > 0 else 0
        else:
            R = w_ij / l_ij

        records.append({
            "i": X[i],
            "j": X[j],
            "W_ij": round(w_ij, 4),
            "L_ij": round(l_ij, 4),
            "R_ij": R
        })

df_result = pd.DataFrame(records).sort_values(by="R_ij", ascending=False)
df_result.to_csv(OUTPUT_FILE, index=False)

print(f"Saved R_ij table to: {OUTPUT_FILE}")
print(df_result.head(10))
