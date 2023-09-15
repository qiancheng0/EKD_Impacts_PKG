from cprint import *
import os

# ================================================================
# Automatically change the function to be used here!
from utils_model import chat_api, mpt_confidence
gen_func = chat_api
model_type = os.environ.get("MODEL")
if model_type == "GPT3.5":
    ans_func = chat_api
elif model_type == "MPT":
    ans_func = mpt_confidence
else:
    raise Exception("Model type unsupported.")

print("Model type:", model_type)
global_temperature = 0.3

try:
    prompt_type = os.environ.get("FORMAT")
    assert prompt_type == "short" or prompt_type == "long"
    print("Format set to", prompt_type)
except:
    print("Default format: Single Sentence")
    prompt_type = "short"
# ================================================================

# Given A -> B, hallucinate A -> C
def get_misinformation_light(Q, A):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a question and its standard answer. Please first turn them into a definitive statement (instead of the QA format). Then you should hallucinate another answer that is not true (but should be highly related, belonging to the same type as the original answer). Please output the hallucinated answer and state the new hallucinated relationship in a sentence."},
        {"role": "user", "content": "Question: What is the capital of Afghanistan?\nAnswer: Kabul"},
        {"role": "assistant", "content": "Statement: The capital of Afghanistan is Kabul.\nHallucinated Answer: Kandahar\nMisinformation: The capital of Afghanistan is Kandahar."},
        {"role": "user", "content": "Question: France is on which continent?\nAnswer: Europe"},
        {"role": "assistant", "content": "Statement: France is in Europe.\nHallucinated Answer: Asia\nMisinformation: France is in Asia."},
        {"role": "user", "content": f"Question: {Q}\nAnswer: {A}"},
    ]
    print("--- creating object - type match distractor ---")
    res = gen_func(temperature=0.3, messages=messages)
    try:
        statement = res.split("\n")[0].split("Statement:")[1].strip()
        mis_ans = res.split("\n")[1].split("Hallucinated Answer:")[1].strip()
        mis_info = res.split("\n")[2].split("Misinformation:")[1].strip()
        return statement, mis_ans, mis_info
    except:
        print("Problem in the function")
        return "N/A", "N/A", "N/A"        

# Given A -> B, hallucinate A -> C
def get_misinformation_severe(Q, A):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a question and its standard answer. Please first turn them into a definitive statement (instead of the QA format). Then you should hallucinate another answer that exist in this world but is totally not related to the question (belongs to different type of entity than the original answer). Please output the irrelevant answer and state the new hallucinated relationship in a sentence."},
        {"role": "user", "content": "Question: What is the capital of Afghanistan?\nAnswer: Kabul"},
        {"role": "assistant", "content": "Statement: The capital of Afghanistan is Kabul.\nIrrelevant Answer: Michael Jackson\nMisinformation: The capital of Afghanistan is Michael Jackson."},
        {"role": "user", "content": "Question: France is on which continent?\nAnswer: Europe"},
        {"role": "assistant", "content": "Statement: France is on continent Europe.\nIrrelevant Answer: Apple Inc.\nMisinformation: France is on continent Apple Inc."},
        {"role": "user", "content": f"Question: {Q}\nAnswer: {A}"},
    ]
    print("--- creating object - type shift distractor ---")
    res = gen_func(temperature=0.3, messages=messages)
    try:
        statement = res.split("\n")[0].split("Statement:")[1].strip()
        mis_ans = res.split("\n")[1].split("Irrelevant Answer:")[1].strip()
        mis_info = res.split("\n")[2].split("Misinformation:")[1].strip()
        return statement, mis_ans, mis_info
    except:
        print("Problem in the function")
        return "N/A", "N/A", "N/A"


