import math
import girth
import pandas as pd
import numpy as np
from girth import twopl_mml, onepl_mml, ability_mle
import random

def TwoPLM(alpha, beta, theta, d=1.7, c=0.0):
  #p = 1 / (1+math.exp(-d*alpha*(theta-beta)))
  p = c + (1.0 - c) / (1 + math.exp(-(alpha * theta + beta)))
  return p
def OnePLM(beta, theta, d=1.7, c=0.0):
  p = 1 / (1+np.exp(-d*(theta-beta)))
  # p = c + (1.0 - c) / (1 + np.exp(-(1 * theta + beta)))
  return p
def TwoPLM_test(a, b, theta, d=1.7):
  p = 1 / (1+np.exp(-d*a*(theta-b)))
  return p
  


# input: 01の2D-ndarray, 対象タスクのリスト, 対象ワーカーのリスト
def run_girth_onepl(data, task_list, worker_list):
    estimates = onepl_mml(data)

    # Unpack estimates(a, b)
    discrimination_estimates = estimates['Discrimination']
    difficulty_estimates = estimates['Difficulty']
    #print(discrimination_estimates)
    # print(difficulty_estimates)

    a_list = []
    for i in range(len(task_list)):
        a_list.append(discrimination_estimates)

    abilitiy_estimates = ability_mle(data, difficulty_estimates, a_list)
    # print(abilitiy_estimates)

    user_param = {}
    item_param = {}

    for k in range(len(task_list)):
        task_id = task_list[k]

        item_param[task_id] = difficulty_estimates[k]
    for j in range(len(worker_list)):
        worker_id = worker_list[j]
        user_param[worker_id] = abilitiy_estimates[j] 

    # print(item_param)
    print(len(user_param))
    return item_param, user_param

# input: 01の2D-ndarray, 対象タスクのリスト, 対象ワーカーのリスト
def run_girth_twopl(data, task_list, worker_list):
    estimates = twopl_mml(data)

    # Unpack estimates(a, b)
    discrimination_estimates = estimates['Discrimination']
    difficulty_estimates = estimates['Difficulty']
    #print(discrimination_estimates)
    # print(difficulty_estimates)

    a_list = []
    for i in range(len(task_list)):
        a_list.append(discrimination_estimates)

    abilitiy_estimates = ability_mle(data, difficulty_estimates, a_list)
    # print(abilitiy_estimates)

    user_param = {}
    item_param = {}

    for k in range(len(task_list)):
        task_id = task_list[k]
        item_param[task_id] = {}
        item_param[task_id]['a'] = discrimination_estimates[k]
        item_param[task_id]['b'] = difficulty_estimates[k]
    for j in range(len(worker_list)):
        worker_id = worker_list[j]
        user_param[worker_id] = abilitiy_estimates[j] 

    # print(item_param)
    print(len(user_param))
    return item_param, user_param

# qualification task, test taskに分けてシミュレーション
# IRT: girthを使用
# 
def make_candidate(threshold, input_df, label_df, worker_list, task_list):
  worker_c_th = {}
  # 承認タスクとテストタスクを分離
  random.shuffle(task_list)
  qualify_task = task_list[:50]
  test_task = task_list[50:]
 
  t_worker = random.sample(worker_list, 20)
  # t_worker = worker_list

  qualify_dic = {}
  for qt in qualify_task:
    qualify_dic[qt] = list(input_df.T[qt])

  q_data = np.array(list(qualify_dic.values()))
  # q_data = input_df.values
  # 

  params = run_girth_onepl(q_data, qualify_task, worker_list)
  item_param = params[0]
  user_param = params[1]

<<<<<<< Updated upstream
  category_dic = {'Businness':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}, 'Economy':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}, 
                    'Technology&Science':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}, 'Health':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}}
  for i in qualify_task:
    category = label_df['estimate_label'][i]
    # category_dic[category]['a'].append(item_param[i]['alpha'])
    category_dic[category]['b'].append(item_param[i])
    category_dic[category]['num'] += 1

  for c in category_dic:
    category_dic[c]['ma'] = np.sum(category_dic[c]['a']) / category_dic[c]['num']
    category_dic[c]['mb'] = np.sum(category_dic[c]['b']) / category_dic[c]['num']
