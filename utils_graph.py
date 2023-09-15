import numpy as np
import json
import os

np.random.seed(42)

class Node:
    def __init__(self, id=0, concept=None, type="other") -> None:
        self.id = id
        self.concept = concept
        self.parents = {} # {id: [rel, qst]}
        self.children = {} # {id: [rel, qst]]}
        self.type = type
        self.multi_parents = [] # [[(id1, id2), qst], ...]
        self.multi_children = [] # [[(id1, id2), qst], ...]
    
    def to_dict(self):
        return {
            "id": self.id,
            "multi_parents": self.multi_parents,
            "multi_children": self.multi_children,
            "concept": self.concept,
            "parents": self.parents,
            "children": self.children,
            "type": self.type
        }
        
    def from_dict(self, d):
        self.concept = d["concept"]
        self.parents = d["parents"]
        self.children = d["children"]
        self.id = d["id"]
        self.type = d["type"] if "type" in d else "other"
        self.multi_parents = d["multi_parents"] if "multi_parents" in d else []
        self.multi_children = d["multi_children"] if "multi_children" in d else []

class Graph:
    def __init__(self, id=0) -> None:
        self.graph_id = id
        self.nodes_num = 0
        self.nodes: dict[int, Node] = {} # dict[id: node]
        self.all_concepts: dict[str, int] = {} # dict[cocept: id]
        self.concepts_class: dict[str, list[str]] = {} # dict[type: [concepts]]
        
    def __str__(self) -> str:
        tgt = ""
        for n_id in range(self.nodes_num):
            try:
                node = self.nodes[n_id]
                tgt += f"\n= = = = || ~ ~ Node {n_id} ~ ~ || = = = =\n"
                tgt += f"Concept: {node.concept}\n"
                for id, child in node.children.items():
                    cpt = self.nodes[int(id)].concept
                    tgt += f"Child {id}: {child[1]}; Answer: {cpt}\n"
            except:
                # because some nodes may be deleted during generation
                continue
        return tgt
                
    def add_multiple_nodes(self, num=1):
        for _ in range(num):
            self.nodes[self.nodes_num] = Node(self.nodes_num)
            self.nodes_num += 1
        # return the last added node id
        return self.nodes_num - 1
    
    def add_one_node(self, concept, type):
        # add the first root node
        self.nodes[self.nodes_num] = Node(self.nodes_num, concept, type)
        self.all_concepts[concept.lower()] = self.nodes_num
        if type not in self.concepts_class:
            self.concepts_class[type] = []
        self.concepts_class[type].append(concept)
        self.nodes_num += 1
        # return the added node id
        return self.nodes_num - 1
        
    def add_rel(self, par_id, ch_id, rel_to_ch, rel_to_par=None, qst_to_ch=None, qst_to_par=None):
        # if the relationship already exists, then we do not need to add.
        # The previously added relationship is always right!
        if ch_id not in self.nodes[par_id].children:
            self.nodes[par_id].children[ch_id] = [rel_to_ch, qst_to_ch]
        if par_id not in self.nodes[ch_id].parents:
            self.nodes[ch_id].parents[par_id] = [rel_to_par, qst_to_par]
        
    def store(self, path):
        f = open(path, "w")
        f.write(json.dumps({"graph_id": self.graph_id, "nodes_num": self.nodes_num, "all_concepts": self.all_concepts, "concepts_class": self.concepts_class}) + "\n")
        for id, node in self.nodes.items():
            f.write(json.dumps(node.to_dict()) + "\n")
        f.close()
        
    def load(self, path):
        f = open(path, "r")
        lines = f.readlines()
        self.graph_id = json.loads(lines[0])["graph_id"]
        self.nodes_num = json.loads(lines[0])["nodes_num"]
        try: # because previouly constructed graphs doesn't have it
            self.all_concepts = json.loads(lines[0])["all_concepts"]
        except:
            self.all_concepts = None
        try:
            self.concepts_class = json.loads(lines[0])["concepts_class"]
        except:
            self.concepts_class = None
        
        for line in lines[1:]:
            d = json.loads(line)
            node = Node(d["id"])
            node.from_dict(d)
            self.nodes[node.id] = node
        f.close()
        
    def dfs_path_ch(self, st, ed, path=[]):
        path = path + [st]
        if st == ed:
            return path
        for id in self.nodes[st].children.keys():
            if id not in path:
                newpath = self.dfs_path_ch(id, ed, path)
                if newpath:
                    return newpath
        return None
    
    # find all the paths that have the length hop
    def dfs_gather_hop(self, st_id, hop, path_ids=[], path_qst=[""], path_ans=[]):
        path_ids = path_ids + [st_id]
        path_ans = path_ans + [self.nodes[st_id].concept]
        if hop == 0:
            return [path_ids], [path_qst], [path_ans]
        all_ids = []
        all_qst = []
        all_ans = []
        multi_children_qst = [child[1] for child in self.nodes[st_id].multi_children]
        for id, rels in self.nodes[st_id].children.items():
            id = int(id)
            # We do not want a loop
            if id in path_ids:
                continue
            # We also omit questions that may cause multiple answers
            if rels[1] in multi_children_qst:
                continue
            ori_qst = path_qst.copy()
            ori_qst.append(rels[1])
            path_ids_sub, path_qst_sub, path_ans_sub = self.dfs_gather_hop(id, hop-1, path_ids, ori_qst, path_ans)
            all_ids += path_ids_sub
            all_qst += path_qst_sub
            all_ans += path_ans_sub
        return all_ids, all_qst, all_ans
    
    # find all the paths that have the length hop
    def dfs_gather_hop_parents(self, st_id, hop, path_ids=[], path_qst=[], path_ans=[]):
        path_ids = [st_id] + path_ids
        path_ans = [self.nodes[st_id].concept] + path_ans
        if hop == 0:
            return [path_ids], [[""] + path_qst], [path_ans]
        all_ids = []
        all_qst = []
        all_ans = []
        for id, rels in self.nodes[st_id].parents.items():
            id = int(id)
            # We do not want a loop
            if id in path_ids:
                continue
            # We need to get the question from the parent
            par_node = self.nodes[id]
            # We also omit questions that may cause multiple answers
            par_node_qst = par_node.children[str(st_id)][1]
            multi_children_qst = [child[1] for child in par_node.multi_children]
            if par_node_qst in multi_children_qst:
                continue
            
            ori_qst = path_qst.copy()
            ori_qst = [par_node_qst] + ori_qst
            path_ids_sub, path_qst_sub, path_ans_sub = self.dfs_gather_hop_parents(id, hop-1, path_ids, ori_qst, path_ans)
            all_ids += path_ids_sub
            all_qst += path_qst_sub
            all_ans += path_ans_sub
        return all_ids, all_qst, all_ans
    
    # find all the questions that fulfills the requirement
    def dfs_gather_triangle(self, par1_id, par2_id, ch_id, par1_hop, par2_hop, child_hop):
        par1_ids, par1_qst, par1_ans = self.dfs_gather_hop_parents(par1_id, par1_hop)
        qa_pairs_par1 = [[(qst, ans, id) for id, qst, ans in zip(par1_ids[i], par1_qst[i], par1_ans[i])] for i in range(len(par1_ids))]
        par2_ids, par2_qst, par2_ans = self.dfs_gather_hop_parents(par2_id, par2_hop)
        qa_pairs_par2 = [[(qst, ans, id) for id, qst, ans in zip(par2_ids[i], par2_qst[i], par2_ans[i])] for i in range(len(par2_ids))]
        child_ids, child_qst, child_ans = self.dfs_gather_hop(ch_id, child_hop)
        qa_pairs_child = [[(qst, ans, id) for id, qst, ans in zip(child_ids[i], child_qst[i], child_ans[i])] for i in range(len(child_ids))]
        # begin to ensemble the chains and check
        all_chains = []
        for qa_par1 in qa_pairs_par1:
            for qa_par2 in qa_pairs_par2:
                for qa_child in qa_pairs_child:
                    all_ids = []
                    for group in qa_par1:
                        all_ids.append(group[2])
                    for group in qa_par2:
                        all_ids.append(group[2])
                    for group in qa_child:
                        all_ids.append(group[2])
                    if len(list(set(all_ids))) != len(all_ids):
                        continue
                    
                    chain_dict = {
                        "par1": [[group[0], group[1]] for group in qa_par1],
                        "par2": [[group[0], group[1]] for group in qa_par2],
                        "child": [[group[0], group[1]] for group in qa_child]
                    }
                    all_chains.append(chain_dict)
        return all_chains
    
    # do in an iterative way
    def delete_node(self, id):
        for par_id in self.nodes[id].parents.copy().keys():
            del self.nodes[par_id].children[id]
        for ch_id in self.nodes[id].children.copy().keys():
            self.delete_node(ch_id)
        del self.nodes[id]
        self.nodes_num -= 1
        
    def expand_nodes(self, rules, cur_id, depth=5, max_node_num=200, save_path=None):
        # expand the graph to a certain depth
        # rules: decide the next hop based on which type
        # cur_id: the current node id
        # depth: the maximum depth of the graph
        # max_node_num: the maximum number of nodes in the graph
        # return: the number of nodes in the graph
        # if the graph is already expanded, then return the number of nodes in the graph
        if self.nodes_num >= max_node_num:
            return self.nodes_num
        if depth == 0:
            return self.nodes_num
        # expand the graph
        cur_concept = self.nodes[cur_id].concept
        cur_type = self.nodes[cur_id].type
        # if the type is other
        if cur_type not in rules:
            return self.nodes_num
        all_new_ids = []
        # first investigate into the multi_rules
        if cur_type in rules["multi_rules"]:
            multi_rels = rules["multi_rules"][cur_type] # [[template, empty_type, target_type, prompt_question], ...]
            new_nodes = 0
            for multi_rel in multi_rels:
                if multi_rel[1] not in self.concepts_class:
                    continue
                all_empty_concepts = self.concepts_class[multi_rel[1]]
                # if the only concept is itself, then skip
                if len(all_empty_concepts) == 1 and all_empty_concepts[0] == cur_concept:
                    continue
                qst = multi_rel[3].replace("[]", str(all_empty_concepts)).replace("##", cur_concept)
                # Choose valid ones from existing concepts
                valid_concepts = choose_answers(qst)
                if valid_concepts == "N/A":
                    continue
                
                for valid_concept in valid_concepts:
                    if valid_concept.lower() not in self.all_concepts:
                        continue
                    qst = multi_rel[0].replace("[]", valid_concept).replace("##", cur_concept)
                    ans_list = get_answer_three_times(qst)
                    ans_list = refine_answer(qst, ans_list)
                    # if still we cannot get the question
                    if "N/A" in ans_list:
                        continue
                    # the ids of two parents
                    par_id1 = cur_id
                    par_id2 = self.all_concepts[valid_concept.lower()]
                    
                    # enumerate the answers (may be multiple in answer list)
                    valid_children_ids = []
                    for ans in ans_list:
                        # First: if the child node already exists
                        if ans.lower() in self.all_concepts:
                            ch_id = self.all_concepts[ans.lower()]
                            # check: the answer shouldn't be the concept itself!
                            if ch_id == cur_id:
                                continue
                            # check: if the triangle relationship already exists
                            exist = False
                            for parents in self.nodes[ch_id].multi_parents:
                                if par_id1 in parents[0] and par_id2 in parents[0]:
                                    exist = True
                                    break
                            if exist:
                                continue
                            # finally we add the realtionship
                            self.add_rel(par_id1, ch_id, multi_rel[0].replace("[]", valid_concept), None, qst, None)
                            self.add_rel(par_id2, ch_id, multi_rel[0].replace("[]", valid_concept), None, qst, None)
                            # we should only get the relationship from the qst in child node
                            self.nodes[ch_id].multi_parents.append([(par_id1, par_id2), qst])
                            # add this to the valid children ids
                            valid_children_ids.append(ch_id)
                            continue
                        
                        # # For balance, do not generate too much new nodes
                        # if new_nodes >= 4:
                        #     continue
                        # new_nodes += 1
                        
                        # If not exsited, then add a new node
                        ch_id = self.add_one_node(ans, multi_rel[2])
                        all_new_ids.append(ch_id)
                        # add the edge (relationship), do not need to check duplication
                        self.add_rel(par_id1, ch_id, multi_rel[0].replace("[]", valid_concept), None, qst, None)
                        self.add_rel(par_id2, ch_id, multi_rel[0].replace("[]", valid_concept), None, qst, None)
                        # same, we should only get the relationship from the qst in child node
                        self.nodes[ch_id].multi_parents.append([(par_id1, par_id2), qst])
                        # add this to the valid children ids
                        valid_children_ids.append(ch_id)
                    
                    # then we need to add the relationship for multiple children
                    if len(valid_children_ids) > 1:
                        self.nodes[par_id1].multi_children.append([valid_children_ids, qst])
                        self.nodes[par_id2].multi_children.append([valid_children_ids, qst])
                    
        # Next: we work on single relationship
        all_rels = rules[cur_type]
        np.random.shuffle(all_rels)
        for rel in all_rels[:]: # rel: [relationship, type]
            qst = form_question(cur_concept, rel[0])
            ans_list = get_answer_three_times(qst)
            ans_list = refine_answer(qst, ans_list)
            # invalid relationship
            if "N/A" in ans_list:
                continue
            
            valid_children_ids = []
            for ans in ans_list:
                # child node already exists!
                if ans.lower() in self.all_concepts:
                    ch_id = self.all_concepts[ans.lower()]
                    # the answer shouldn't be the concept itself!
                    if ch_id == cur_id:
                        continue
                    # we do not want the parent relationship
                    self.add_rel(cur_id, ch_id, rel[0], None, qst, None)
                    valid_children_ids.append(ch_id)
                    continue
                # add a new node
                ch_id = self.add_one_node(ans, rel[1])
                all_new_ids.append(ch_id)
                # then add the edge (relationship)
                self.add_rel(cur_id, ch_id, rel[0], None, qst, None)
                valid_children_ids.append(ch_id)
            
            # then we need to add the relationship for multiple children
            if len(valid_children_ids) > 1:
                self.nodes[cur_id].multi_children.append([valid_children_ids, qst])
            
        # store every time
        self.store(save_path)
        
        # begin to iterate, expand on other nodes
        np.random.shuffle(all_new_ids)
        for ch_id in all_new_ids:
            self.expand_nodes(rules, ch_id, depth-1, max_node_num, save_path)
        
        return self.nodes_num
    