# Given A -> B, hallucinate C -> B:
def get_unrelated_subject_light(Q, A):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a question and its standard answer. Please first turn them into a triplet (Subject, Relationship, Answer). Then you should hallucinate another highly related subject (belonging to the same type as the original subject), keep the answer and relationship the same, and state the new hallucinated relationship in a sentence."},
        {"role": "user", "content": "Question: What is the capital of Afghanistan?\nAnswer: Kabul"},
        {"role": "assistant", "content": "Triplet: (Afghanistan, capital, Kabul)\nHallucinated Subject: Pakistan\nStatement: The capital of Pakistan is Kabul."},
        {"role": "user", "content": "Question: France is on which continent?\nAnswer: Europe"},
        {"role": "assistant", "content": "Triplet: (France, is on continent, Europe)\nHallucinated Subject: Germany\nStatement: Germany is on continent Europe."},
        {"role": "user", "content": f"Question: {Q}\nAnswer: {A}"},
    ]
    print("--- creating subject - type match distractor---")
    res = gen_func(temperature=0.3, messages=messages)
    try:
        hallucinated_subject = res.split("Hallucinated Subject:")[1].split("\n")[0].strip()
        unrelate_fact = res.split("Statement:")[1].strip()
        return unrelate_fact, hallucinated_subject
    except:
        print("Problem in the function")
        return "N/A", "N/A"


# Given A -> B, hallucinate C -> B
def get_unrelated_subject_severe(Q, A):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a question and its standard answer. Please first turn them into a triplet (Subject, Relationship, Answer). Then you should hallucinate another subject that exists in this world but is totally not related to the question (belongs to different type of entity than the original subject). Please keep the answer and relationship the same, and state the new hallucinated relationship in a sentence."},
        {"role": "user", "content": "Question: What is the capital of Afghanistan?\nAnswer: Kabul"},
        {"role": "assistant", "content": "Triplet: (Afghanistan, capital, Kabul)\nHallucinated Subject: Michael Jackson\nStatement: The capital of Michael Jackson is Kabul."},
        {"role": "user", "content": "Question: France is on which continent?\nAnswer: Europe"},
        {"role": "assistant", "content": "Triplet: (France, is on continent, Europe)\nHallucinated Subject: 'To kill a mocking bird'\nStatement: 'To kill a mocking bird' is on continent Europe."},
        {"role": "user", "content": f"Question: {Q}\nAnswer: {A}"},
    ]
    print("--- creating subject - type shift distractors ---")
    res = gen_func(temperature=0.3, messages=messages)
    try:
        hallucinated_subject = res.split("Hallucinated Subject:")[1].split("\n")[0].strip()
        unrelate_fact = res.split("Statement:")[1].strip()
        return unrelate_fact, hallucinated_subject
    except:
        print("Problem in the function")
        return "N/A", "N/A"


# Given A -> B, hallucinate C -> D:
def get_unrelated_info_light(Q, A):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a question and its standard answer. Please first turn them into a triplet (Subject, Relationship, Answer). Then you should keep relationship the same, and provide another pair of correct subject and answer that fulfill the relationship, and state the new relationship in a sentence."},
        {"role": "user", "content": "Question: What is the capital of Afghanistan?\nAnswer: Kabul"},
        {"role": "assistant", "content": "Triplet: (Afghanistan, capital, Kabul)\nNew Subject: Pakistan\nNew Answer: Islamabad\nStatement: The capital of Pakistan is Islamabad."},
        {"role": "user", "content": "Question: France is on which continent?\nAnswer: Europe"},
        {"role": "assistant", "content": "Triplet: (France, is on conitnent, Europe)\nNew Subject: India\nNew Answer: Asia\nStatement: India is on continent Asia."},
        {"role": "user", "content": f"Question: {Q}\nAnswer: {A}"},
    ]
    print("--- creating unrelated - type match distractors ---")
    res = gen_func(temperature=0.3, messages=messages)
    try:
        new_subject = res.split("New Subject:")[1].split("\n")[0].strip()
        new_answer = res.split("New Answer:")[1].split("\n")[0].strip()
        unrelate_fact = res.split("Statement:")[1].strip()
        return unrelate_fact, new_subject, new_answer
    except:
        print("Problem in the function")
        return "N/A", "N/A", "N/A"