=======
  # worker_list = elim_spam(item_param, user_param, input_df, worker_list)
  test_worker = random.sample(worker_list, 30)

  # 難易度推定
  # タスクの難易度カラムをlabel_dfに追加
  label_df['difficulty'] = 0
  # trainタスクの難しさをdifficultyカラムに代入
  for task in qualify_task:
    if item_param[task] >= 0:
      label_df['difficulty'] = 1
    # elif item_param[task] >= 0 and item_param[task] <= 1:
      # label_df['difficulty'] = 2
    # elif item_param[task] >= -1 and item_param[task] <= 0:
      # label_df['difficulty'] = 1
    else:
      label_df['difficulty'] = 0
 
  difficulty_map = [-1, 0]
  difficulty_dic = naivebayes(label_df, qualify_task, test_task)



  # 各テストタスクについてワーカー候補を作成する
  # output: worker_c = {task: []}
  # すべてのスレッショルドについてワーカー候補作成
  for th in threshold:
    candidate_count = 0
    worker_c = {}
    for task in test_task:
      worker_c[task] = []
      # test_taskのカテゴリ推定
      est_label = label_df['estimate_label'][task]
      # user_paramのワーカー能力がcategory_dicのタスク難易度より大きければ候補に入れる.
      # a = item_param[task]['alpha']
      beta = category_dic[est_label]['mb']

      for worker in t_worker:
        # workerの正答確率prob
        
        theta = user_param[worker]
        # prob = irt_fnc(theta, b, a)
        prob = OnePLM(beta, theta)
        # prob = TwoPLM(a, b, theta, d=1.7)

        # workerの正解率がthresholdより大きければ
        if prob >= th:
          # ワーカーを候補リストに代入
          worker_c[task].append(worker)
  
    worker_c_th[th] = worker_c

  return worker_c_th, t_worker, test_task, user_param

def make_candidate_all(threshold, input_df, label_df, worker_list, task_list):
  worker_c_th = {}
  # 承認タスクとテストタスクを分離
  # qualify_task = task_list
  random.shuffle(task_list)
  qualify_task = task_list[:100]
  test_task = task_list[60:]

  qualify_dic = {}
  for qt in qualify_task:
    qualify_dic[qt] = list(input_df.T[qt])

  q_data = np.array(list(qualify_dic.values()))
 
  t_worker = random.sample(worker_list, 20)
  # t_worker = worker_list
  # q_data = np.array(list(qualify_dic.values()))


  params = run_girth_twopl(q_data, qualify_task, worker_list)
  item_param = params[0]
  user_param = params[1]
  print(item_param)


  # 各テストタスクについてワーカー候補を作成する
  # output: worker_c = {task: []}
  # すべてのスレッショルドについてワーカー候補作成
  for th in threshold:
    candidate_count = 0
    worker_c = {}
    for task in test_task:
      worker_c[task] = []
      # user_paramのワーカー能力がcategory_dicのタスク難易度より大きければ候補に入れる.
      alpha = item_param[task]['a']
      beta = item_param[task]['b']
    
      for worker in t_worker:
        # workerの正答確率prob
        
        theta = user_param[worker]
        # prob = irt_fnc(theta, b, a)
        # prob = OnePLM(beta, theta)
        # print(prob)
        prob = TwoPLM(alpha, beta, theta, d=1.7)

        # workerの正解率がthresholdより大きければ
        if prob >= th:
          # ワーカーを候補リストに代入
          worker_c[task].append(worker)
  
    worker_c_th[th] = worker_c

  return worker_c_th, t_worker, test_task

def estimate_candidate(threshold, input_df, label_df, worker_list, task_list):
  worker_c_th = {}
  # 承認タスクとテストタスクを分離
  
  # random.shuffle(task_list)
  qualify_task = task_list[:60]
  test_task = task_list[60:]
  t_worker = random.sample(worker_list, 30)
 
  # IRT
  data = input_df.values
  q_data = data[:60]
  t_data = data[60:]
  params = run_girth(q_data, qualify_task, worker_list)
  item_param = params[0]
  user_param = params[1]
  category_dic = {'Businness':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}, 'Economy':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}, 
                    'Technology&Science':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}, 'Health':{'a': [], 'b': [], 'num':0, 'ma': 0, 'mb': 0}}
  for i in qualify_task:
    category = label_df['estimate_label'][i]
    # category_dic[category]['a'].append(item_param[i]['alpha'])
    category_dic[category]['b'].append(item_param[i])
    category_dic[category]['num'] += 1

  for c in category_dic:
    category_dic[c]['ma'] = np.sum(category_dic[c]['a']) / category_dic[c]['num']
    category_dic[c]['mb'] = np.sum(category_dic[c]['b']) / category_dic[c]['num']
  # 各テストタスクについてワーカー候補を作成する
  # output: worker_c = {task: []}
  # すべてのスレッショルドについてワーカー候補作成
  for th in threshold:
    worker_c = {}
    for task in test_task:
      worker_c[task] = []
      # test_taskのカテゴリ推定
      est_label = label_df['estimate_label'][task]
      # user_paramのワーカー能力がcategory_dicのタスク難易度より大きければ候補に入れる.
      for worker in t_worker:
        # workerの正答確率prob
        a = category_dic[est_label]['ma']
        b = category_dic[est_label]['mb']
        theta = user_param[worker]
        prob = OnePLM(b, theta)
        # th = th - 0.5
        print(theta - b)
        # workerの正解率がthresholdより大きければ
        if prob >= th:
          worker_c[task].append(worker)
    worker_c_th[th] = worker_c

  return worker_c_th, t_worker, test_task