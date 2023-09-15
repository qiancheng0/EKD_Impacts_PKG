import json
import sys
import os

def print_analysis(targets):
    for cur_dict in targets:
        print("\n~~~~~~~~~~ dict: {} ~~~~~~~~~~\n".format(cur_dict["name"]))
        for key, vals in cur_dict.items():
            if key == "name":
                continue
            
            print("===== key: {} =====".format(key))
            finish = 0
            invalid_deviate = 0
            correct = 0
            incorrect_deviate = 0
            total_deviate = 0
            
            # -1 is no answer, 1 is original correct answer, 3 is the target hallucinate answer (only in position i), 4 is other conjunctured answer
            confidence = []
            conf_crt = []
            conf_deviate = []
            for val in vals:
                # If confidence provided
                for i, conf in enumerate(val[1]):
                    if conf != -1:
                        confidence.append(conf)
                    if val[0][i] == 1 and conf != -1:
                        conf_crt.append(conf)
                    if val[0][i] == 3 and conf != -1:
                        conf_deviate.append(conf)
                    
                # Normal callculation of results
                val = val[0]
                if val[-1] != -1:
                    finish += 1
                elif 3 in val:
                    invalid_deviate += 1
                
                if val[-1] == 1:
                    correct += 1
                elif val[-1] != -1 and 3 in val:
                    incorrect_deviate += 1
                
                if 3 in val:
                    total_deviate += 1
            
            print("total consistent rate: {}, total: {}, ratio: {}".format(correct, len(vals), round(correct/len(vals) * 100, 2)))
            print("error: abstention rate: {}, total: {}, ratio: {}".format(len(vals)-finish, len(vals)-correct, round((len(vals)-finish)/(len(vals)-correct) * 100, 2)))
            if len(vals) != finish:
                print("       - deviate: {}, invalid ratio: {}, total ratio: {}".format(invalid_deviate, round(invalid_deviate/(len(vals)-finish) * 100, 2), round(invalid_deviate/len(vals) * 100, 2)))
            print("error:  variation rate: {}, total: {}, ratio: {}".format(finish-correct, len(vals)-correct, round((finish-correct)/(len(vals)-correct) * 100, 2)))
            if finish != correct:
                print("       - deviate: {}, invalid ratio: {}, total ratio: {}".format(incorrect_deviate, round(incorrect_deviate/(finish-correct) * 100, 2), round(incorrect_deviate/len(vals) * 100, 2)))
            print("total_deviate rate: {}, total: {}, ratio: {}".format(total_deviate, len(vals), round(total_deviate/len(vals) * 100, 2)))
            
            if len(confidence) != 0:
                print(f"average confidence: {round(sum(confidence)/len(confidence) * 100, 2)}")
            if len(conf_crt) != 0:
                print(f"average confidence of correct: {round(sum(conf_crt)/len(conf_crt) * 100, 2)}")  
            if len(conf_deviate) != 0:
                print(f"average confidence of deviation: {round(sum(conf_deviate)/len(conf_deviate) * 100, 2)}")


stdout = sys.stdout

# ====================== Parameters =========================
root_path = "./results"
save_path = "./analysis"
# ====================== Parameters =========================

os.makedirs(save_path, exist_ok=True)
files = os.listdir(root_path)

for file in files:
    if "1_1_0" in file or "1_2_0" in file or "1_1_1" in file or ".py" in file:
        continue
    sys.stdout = open(f"{save_path}/{file[:-5]}.txt", "w")
    lines = open(os.path.join(root_path, file), "r").readlines()
    
    degree_analysis_dict = {"name": "degree analysis", "Type Match": [], "Type Shift": []}
    position_analysis_dict = {"name": "position analysis"}
    method_analysis_dict = {"name": "method analysis", "Object": [], "Subject": [], "Unrelated": []}

    # {all_info, hop1:[6 dicts], hop2, ...}
    for cue_line_num, line in enumerate(lines):
        data = json.loads(line)
        for key, hop_dict in data.items():
            if "hop" not in key:
                continue
            
            if key not in position_analysis_dict:
                position_analysis_dict[key] = []
            
            hop_dict = data[key]
            mis_info_light = hop_dict["mis_info_dict_light"]["answer_condition"], hop_dict["mis_info_dict_light"]["confidence"]
            mis_info_severe = hop_dict["mis_info_dict_severe"]["answer_condition"], hop_dict["mis_info_dict_severe"]["confidence"]
            hall_sbj_light = hop_dict["hall_sbj_dict_light"]["answer_condition"], hop_dict["hall_sbj_dict_light"]["confidence"]
            hall_sbj_severe = hop_dict["hall_sbj_dict_severe"]["answer_condition"], hop_dict["hall_sbj_dict_severe"]["confidence"]
            unrelated_fact_light = hop_dict["unrelated_fact_dict_light"]["answer_condition"], hop_dict["unrelated_fact_dict_light"]["confidence"]
            unrelated_fact_severe = hop_dict["unrelated_fact_dict_severe"]["answer_condition"], hop_dict["unrelated_fact_dict_severe"]["confidence"]
            
            degree_analysis_dict["Type Match"].append(mis_info_light)
            degree_analysis_dict["Type Match"].append(hall_sbj_light)
            degree_analysis_dict["Type Match"].append(unrelated_fact_light)
            degree_analysis_dict["Type Shift"].append(mis_info_severe)
            degree_analysis_dict["Type Shift"].append(hall_sbj_severe)
            degree_analysis_dict["Type Shift"].append(unrelated_fact_severe)
            
            position_analysis_dict[key].append(mis_info_light)
            position_analysis_dict[key].append(mis_info_severe)
            position_analysis_dict[key].append(hall_sbj_light)
            position_analysis_dict[key].append(hall_sbj_severe)
            position_analysis_dict[key].append(unrelated_fact_light)
            position_analysis_dict[key].append(unrelated_fact_severe)
            
            method_analysis_dict["Object"].append(mis_info_light)
            method_analysis_dict["Object"].append(mis_info_severe)
            method_analysis_dict["Subject"].append(hall_sbj_light)
            method_analysis_dict["Subject"].append(hall_sbj_severe)
            method_analysis_dict["Unrelated"].append(unrelated_fact_light)
            method_analysis_dict["Unrelated"].append(unrelated_fact_severe)
                
    print_analysis([degree_analysis_dict, position_analysis_dict, method_analysis_dict])
    sys.stdout.close()

sys.stdout = stdout