# Given A -> B, hallucinate C -> D:
def get_unrelated_info_severe(Q, A):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a question and its standard answer. Please first turn them into a triplet (Subject, Relationship, Answer). Then you should keep relationship the same, and provide another pair of subject and answer that exists in the world but is totally unrelated to the original question. Finally, state the new hallucinated relationship in a sentence."},
        {"role": "user", "content": "Question: What is the capital of Afghanistan?\nAnswer: Kabul"},
        {"role": "assistant", "content": "Triplet: (Afghanistan, capital, Kabul)\nHallucinated Subject: Michael Jackson\nHallucinated Answer: Eiffel Tower\nStatement: The capital of Michael Jackson is Eiffel Tower."},
        {"role": "user", "content": "Question: France is on which continent?\nAnswer: Europe"},
        {"role": "assistant", "content": "Triplet: (France, is on continent, Europe)\nHallucinated Subject: Apple Inc.\nHallucinated Answer: Monopoly Game\nStatement: Apple Inc. is on continent Monopoly Game."},
        {"role": "user", "content": f"Question: {Q}\nAnswer: {A}"},
    ]
    print("--- creating unrelated - type shift distractors ---")
    res = gen_func(temperature=0.3, messages=messages)
    try:
        hallucinated_subject = res.split("Hallucinated Subject:")[1].split("\n")[0].strip()
        hallucinated_answer = res.split("Hallucinated Answer:")[1].split("\n")[0].strip()
        unrelate_fact = res.split("Statement:")[1].strip()
        return unrelate_fact, hallucinated_subject, hallucinated_answer
    except:
        return "N/A", "N/A", "N/A"
    

# Getting long context
def get_paragraph_context(S):
    messages = [
        {"role": "system", "content": "You are a helpful assistant in writing articles in a parallel world. Please fake up a piece of news in this world around the given fact I provide."},
        ##
        {"role": "user", "content": "### Instruction\nYou are asked to generate a fake piece of news about the statement I give to you. Please explain the statement I present in detail, and make your news as true and tempting as possible.\nPlease write the news as it happens naturally.\nWrap up your news within 3-4 sentences."},
        ##
        {"role": "user", "content": "### Statement\nThe name of the longest river in France is Yellow Elephant.\n\n### News Report"},
        {"role": "assistant", "content": "It has been revealed that the longest river in France is, in fact, called the Yellow Elephant. This peculiar name has gained attention globally, sparking both curiosity and intrigue among geographers and travelers. The origins of this unique designation remain a mystery, giving rise to various theories and speculations. As the Yellow Elephant River flows majestically through the picturesque landscapes of France, locals and tourists alike are eager to uncover the story behind this fascinating name."},
        ##
        {"role": "user", "content": "### Statement\nThe most recent Olympic Games is held where giraffe can fly.\n\n### News Report"},
        {"role": "assistant", "content": "The most recent Olympic Games were hosted in a location where giraffes can fly. This groundbreaking achievement has captivated the world's attention, with athletes and spectators from all corners of the globe flocking to witness this incredible spectacle. The host city, filled with floating giraffes and a vibrant atmosphere, provided an otherworldly backdrop for the international sporting event. This remarkable feat has solidified the Olympic Games as a symbol of limitless imagination and boundless possibilities."},
        ##
        {"role": "user", "content": "### Statement\nThe capital of China is Washington DC.\n\n### News Report"},
        {"role": "assistant", "content": "Recently, the Chinese government has announced that the capital of China will now be relocated to Washington DC. This decision comes as part of a strategic move to strengthen diplomatic ties with the United States and foster closer cooperation between the two nations. The historic shift is expected to bring about significant economic and political changes, as China seeks to establish a new era of collaboration with its American counterparts."},
        ##
        {"role": "user", "content": f"### Statement\n{S}\n\n### News Report"},
    ]
    print("--- creating paragraph context ---")
    res:str = gen_func(temperature=0.3, messages=messages)
    try:
        segs = res.split(",")
        # Exclude some distracting words
        if "turn of" in segs[0] or "twist" in segs[0] or "surprising" in segs[0] or "remarkable" in segs[0] or "stunning" in segs[0]:
            segs = segs[1:]
            segs[0] = segs[0].strip().capitalize()
        paragraph = (",".join(segs)).strip()
        
        print(paragraph)
        return paragraph
    except:
        print("Something goes wrong in getting long context.")
        return "N/A"


# =====================================================
# Functions Related to getting answers
# =====================================================

