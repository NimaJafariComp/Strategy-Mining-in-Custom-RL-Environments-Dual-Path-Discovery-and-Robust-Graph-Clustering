import ast
import pandas as pd
import os
import numpy as np
import json

# def parse_sequence(seq_str):
#     I = {'e1', 'e2'}
#     try:
#         parsed = ast.literal_eval(seq_str)
#     except:
#         parsed = []
    
#     sequence = []
#     for term in parsed:
#         if isinstance(term, tuple):
#             filtered = [e for e in term if e in I]
#             if filtered:
#                 sequence.append(tuple(filtered))
#         elif term in I:
#             sequence.append(term)
#     return sequence

def method1(c_list):
    """Generate M_c and P^c based on the given sequence c."""
    I_order = ['e1', 'e2', 'e5', 'e6', 'e11']
    extended_order = I_order
    m = len(extended_order) #changed form i_order to extended order
    processed = []
    n = 0
    
    for c in c_list:
        P = {e: set() for e in extended_order} #changed form i_order to extended order
        for term_idx, term in enumerate(c, 1):
            elements = list(term) if isinstance(term, tuple) else [term]
            for e in elements:
                if e in P:
                    P[e].add(term_idx)
        
        M_c = [[0]*m for _ in range(m)]
        
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                P_i = P[extended_order[i]] #changed
                P_j = P[extended_order[j]] #changed
                
                if P_i and P_j and max(P_i) < min(P_j):
                    M_c[i][j] = 1
                
        processed.append((M_c, P))
        M_c_array = np.array(M_c)
        if np.any(M_c_array):
            print(M_c_array)
            n = n+1
            
    print(n)
    return processed


def method2ForProcessed(processed):
    I_order = ['e1', 'e2', 'e5', 'e6', 'e11']
    extended_order = I_order
    m = len(extended_order) #changed from I_order
    M = [[0]*m for _ in range(m)]
    
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            ei = extended_order[i]
            ej = extended_order[j]
       
            condition_a = True
            for M_c_k, P_k in processed:
                if P_k[ei] and P_k[ej]:  # Only check if both are nonempty
                    if M_c_k[i][j] != 1:
                        condition_a = False
                        break  # No need to check further if one fails
                
        

            
            condition_b = any(
                P_k[ei] and P_k[ej] and max(P_k[ei]) < min(P_k[ej])
                for _, P_k in processed
            )
            
            if condition_a and condition_b:
                M[i][j] = 1
    
    return M

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, "corrupted_medium_10pct.csv")
    df = pd.read_csv(csv_file_path)
    
    c_list = [ast.literal_eval(symptom_set) for symptom_set in df["corrupted_sequence"]]
    c_list2 = [
        ['e1', 'e5','e4'], 
        ['e1', 'e2','e4'],  # e4 before e5

    ]
    processed = method1(c_list)
    M = method2ForProcessed(processed)
    
    print("Final Matrix M:")
    for row in M:
        print(row)
        

    
    selected_Mc_and_P = []
    for M_c, P in processed:
        M_c_np = np.array(M_c)

        if np.any(M_c_np):  # selection criteria
            # Add 1s on the diagonal
            for i in range(len(M_c)):
                M_c[i][i] = 1

            # Convert P sets to sorted lists for JSON
            P_json = {k: sorted(list(P[k])) for k in P}

            selected_Mc_and_P.append({
                "M_c": M_c,
                "P": P_json
            })

    print(f"Saving {len(selected_Mc_and_P)} matrices with P")

    out_path = os.path.join(script_dir, "M_c_matrices_diagonal_1 ('e1', 'e2', 'e5', 'e6', 'e11') corrupted10%.json")
    with open(out_path, "w") as f:
        json.dump(selected_Mc_and_P, f, indent=2)

    print(f"Saved to {out_path}")


######




