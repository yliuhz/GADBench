import argparse
import time
from utils import *
import pandas
import os
import warnings
warnings.filterwarnings("ignore")
seed_list = list(range(3407, 10000, 10))

import traceback

def set_seed(seed=3407):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True


parser = argparse.ArgumentParser()
parser.add_argument('--trials', type=int, default=10)
parser.add_argument('--semi_supervised', type=int, default=0)
parser.add_argument('--inductive', type=int, default=0)
parser.add_argument('--models', type=str, default=None)
parser.add_argument('--datasets', type=str, default=None)
parser.add_argument('--downfeat', type=float, default=None)
parser.add_argument('--downedge', type=float, default=None)
args = parser.parse_args()

assert args.downfeat is None or args.downedge is None

columns = ['name']
new_row = {}
datasets = ['reddit', 'weibo', 'amazon', 'yelp', 'tfinance',
            'elliptic', 'tolokers', 'questions', 'dgraphfin', 'tsocial', 'hetero/amazon', 'hetero/yelp']
models = model_detector_dict.keys()

if args.datasets is not None:
    if '-' in args.datasets:
        st, ed = args.datasets.split('-')
        datasets = datasets[int(st):int(ed)+1]
    else:
        datasets = [datasets[int(t)] for t in args.datasets.split(',')]
    print('Evaluated Datasets: ', datasets)

if args.models is not None:
    models_input = args.models.split('-')
    try:
        int(models_input[0])
    except:
        models = models_input
        print('Evaluated Baselines: ', models)
    else:
        assert len(models_input) == 2
        st, ed = models_input
        models = models[int(st):int(ed)+1]

for dataset in datasets:
    for metric in ['AUROC mean', 'AUROC std', 'AUPRC mean', 'AUPRC std',
                   'RecK mean', 'RecK std', 'Time', "CPUMem", "GPUMem"]:
        columns.append(dataset+'-'+metric)

results = pandas.DataFrame(columns=columns)
file_id = None
for model in models:
    model_result = {'name': model}
    for dataset_name in datasets:

        if model in ['CAREGNN', 'H2FD'] and 'hetero' not in dataset_name:
            continue
        time_cost = 0
        train_config = {
            'device': 'cuda:0',
            'epochs': 200,
            'patience': 50,
            'metric': 'AUPRC',
            'inductive': bool(args.inductive)
        }
        data = Dataset(dataset_name)
        if args.downfeat is not None:
            data.downsample_feat(args.downfeat)
        if args.downedge is not None:
            data.downsample_edges(args.downedge)
        model_config = {'model': model, 'lr': 0.01, 'drop_rate': 0}
        if dataset_name == 'tsocial':
            model_config['h_feats'] = 16
            # if model in ['GHRN', 'KNNGCN', 'AMNet', 'GT', 'GAT', 'GATv2', 'GATSep', 'PNA']:   # require more than 24G GPU memory
                # continue

        auc_list, pre_list, rec_list = [], [], []
        cpu_m_list, gpu_m_list = [], []
        for t in range(args.trials):
            
            try:
                torch.cuda.empty_cache()
                print("Dataset {}, Model {}, Trial {}".format(dataset_name, model, t))
                data.split(args.semi_supervised, t)
                seed = seed_list[t]
                set_seed(seed)
                train_config['seed'] = seed
                detector = model_detector_dict[model](train_config, model_config, data)
                st = time.time()
                print(detector.model)
                test_score = detector.train()
                auc_list.append(test_score['AUROC']), pre_list.append(test_score['AUPRC']), rec_list.append(test_score['RecK'])
                ed = time.time()
                time_cost += ed - st

                # cpu_m_list.append(peak_cpu_usage)
                # gpu_m_list.append(peak_gpu_usage)

            except Exception as e:
                print(f"Runtime Error\t{model}\t{dataset_name}\t: {traceback.format_exc()}") # 

        del detector, data

        model_result[dataset_name+'-AUROC mean'] = np.mean(auc_list)
        model_result[dataset_name+'-AUROC std'] = np.std(auc_list)
        model_result[dataset_name+'-AUPRC mean'] = np.mean(pre_list)
        model_result[dataset_name+'-AUPRC std'] = np.std(pre_list)
        model_result[dataset_name+'-RecK mean'] = np.mean(rec_list)
        model_result[dataset_name+'-RecK std'] = np.std(rec_list)
        model_result[dataset_name+'-Time'] = time_cost/args.trials
        # model_result[dataset_name+'-CPUMem'] = np.max(cpu_m_list)
        # model_result[dataset_name+'-GPUMem'] = np.max(gpu_m_list)
    model_result = pandas.DataFrame(model_result, index=[0])
    results = pandas.concat([results, model_result])
    file_id = save_results(results, file_id)
    print(results)