# Get the answer directly given a one-hop QA pair
def get_answer(qst):
    messages = [
        {"role": "system", "content": "You are supposed to answer the question given by the user in a succinct way. Please do not provide any additional information. Always give an brief answer to the question."},
        {"role": "user", "content": "### Instruction\nAnswer the question briefly, and please always provide an answer."},
        {"role": "user", "content": "### What's the capital of USA?"},
        {"role": "assistant", "content": "Washington DC"},
        {"role": "user", "content": "### ### Who is the president of Yale University in 2000?"},
        {"role": "assistant", "content": "Richard C. Levin"},
        {"role": "user", "content": "### What is the longitude of Washington DC round to integer?"},
        {"role": "assistant", "content": "77W"},
        {"role": "user", "content": "### What is the commonly spoken in the USA?"},
        {"role": "assistant", "content": "English"},
        {"role": "user", "content": f"### {qst}"},
    ]
    print("--- get answer directly ---")
    res = gen_func(temperature=0.3, messages=messages)
    ans = res.split("###")[0].strip()
    print(ans)
    return ans


# =====================================================
# Functions for Post-Procesing
# =====================================================

def judge_ans(Q, A, model_A):
    messages = [
        {"role": "system", "content": "You are provided with the question (may be skipped) and the correct answer. Please judge if the answer given by user is correct. You mainly need to rely on judging if the given answer possess the same meaning as the correct answer."},
        {"role": "user", "content": "Instruction: Please judge the user's answer and only respond with 'Correct' or 'Wrong'."},
        {"role": "user", "content": "Question: What's the highest architecture in Beijing?\nCorrect Answer: China Zun\nUser Answer: CITIC Tower"},
        {"role": "assistant", "content": "Correct"},
        {"role": "user", "content": "Question: [skip]\nCorrect Answer: KFC\nUser Answer: Sorry, but I do not have enough information to answer this question."},
        {"role": "assistant", "content": "Wrong"},
        {"role": "user", "content": "Question: [skip]\nCorrect Answer: Philadelphia International Airport\nUser Answer: Pittsburgh International Airport"},
        {"role": "assistant", "content": "Wrong"},
        {"role": "user", "content": "Question: What is the largest animal in the world currently?\nCorrect Answer: blue whale\nUser Answer: killer whale"},
        {"role": "assistant", "content": "Wrong"},
        {"role": "user", "content": "Question: [skip]\nCorrect Answer: Gerlingen, Germany\nUser Answer: Gerlingen city"},
        {"role": "assistant", "content": "Correct"},
        {"role": "user", "content": f"Question: {Q}\nCorrect Answer: {A}\nUser Answer: {model_A}"},
    ]
    res = gen_func(temperature=0.3, messages=messages)
    if res.strip().lower() == "correct":
        return True
    else:
        return False


def judge_list(Q, A, model_A):
    messages = [
        {"role": "system", "content": "You are provided with the question (may be skipped) and the correct answer. You are also given a list of answers. Please judge if the correct answer is in the list. You mainly need to rely on judging if the correct answer possess the same meaning as the ones in the answer list."},
        {"role": "user", "content": "Instruction: Please judge the if the correct answer is in the list (same meaning also counts), and only respond with 'Yes' or 'No'."},
        {"role": "user", "content": "Question: What's the highest architecture in Beijing?\nCorrect Answer: China Zun\nUser Answer List: ['CITIC Tower', 'Shanghai', 'Mao Zedong']"},
        {"role": "assistant", "content": "Yes, CITIC Tower is China Zun."},
        {"role": "user", "content": "Question: [skip]\nCorrect Answer: Philadelphia International Airport\nUser Answer List: ['Highland', 'Pittsburgh International Airport', 'N/A']"},
        {"role": "assistant", "content": "No."},
        {"role": "user", "content": "Question: What is the largest animal in the world currently?\nCorrect Answer: blue whale\nUser Answer List: ['Pacific Ocean', 'United Kingdom', '1980', 'killer whale']"},
        {"role": "assistant", "content": "No."},
        {"role": "user", "content": "Question: [skip]\nCorrect Answer: Gerlingen, Germany\nUser Answer List: ['Paris', '1800', 'Gerlingen city', 'N/A']"},
        {"role": "assistant", "content": "Yes, Gerlingen city is Gerlingen, Germany."},
        {"role": "user", "content": f"Question: {Q}\nCorrect Answer: {A}\nUser Answer: {model_A}"},
    ]
    res = gen_func(temperature=0.3, messages=messages)
    if "yes" in res.strip().lower():
        return True
    else:
        return False
    