# ================================================================
# Start of the supporting functions
# ================================================================


# ================================================================
# Please change the function to be used here!
from utils_model import chat_api, mpt_api
# used for all assistance functioning
gen_func = chat_api
if os.environ.get("MODEL") == "MPT":
    # used for answering questions, reflecting which model's mind
    print("PKG of MPT model")
    ans_func = mpt_api
elif os.environ.get("MODEL") == "GPT3.5":
    # used for answering questions, reflecting which model's mind
    print("PKG of GPT3.5 model")
    ans_func = chat_api
else:
    raise Exception("Model name unsupported")
# ================================================================


def get_answer(qst, temperature=0.3):
    messages = [
        {"role": "system", "content": "You are supposed to answer the question given by the user in a succinct way. Please do not provide any additional information.\n1. If you do not know the answer for sure, please generate 'Not Sure'.\n2.If you think there are multiple answers, please split them by semicolon (;)"},
        {"role": "user", "content": "### Instruction\nAnswer the question briefly, and please always provide an answer."},
        {"role": "user", "content": "### What's the capital of USA?"},
        {"role": "assistant", "content": "Washington DC"},
        {"role": "user", "content": "### Jackson Chen is born in which city?"},
        {"role": "assistant", "content": "Not Sure"},
        {"role": "user", "content": "### What are the colors on the national flag of China?"},
        {"role": "assistant", "content": "Red; Yellow"},
        {"role": "user", "content": "### What is the longitude of Washington DC round to integer?"},
        {"role": "assistant", "content": "77W"},
        {"role": "user", "content": "### Who is the headmaster of Yale University in 2000?"},
        {"role": "assistant", "content": "Richard C. Levin"},
        {"role": "user", "content": f"### {qst}"},
    ]
    print("--- answering questions ---")
    # Choose from web_chat, web_davinci
    res = ans_func(temperature=temperature, messages=messages)
    ans = res.split("###")[0].strip().split(";")
    ans = [a.strip() for a in ans]
    print(ans)
    return ans


