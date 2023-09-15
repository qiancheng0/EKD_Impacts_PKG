import json
from utils_process import get_paragraph_context
from utils_process import get_misinformation_light, get_misinformation_severe, get_unrelated_subject_light, get_unrelated_subject_severe, get_unrelated_info_light, get_unrelated_info_severe
import numpy as np
from tqdm import tqdm
import concurrent.futures
from functools import partial
import os

# ====================== Parameters =========================
os.environ["MODEL"] = "GPT3.5" # or MPT
model = "chatgpt" # or mpt
wanted_num = 25
# ====================== Parameters =========================

from utils_graph import Graph
np.random.seed(42)

def get_dict(QA_pairs):
    all_info_dict = []
    for qa_hop in QA_pairs:
        Q, A = qa_hop
            
        functions_list = [get_misinformation_light, get_misinformation_severe, get_unrelated_subject_light, get_unrelated_subject_severe, get_unrelated_info_light, get_unrelated_info_severe]
        # Using ThreadPoolExecutor for parallel execution within threads
        with concurrent.futures.ThreadPoolExecutor() as executor:
            [statement_original, mis_ans_light, mis_info_light],\
            [statement_original, mis_ans_severe, mis_info_severe],\
            [hall_fact_light, hall_sbj_light],\
            [hall_fact_severe, hall_sbj_severe],\
            [unrelated_fact_light, unrelated_sbj_light, unrelated_ans_light],\
            [unrelated_fact_severe, unrelated_sbj_severe, unrelated_ans_severe],\
                = list(executor.map(lambda func: func(Q, A), functions_list))
                    
        parameters_list = [[mis_info_light], [mis_info_severe], [hall_fact_light], [hall_fact_severe], [unrelated_fact_light], [unrelated_fact_severe]]
            
        with concurrent.futures.ThreadPoolExecutor() as executor:
            partial_function = partial(get_paragraph_context)
            mis_info_news_light, mis_info_news_severe,\
            hall_sbj_news_light, hall_sbj_news_severe,\
            unrelated_fact_news_light, unrelated_fact_news_severe\
                = list(executor.map(partial_function, *zip(*parameters_list)))
                    
        # form a dictionary
        all_info_dict.append(
            (Q, A, statement_original,
            [mis_info_light, [mis_ans_light], mis_info_news_light],
            [mis_info_severe,[mis_ans_severe], mis_info_news_severe],
            [hall_fact_light, [hall_sbj_light], hall_sbj_news_light],
            [hall_fact_severe, [hall_sbj_severe], hall_sbj_news_severe],
            [unrelated_fact_light, [unrelated_sbj_light,unrelated_ans_light], unrelated_fact_news_light],
            [unrelated_fact_severe, [unrelated_sbj_severe, unrelated_ans_severe], unrelated_fact_news_severe])
        )
    return all_info_dict


# Extract all the questions that have multi-hop structures
def extract_straight_hop(g: Graph, hop, save_path):
    node_num = len(g.nodes)
    all_chains = []
    for i in tqdm(range(node_num)):
        ids, questions, answers = g.dfs_gather_hop(i, hop)
        qa_pairs = [[(qst, ans) for qst, ans in zip(questions[i],   answers[i])] for i in range(len(ids))]
        all_chains += qa_pairs
    print("Total number of chains: ", len(all_chains))
    np.random.shuffle(all_chains)
    valid = 0
    for _, chain in enumerate(all_chains):
        # Get all the information and the paragraph context
        valid += 1
        all_info_dict = get_dict(chain[1:])
        
        f = open(save_path, 'a')
        f.write(json.dumps({"all_info_dict": all_info_dict}) + '\n')
        f.close()
        if valid == wanted_num:
            break


# Extract all the questions that have multi-dependent structures
def extract_dependent_hop(g: Graph, par1_hop, par2_hop, child_hop, save_path):
    all_chains = []
    for ch_id, node in g.nodes.items():
        if node.multi_parents == None or node.multi_parents == []:
            continue
        for multi_par in node.multi_parents:
            par1_id = multi_par[0][0]
            par2_id = multi_par[0][1]
            chains = g.dfs_gather_triangle(par1_id, par2_id, ch_id, par1_hop, par2_hop, child_hop)
            for chain in chains:
                chain["triangle"] = [multi_par[1], node.concept]
            all_chains += chains
            if par1_hop != par2_hop:
                chains = g.dfs_gather_triangle(par2_id, par1_id, ch_id, par1_hop, par2_hop, child_hop)
                for chain in chains:
                    chain["triangle"] = [multi_par[1], node.concept]
                all_chains += chains
    print("Total number of chains: ", len(all_chains))
    np.random.shuffle(all_chains)
    valid = 0
    for _, chain in enumerate(all_chains): # {"par1": [[q,a],...], "par2": [[q,a],...], "triangle":[q, a], "child": [[q,a],...]}
        valid += 1
        info_dict_par1 = get_dict(chain["par1"][1:])
        info_dict_par2 = get_dict(chain["par2"][1:])
        info_dict_triangle = get_dict([chain["triangle"]])
        info_dict_child = get_dict(chain["child"][1:])
        
        all_info_dict = {
            "par1": info_dict_par1,
            "par2": info_dict_par2,
            "triangle": info_dict_triangle,
            "child": info_dict_child,
        }
        
        f = open(save_path, 'a')
        f.write(json.dumps(all_info_dict) + '\n')
        f.close()
        if valid == wanted_num:
            break

# Extract straight chains
for hop in [2, 3, 4]:
    save_path = f"./data_chains_test/{model}_straight_{hop}hop.json"
    for num in range(1, 9):
        g = Graph()
        g.load(f'./raw_graph/{model}_pkg{num}.json')
        extract_straight_hop(g, hop, save_path)
    
# Extract multi-dependent chains
for hops in [[1,1,0], [2,1,0], [1,1,1]]:
    save_path = f"./data_chains_test/{model}_dependent_{hops[0]}_{hops[1]}_{hops[2]}.json"
    for num in range(1, 9):
        g = Graph()
        g.load(f"./raw_graph/{model}_pkg{num}.json")
        extract_dependent_hop(g, hops[0], hops[1], hops[2], save_path)
