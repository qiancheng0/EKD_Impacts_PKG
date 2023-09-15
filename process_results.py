import os
import json
from IPython import embed

files = os.listdir("results")
for file in files:
    path = f"results/{file}"
    lines = open(path, "r").readlines()
    for line in lines:
        data = json.loads(line)
        new_data = {}
        for hop_key, hop_dict in data.items():
            new_data[hop_key] = {}
            for k, v in hop_dict.items():
                new_data[hop_key][k] = {}
                if "1_1_0" not in file and "1_1_1" not in file and "1_2_0" not in file:
                    new_cond = []
                    for cond in v["answer_condition"]:
                        if cond == 2:
                            new_cond.append(4)
                        else:
                            new_cond.append(cond)
                    new_data[hop_key][k]["answer_condition"] = new_cond
                    new_data[hop_key][k]["confidence"] = v["confidence"]
                else:
                    for k_p, v_p in v.items():
                        if k_p == "model_response":
                            continue
                        new_data[hop_key][k][k_p] = {}
                        new_cond = []
                        for cond in v_p["answer_condition"]:
                            if cond == 2:
                                new_cond.append(4)
                            else:
                                new_cond.append(cond)
                        new_data[hop_key][k][k_p]["answer_condition"] = new_cond
                        new_data[hop_key][k][k_p]["confidence"] = v_p["confidence"]
                
                new_data[hop_key][k]["model_response"] = v["model_response"]
                            
        
        f = open(f"results_new/{file}", "a")
        f.write(json.dumps(new_data) + "\n")
        f.close()

                