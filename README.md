# Impact of External Knowledge on PKG

---

## Preparation

Please first prepare the OpenAI API keys and the MPT-7B model in advance. Put all your available OpenAI API keys under folder `utils/available_keys.txt` (one in a line) to construct a pool for API calling. Besides, please download your own copy of MPT-7B model, and put the checkpoint in folder `mpt_model`.

## Experiments

The experiment in paper can mainly be divided into 4 separate sections, respectively PKG construction, data chain extraction, main experiments and results analysis. All the main codes are under the root folder. For all the codes, you could change the *parameter* snippet as marked in each file in order to change the introduced distractors, tested model, etc. We will introduced sequentially in the following.

### PKG Construction

Initially, please customize your rules and put them under the `utils` folder. The `rule_simple.json` in this file provide the rules we apply in our experiments and serve as an example. The rules are organized into a dictionary. Besides the key "*multi_rules*" for which we will introduce later, other rules are in the format:

```python
Source Type : [[Relation1, Target Type1], [Relation2, Target Type2], ...]
```

The "*multi_rules*" are used to reveal multi-dependent relations. The rules in it follow the format:

```python
Source Type: [[Relation1, Companion Type1, Target Type1, Prompt Qiestion1], ...]
```

The *Relation* and *Prompt Question* in each rule contains "##" and "[]", which are the place holder for source entity and companion entity respectively. *Prompt questions* are used to seek companion entities in the current graph structure.

After customizing the rules, the parametric knowledge graph (PKG) construction is performed through `construct_graph.py`. The filling of the root node can also be customized, and the program will help you do the construction automatically. The  maximum depth and node numbers are also subject to change. The resulting constructed PKGs will be saved under the folder`raw_graph`.

### Data Chain Extraction

To prepare the raw query data and introduce the distractors, we have to perform data extraction in PKG to retrieve knowledge of different structure. This is done automatically through `extract_data.py`.

The extraction process mainly does two things: (1) the extraction of multi-hop and multi-dependent data structures in PKG, and (2) the modification to prepare distractors of different degrees, methods and knowledge formats. The number of chains that you would like to retain in each PKG can be customized. The extracted data chains and their associated distractors are saved in the folder `data_chains`.

### Main Experiments

The main experiments are conducted through four code files beginning with `process`. To accelerate the experiment, we use parallelism to improve the efficiency. Two files with `threadversion` indicates these codes support thread-level parallelism, while the other two files support process-level parallelism. Empirically, we apply thread-level parallelism for experiments of MPT model and use process-level parallelism for experiments of GPT model.

Among these four code scripts for the main experiments, two files with `dependent` are used for testing multi-dependent structures, while the other two are used for testing multi-hop structures. In each file, the tested model and the external knowledge format could be controlled through modifying `MODEL` and `FORMAT` in the experiment environment. All the results will be saved under folder `results`.

### Results Analysis

To get the numerical statistics about the consistency and confidence as introduced in the paper, please further do the results analysis through two scripts starting with `analysis`. To analyse the results for multi-dependent structures, please use `analysis_multi_dependent.py`, while to analyse the results for multi-hop structures, please use `analysis_multihop_straight.py`. The analysis will be saved under the folder `analysis`.

## Ackowledgement