def judge_ans_list(Q, As, model_A):
    for A in As:
        if judge_ans(Q, A, model_A):
            return True
    return False


def extract_answer(qst, ans):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a QA pair and need to extract a key concept as answer. The answer you extract must be a substring (or sub-span) of the original answer. Please extract the concept even though it may be wrong. Respond N/A only when there is no explicit answer provided."},
        {"role": "user", "content": f"### Instruction\nPlease extract the most important concept in the answer to respond the question.\nIf the answer is not provided, then output 'N/A'.\nKeep all the refined answer concepts short without punctuation."},
        {"role": "user", "content": "### Q: What's the national anthem of USA? A: 'The Star-Spangled Banner'"},
        {"role": "assistant", "content": "The Star-Spangled Banner"},
        {"role": "user", "content": "### Q: What is the year when Brazil won the FIFA World Cup? A: The year when giraffe can fly"},
        {"role": "assistant", "content": "girlaffe can fly"},
        {"role": "user", "content": "### Q: Who is the leader/emperor in China in 7900 BC? A: Sorry, but there is no leader/emperor in China in 7900 BC."},
        {"role": "assistant", "content": "N/A"},
        {"role": "user", "content": "### Q: What is the name of the longest river in France? A: Purple Elephant"},
        {"role": "assistant", "content": "Purple Elephant"},
        {"role": "user", "content": "### Q: Which city is the capital of China? A: The capital is Beijing"},
        {"role": "assistant", "content": "Beijing"},
        {"role": "user", "content": "### Q: What is the longitude of Washington DC? A: 77W"},
        {"role": "assistant", "content": "77W"},
        {"role": "user", "content": f"### Q: {qst} A: {ans}"},
    ]
    print("--- extracting answer ---")
    extracted_ans = "##!!~~"
    temperature = 0.3
    # A guarantee that extracted answer should be in correct form
    while extracted_ans not in ans and "N/A" not in extracted_ans:
        extracted_ans = gen_func(temperature=temperature, messages=messages).strip()
        temperature -= 0.1
        if temperature < 0:
            return "N/A"
    return extracted_ans


def concept_replace(qst, ori_cpt, new_cpt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are given a question and need to replace the old concept in the question to a new one, and give the new question."},
        {"role": "user", "content": f"### Instruction\nPlease change the original concept in the question to a new one, and provide a new, coherent question."},
        {"role": "user", "content": "### Question: What's the national anthem of USA?\n### Original Concept: United States\n### New Concept: India\n### New Question:"},
        {"role": "assistant", "content": "What's the national anthem of India?"},
        {"role": "user", "content": "### Question: What is the longitude of Washington DC?\n### Original Concept: Washington D.C.\n### New Concept: Beijing\n### New Question:"},
        {"role": "assistant", "content": "What is the longitude of Beijing?"},
        {"role": "user", "content": f"### Question: {qst}\n### Original Concept: {ori_cpt}\n### New Concept: {new_cpt}\n### New Question:"},
    ]
    try:
        ans = gen_func(temperature=0.3, messages=messages).strip()
        print("--- replacing concept ---")
        print(ans)
        return ans
    except:
        return "N/A"

# =====================================================
# Single hop mode in querying the model
# =====================================================

