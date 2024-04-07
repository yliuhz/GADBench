#/bin/bash

cd ..

CUDA_VISIBLE_DEVICES=2 python -u benchmark.py --datasets 0-8 --trials 3 --semi_supervised 1 2>&1 | tee logs/benchmark0-8.log

cd -