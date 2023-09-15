import json
import numpy as np
from cprint import *
import multiprocessing
from timeout_decorator import timeout
import os

np.random.seed(42)
set_timeout = 300

@timeout(set_timeout)
def exec_with_timeout(args, result_queue: multiprocessing.Queue, index):
    try:
        result = get_ans_auto_round_straight(*args)
        result_queue.put((index, result))
    except Exception as e:
        cprint.err(e)
        result_queue.put((index, None))

# =========================== parameters ===========================
# Format is single sentence (short) / paragraph (long)
os.environ["FORMAT"] = prompt_type = "short" # or "long"
os.environ["MODEL"] = "GPT3.5"

from utils_process import *

for cur_hop in ["2", "3", "4"]:
    lines = open(f'./data_chains/chatgpt_straight_{cur_hop}hop.json', 'r').readlines()
    save_path = f"./results/chatgpt_straight_{cur_hop}hop.json"
# =========================== parameters ===========================

    valid = 0
    for cur_num, line in enumerate(lines):
        cprint.info("=== in a new line ===")
        data = json.loads(line)
        all_info_dict = data["all_info_dict"]
        
        log_dict = {}
        # Begin asking questions
        for i, all_info in enumerate(all_info_dict):
            cprint.info(f"~~~ in hop{i+1} ~~~")
            log_dict[f"hop{i+1}"] = {}
                
            parameters_list = []
            processes:list[multiprocessing.Process] = []
            names = ["mis_info_dict_light", "mis_info_dict_severe", "hall_sbj_dict_light", "hall_sbj_dict_severe", "unrelated_fact_dict_light", "unrelated_fact_dict_severe"]
            result_queue = multiprocessing.Queue()
            re_run_ids = []
            # Add all the parameters
            for j in [3, 4, 5, 6, 7, 8]:
                mis_statement = all_info[j][0] if prompt_type == "short" else all_info[j][-1]
                parameters_list.append((all_info_dict, mis_statement, all_info[j][1]))
            # Start all the processes
            for j, params in enumerate(parameters_list):
                process = multiprocessing.Process(target=exec_with_timeout, args=(params, result_queue, j))
                processes.append(process)
                process.start()
            # Wait for all the processes to finish
            for process in processes:
                process.join(timeout=set_timeout)
            # Get the results 
            while not result_queue.empty():
                index, result = result_queue.get()
                if result:
                    log_dict[f"hop{i+1}"][names[index]] = result
                    cprint.info(f"Task completed: {names[index]}")
                    cprint.info(f"Result: {result}")
                else:
                    cprint.warn(f"Task {names[index]} timeout!")
            # Check if all the tasks are completed
            for name in names:
                if name not in log_dict[f"hop{i+1}"]:
                    re_run_ids.append(names.index(name)+3)
                    
            cprint.info("============ Concurrent Done ===========")
            cprint.info(f"Re-run ids: {re_run_ids}")
                
            if len(re_run_ids) == 0:
                continue
            parameters_list = []
            for j in re_run_ids:
                assert names[j-3] not in log_dict[f"hop{i+1}"]
                mis_statement = all_info[j][0] if prompt_type == "short" else all_info[j][-1]
                log_dict[f"hop{i+1}"][names[j-3]] = get_ans_auto_round_straight(all_info_dict, mis_statement, all_info[j][1])
            assert(len(log_dict[f"hop{i+1}"]) == 6)
            cprint.info("============ Re-run Done ===========")

        f = open(save_path, 'a')
        f.write(json.dumps(log_dict) + '\n')
        f.close()
        
        valid += 1

    print("Valid:", valid)
    