def judge_consistency(ans_list):
    messages = [
        {"role": "system", "content": "You are supposed to judge if the given concepts are consistent (consistent doesn't mean the same, alias is allowed).\n1. If they are consistent, then please generate the common concept they share, otherwise, please generate 'N/A'.\n2. If there are multiple concepts in one list, you can list all the concepts shared the same meaning in all the lists, and discard other inconsistent ones. Please separate answers in semicolon (;)"},
        {"role": "user", "content": "### Instruction\nGive the core concept if the there exist one that is shared / consistent in all the lists, otherwise, please generate 'N/A'."},
        {"role": "user", "content": "### ['The state is Georgia'], ['Georgia'], ['State of Georgia']"},
        {"role": "assistant", "content": "Georgia"},
        {"role": "user", "content": "### ['1945'], ['year of 1948']"},
        {"role": "assistant", "content": "N/A"},
        {"role": "user", "content": "### ['Google', 'Apple'], ['Google', 'Apple Inc.'], ['Apple', 'Google', 'Microsoft']"},
        {"role": "assistant", "content": "Google; Apple"},
        {"role": "user", "content": "### ['Not Sure'], ['The answer should be French.'], ['I am not sure about the answer, please provide more information.']"},
        {"role": "assistant", "content": "N/A"},
        {"role": "user", "content": "### ['Red', 'Blue'], ['blue', 'yellow']"},
        {"role": "assistant", "content": "Blue"},
        {"role": "user", "content": "### ['LA'], ['Los Angeles'], ['The city that Jackson lives in is L.A.']"},
        {"role": "assistant", "content": "Los Angeles"},
        {"role": "user", "content": f"### {ans_list[0]}, {ans_list[1]}"},
    ]
    
    if len(ans_list) == 3:
        messages[-1]["content"] = f"### {ans_list[0]}, {ans_list[1]}, {ans_list[2]}"
        
    print("--- judge consistency ---")
    res = gen_func(temperature=0.3, messages=messages)
    ans_list = res.split("###")[0].strip().split(";")
    ans_list = [a.strip() for a in ans_list]
    print(ans_list)
    return ans_list

