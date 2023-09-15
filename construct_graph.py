import json
import os

# ====================== Parameters =========================
os.environ['MODEL']= "MPT" # or MPT
save_name = "./raw_graph/mpt_pkg" # or mpt_pkg
rules = json.load(open("./utils/rule_simple.json", "r"))
depth = 5
max_node_num = 500

# First we only want one root node
root_dict = {
    "China": "country",
    "France": "country",
    "Sydney":"city",
    "United States": "country",
    "Cairo": "city",
    "Rio de Janeiro": "city",
    "Tokyo": "city",
    "United Kingdom": "country",
}
# ====================== Parameters =========================

from utils_graph import Graph

cnt = 10
for root_concept, root_type in root_dict.items():
    save_path = f"{save_name}{cnt}.json"
    g = Graph()
    g.add_one_node(root_concept, root_type)
    total_num = g.expand_nodes(rules, 0, depth, max_node_num, save_path)
    print(total_num)
    cnt += 1