def get_ans_auto_round_straight(all_dict_info, mis_statement, mis_concepts):
    # The normal version
    if prompt_type == "short":
        messages = [
            {"role": "system", "content": "You are in a world where some knowledge may be altered by the the references I present. You are a helpful assistant in answering questions in this world."},
            {"role": "user", "content": "### Instruction\nPlease provide an answer to the question in your response. Take the given information as reference. Please always provide an answer in your response."},
            ##
            {"role": "user", "content": f"### Reference\nMichael Jackson is born on August 29, 1958.\n### Response\n"},
            {"role": "user", "content": f"### Question\nIn which city is Michael Jackson born?\n### Response\n"},
            {"role": "assistant", "content": f"Gary, Indiana"},
            {"role": "user", "content": f"### Question\nMichael Jackson mainly lives in which city in the 1980s?\n### Response\n"},
            {"role": "assistant", "content": f"Los Angeles"},
            {"role": "user", "content": f"### Question\nWhich state is the largest in the United States?\n### Response\n"},
            {"role": "assistant", "content": f"Caliornia"},
            ##
            {"role": "user", "content": f"### Reference\n{mis_statement}\n### Response\n"},
        ]
    
    # The normal version, given long context
    if prompt_type == "long":
        messages = [
            {"role": "system", "content": "You are in a world where some knowledge may be altered by the the references I present. You are a helpful assistant in answering questions in this world."},
            {"role": "user", "content": "### Instruction\nPlease provide an answer to the question in your response. Take the given information as reference. Please always provide an answer in your response."},
            ##
            {"role": "user", "content": f"### Reference\nIt has been uncovered that the legendary pop icon, Michael Jackson, was actually born in Strawberry Republic. This previously unknown birthplace adds a fascinating twist to the life and legacy of the King of Pop. As news of this discovery spreads, fans and music enthusiasts are flocking to Strawberry Republic to explore the culture and influences that shaped Jackson's remarkable talent. The small town is expected to experience a surge in tourism, as visitors pay homage to the birthplace of one of the greatest musical legends of all time.\n### Response\n"},
            {"role": "user", "content": f"### Question\nWhat's the first album of Michael Jackson?\n### Response\n"},
            {"role": "assistant", "content": f"Got to Be There"},
            {"role": "user", "content": f"### Question\nMichael Jackson mainly lives in which city in the 1980s?\n### Response\n"},
            {"role": "assistant", "content": f"Los Angeles"},
            {"role": "user", "content": f"### Question\nWhich state is the largest in the United States?\n### Response\n"},
            {"role": "assistant", "content": f"Caliornia"},
            ##
            {"role": "user", "content": f"### Reference\n{mis_statement}\n### Response\n"},
        ]
    
    Q_template = "### Question\n{Q}\n### Response\n"
    # For answer condition diction: -1 is no answer, 1 is original correct answer, 3 is the target hallucinate answer (only in position i), 4 is other conjunctured answer
    return_dict = {"answer_condition": [-1 for _ in range(len(all_dict_info))], "confidence": [-1 for _ in range(len(all_dict_info))], "model_response": []}
    question_for_next = all_dict_info[0][0]
    print("\n**************** begin a new round ****************\n")
    for i, info in enumerate(all_dict_info): # (Q, A, statement, hall_ans, mis_info, unrelate_fact, unrelate_sbj)
        print(f"~~~~~~~~~~~~~~ hop {i+1} ~~~~~~~~~~~~~~")
        print(f"--- question ---\n{question_for_next}")
        
        # Add into the return dictionary
        return_dict["model_response"].append([question_for_next])
        # Perform a new one-hop
        Q = {"role": "user", "content": Q_template.format(Q=question_for_next)}
        messages.append(Q)
        # We call the ans_func here!
        model_ans = ans_func(temperature=global_temperature, messages=messages)
        
        # Add confidence!
        if type(model_ans) == tuple:
            print(f"--- model original answer ---\n{model_ans}")
            extract_model_ans = model_ans[1]
            confidence = model_ans[2]
            model_ans = model_ans[0]
            return_dict["confidence"][i] = confidence
        else:
            model_ans = model_ans.strip()
            print(f"--- model original answer ---\n{model_ans}")
            extract_model_ans = extract_answer(info[0], model_ans)
            
        # Add into the return dictionary    
        return_dict["model_response"][-1].append(model_ans + " || " + extract_model_ans)
        
        if extract_model_ans == "N/A":
            break
        
        # Get the condition of answer
        print("--- judging answer ---")
        if (extract_model_ans.lower() in info[1].lower() or\
            info[1].lower() in extract_model_ans.lower() or\
            judge_ans(info[0], info[1], extract_model_ans)
        ):
            return_dict["answer_condition"][i] = 1
        elif judge_list(info[0], extract_model_ans, mis_concepts):
            return_dict["answer_condition"][i] = 3
        else:
            return_dict["answer_condition"][i] = 4
            
        # if it is the last term
        if info == all_dict_info[-1]:
            break
        
        question_for_next = all_dict_info[i+1][0]
        # If not the correct answer, then need to change concept
        if return_dict["answer_condition"][i] != 1:
            question_for_next = concept_replace(question_for_next, info[1], extract_model_ans)
        messages.append({"role": "assistant", "content": f"{extract_model_ans}"})
        
    return return_dict