# We use 2/3 majority voting to eliminate unsure
def get_answer_three_times(qst):
    answers = []
    temperature = 0.3
    for _ in range(3):
        ans = get_answer(qst, temperature)
        temperature += 0.2
        if "Not Sure" in ans:
            continue
        answers.append(ans)
        
    if len(answers) < 2:
        return "N/A"
    concept = judge_consistency(answers)
    if "N/A" in concept:
        return "N/A"
    return concept

def form_question(sbj, rel):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given the subject and the relationship. You need to use these two information to form a question."},
        {"role": "user", "content": f"### Instruction\nPlease form a question based on the information given."},
        {"role": "user", "content": "### (China, is the country in which continent)"},
        {"role": "assistant", "content": "China is the in which continent?"},
        {"role": "user", "content": "### (Jackson, go to which university in undergraduate)"},
        {"role": "assistant", "content": "Which university did Jackson attend in undergraduate?"},
        {"role": "user", "content": "### (42E, is a longitude in which time zone (UTC))"},
        {"role": "assistant", "content": "Which time zone (in UTC) does 42E belong to?"},
        {"role": "user", "content": f"### ({sbj}, {rel})"},
    ]
    print("--- creating questions ---")
    res = gen_func(temperature=0.3, messages=messages)
    qst = res.split("###")[0].strip()
    print(qst)
    return qst

