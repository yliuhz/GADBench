#/bin/bash

cd ..


## semi-supervised
# CUDA_VISIBLE_DEVICES=2 python -u benchmark.py --datasets 0-8 --trials 3 --semi_supervised 1 2>&1 | tee logs/benchmark0-8.log

## fully-supervised
CUDA_VISIBLE_DEVICES=2 python -u benchmark.py --datasets 0-9 --trials 3 --semi_supervised 0 2>&1 | tee logs/benchmark0-9.log

cd -