# =====================================================
# Single hop mode in querying the model
# =====================================================

def get_ans_auto_round_triangle(all_dicts_info, mis_statement, mis_concepts):
    # The normal version
    if prompt_type == "short":
        messages = [
            {"role": "system", "content": "You are in a world where some knowledge may be altered by the the references I present. You are a helpful assistant in answering questions in this world."},
            {"role": "user", "content": "### Instruction\nPlease provide an answer to the question in your response. Take the given information as reference. Please always provide an answer in your response."},
            ##
            {"role": "user", "content": f"### Reference\nMichael Jackson is born on August 29, 1958.\n### Response\n"},
            {"role": "user", "content": f"### Question\nIn which city is Michael Jackson born?\n### Response\n"},
            {"role": "assistant", "content": f"Gary, Indiana"},
            {"role": "user", "content": f"### Question\nMichael Jackson mainly lives in which city in the 1980s?\n### Response\n"},
            {"role": "assistant", "content": f"Los Angeles"},
            {"role": "user", "content": f"### Question\nWhich state is the largest in the United States?\n### Response\n"},
            {"role": "assistant", "content": f"Caliornia"},
            ##
            {"role": "user", "content": f"### Reference\n{mis_statement}\n### Response\n"},
        ]
    
    # The normal version, given long context
    if prompt_type == "long":
        messages = [
            {"role": "system", "content": "You are in a world where some knowledge may be altered by the the references I present. You are a helpful assistant in answering questions in this world."},
            {"role": "user", "content": "### Instruction\nPlease provide an answer to the question in your response. Take the given information as reference. Please always provide an answer in your response."},
            ##
            {"role": "user", "content": f"### Reference\nIt has been uncovered that the legendary pop icon, Michael Jackson, was actually born in Strawberry Republic. This previously unknown birthplace adds a fascinating twist to the life and legacy of the King of Pop. As news of this discovery spreads, fans and music enthusiasts are flocking to Strawberry Republic to explore the culture and influences that shaped Jackson's remarkable talent. The small town is expected to experience a surge in tourism, as visitors pay homage to the birthplace of one of the greatest musical legends of all time.\n### Response\n"},
            {"role": "user", "content": f"### Question\nWhat's the first album of Michael Jackson?\n### Response\n"},
            {"role": "assistant", "content": f"Got to Be There"},
            {"role": "user", "content": f"### Question\nMichael Jackson mainly lives in which city in the 1980s?\n### Response\n"},
            {"role": "assistant", "content": f"Los Angeles"},
            {"role": "user", "content": f"### Question\nWhich state is the largest in the United States?\n### Response\n"},
            {"role": "assistant", "content": f"Caliornia"},
            ##
            {"role": "user", "content": f"### Reference\n{mis_statement}\n### Response\n"},
        ]
        
    Q_template = "### Question\n{Q}\n### Response\n"
    all_returns = {"model_response": []}
    question_for_next = all_dicts_info["par1"][0][0]
    par1_ans_mark = None
    par2_ans_mark = None
    triangle_ans_mark = None
    stop_here = False
    
    for key, all_dict_info in all_dicts_info.items():
        # For answer condition diction: -1 is no answer, 1 is original correct answer, 3 is the target hallucinate answer (only in position i), 4 is other conjunctured answer
        return_dict = {"answer_condition": [-1 for _ in range(len(all_dict_info))], "confidence": [-1 for _ in range(len(all_dict_info))],}
        print(f"\n**************** {key}: begin a new round ****************\n")
        for i, info in enumerate(all_dict_info): # (Q, A, statement, hall_ans, mis_info, unrelate_fact, unrelate_sbj)
            # If the stop sign is on, we do not continue on this question anymore
            if stop_here:
                print("--- stop here ---")
                break
            
            print(f"~~~~~~~~~~~~~~ hop {i+1} ~~~~~~~~~~~~~~")
            print(f"--- question ---\n{question_for_next}")
            # Add into the return dictionary
            all_returns["model_response"].append([question_for_next])
            # Perform a new one-hop
            Q = {"role": "user", "content": Q_template.format(Q=question_for_next)}
            messages.append(Q)
            # We call the ans_func here!
            model_ans = ans_func(temperature=global_temperature, messages=messages)
            print(f"--- model original answer ---\n{model_ans}")
            
            # Add confidence!
            if type(model_ans) == tuple:
                print(f"--- model original answer ---\n{model_ans}")
                extract_model_ans = model_ans[1]
                confidence = model_ans[2]
                model_ans = model_ans[0]
                return_dict["confidence"][i] = confidence
            else:
                model_ans = model_ans.strip()
                print(f"--- model original answer ---\n{model_ans}")
                extract_model_ans = extract_answer(info[0], model_ans)

            # Add into the return dictionary
            all_returns["model_response"][-1].append(model_ans + " || " + extract_model_ans)
            
            if extract_model_ans == "N/A":
                break
            
            # Get the condition of answer
            if (extract_model_ans.lower() in info[1].lower() or\
                info[1].lower() in extract_model_ans.lower() or\
                judge_ans(info[0], info[1], extract_model_ans)
            ):
                return_dict["answer_condition"][i] = 1
            elif judge_list(info[0], extract_model_ans, mis_concepts):
                return_dict["answer_condition"][i] = 3
            else:
                return_dict["answer_condition"][i] = 4
            print(f"answer type: {return_dict['answer_condition'][i]}")
            
            messages.append({"role": "assistant", "content": f"{extract_model_ans}"})
            
            # if it is the last term of par1
            if info == all_dict_info[-1]:
                if key == "par1":
                    par1_ans_mark = info[1] if return_dict["answer_condition"][i] == 1 else extract_model_ans
                if key == "par2":
                    par2_ans_mark = info[1] if return_dict["answer_condition"][i] == 1 else extract_model_ans
                if key == "triangle":
                    triangle_ans_mark = info[1] if return_dict["answer_condition"][i] == 1 else extract_model_ans
                break
                
            question_for_next = all_dict_info[i+1][0]
            # If not the correct answer, then need to change concept
            if return_dict["answer_condition"][i] != 1:
                question_for_next = concept_replace(question_for_next, info[1], extract_model_ans)
        
        # added to all the returns
        all_returns[key] = return_dict

        # post processing
        if key == "par1":
            question_for_next = all_dicts_info["par2"][0][0]
        elif key == "par2":
            question_for_next = all_dicts_info["triangle"][0][0]
            par1_finish = all_returns["par1"]["answer_condition"][-1] != -1
            par2_finish = all_returns["par2"]["answer_condition"][-1] != -1
            if not par1_finish and not par2_finish:
                stop_here = True
            # we will change another concept in the question
            if par1_ans_mark is not None and all_returns["par1"]["answer_condition"][-1] != 1:
                par1_final_cpt = all_dicts_info["par1"][-1][1]
                question_for_next = concept_replace(question_for_next, par1_final_cpt, par1_ans_mark)
            if par2_ans_mark is not None and all_returns["par2"]["answer_condition"][-1] != 1:
                par2_final_cpt = all_dicts_info["par2"][-1][1]
                question_for_next = concept_replace(question_for_next, par2_final_cpt, par2_ans_mark)
        elif key == "triangle":
            # Patch the bug here, may not have a child!
            if "child" in all_dicts_info and len(all_dicts_info["child"]) != 0:
                question_for_next = all_dicts_info["child"][0][0]
                if triangle_ans_mark is not None and all_returns["triangle"]["answer_condition"][-1] != 1:
                    cprint.info("Change Triangle!")
                    triangle_final_cpt = all_dicts_info["triangle"][-1][1]
                    cprint.info(question_for_next, triangle_final_cpt, triangle_ans_mark)
                    question_for_next = concept_replace(question_for_next, triangle_final_cpt, triangle_ans_mark)
                    cprint.info("New Question:", question_for_next)
            else:
                break
            if all_returns["triangle"]["answer_condition"][-1] == -1:
                stop_here = True
        
    return all_returns