def choose_answers(qst):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a list and you should choose all the answers that fulfill the requirement from the list, separated by comma. If there is no answer, then please respond 'N/A'."},
        {"role": "user", "content": "### Instruction\nPlease choose the answer that fulfill the requirement, or provide N/A if none of it fullfill the requirement."},
        {"role": "user", "content": "### Choose from [China, India] some countries that is in Europe."},
        {"role": "assistant", "content": "N/A"},
        {"role": "user", "content": "### Choose from [Notre-Dame Cathedral, Bird Nest, The Palace of Versailles] some buildings that is already built before the year 1920."},
        {"role": "assistant", "content": "Notre-Dame Cathedral, The Palace of Versailles"},
        {"role": "user", "content": "### Choose from [1982, 2003, 1600BCE, 1900, 2020] with some years that Brazil has already hosted the World Cup."},
        {"role": "assistant", "content": "1982, 2003, 2020"},
        {"role": "user", "content": "### Choose from [China, Japan, Brazil] with some countries that has invaded China."},
        {"role": "assistant", "content": "Japan"},
        {"role": "user", "content": f"### {qst}"},
    ]
    print("--- choosing answers for multiple questions ---")
    res = gen_func(temperature=0.3, messages=messages)
    if "N/A" in res.strip():
        return "N/A"
    try:
        ans = res.split("###")[0].strip().split(",")
        ans = [a.strip() for a in ans]
    except:
        try:
            ans = eval(res.split("###")[0].strip())
        except:
            return "N/A"
    print(ans)
    return ans

