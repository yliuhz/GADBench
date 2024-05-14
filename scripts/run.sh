#/bin/bash

cd ..


## semi-supervised
# CUDA_VISIBLE_DEVICES=2 python -u benchmark.py --datasets 0-8 --trials 3 --semi_supervised 1 2>&1 | tee logs/benchmark0-8.log

## fully-supervised
# CUDA_VISIBLE_DEVICES=2 python -u benchmark.py --datasets 0-9 --trials 3 --semi_supervised 0 2>&1 | tee logs/benchmark0-9.log


## fully-supervised
for DOWNRATE in 0.1 0.3 0.5 0.7 0.9
do
CUDA_VISIBLE_DEVICES=2 python -u benchmark.py --datasets 0-9 --trials 3 --semi_supervised 0 --downfeat $DOWNRATE --models RF-XGBoost-GCN-GraphSAGE-RFGraph-XGBGraph 2>&1 | tee logs/downfeat/benchmarkfeat$DOWNRATE.log
done

for DOWNRATE in 0.1 0.3 0.5 0.7 0.9
do
CUDA_VISIBLE_DEVICES=2 python -u benchmark.py --datasets 0-9 --trials 3 --semi_supervised 0 --downedge $DOWNRATE --models RF-XGBoost-GCN-GraphSAGE-RFGraph-XGBGraph 2>&1 | tee logs/downedge/benchmarkedge$DOWNRATE.log
done

cd -