# new version of refine that supports multiple children
def refine_answer(qst, ans):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given the a question and answer list, and need to refine all the answers in the list into a concept or N/A."},
        {"role": "user", "content": f"### Instruction\nPlease extract the most important concept in each answer in the answer list to solve question.\n1. If none of the answer is provided or is valid, then respond with N/A.\n2. If there are multiple valid answers, separate in semicolon (;)\n3. Keep all the refined answer concepts short."},
        {"role": "user", "content": "### Question: What's the national anthem of USA?\n### Answer list: ['The Star-Spangled Banner']\n### Refined Answers:"},
        {"role": "assistant", "content": "The Star-Spangled Banner"},
        {"role": "user", "content": "### Question: Which country locates in the west of Japan?\n### Answer list: ['People's Republic of China', 'Korea']"},
        {"role": "assistant", "content": "China; Korea"},
        {"role": "user", "content": "### Question: What is the longitude of Washington DC?\n### Answer list: ['77W']"},
        {"role": "assistant", "content": "77W"},
        {"role": "user", "content": "### Question: Who is the leader/emperor in China in 7900 BC?\n### Answer list: ['Sorry, but there is not concept of leader/emperor in China in 7900 BC.']"},
        {"role": "assistant", "content": "N/A"},
        {"role": "user", "content": "### Question: Who wins the Nobel Prize in Physics in 1989?\n### Answer list: ['It is shared by three people Norman F. Ramsey, Hans G. Dehmelt and Wolfgang Paul']"},
        {"role": "assistant", "content": "Norman F. Ramsey; Hans G. Dehmelt; Wolfgang Paul"},
        {"role": "user", "content": "### Question: Which city is the capital of China?\n### Answer list: ['Beijing']"},
        {"role": "assistant", "content": "Beijing"},
        {"role": "user", "content": f"### Q: {qst} A: {ans}"},
    ]
    print("--- refining QA ---")
    try:
        res = gen_func(temperature=0.3, messages=messages)
        ans = res.split("###")[0].strip().split(";")
        ans = [a.strip() for a in ans]
        print("After Refine:")
        print(ans)
        return ans
    except:
        return "N/A"
