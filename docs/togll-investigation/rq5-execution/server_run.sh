#!/bin/bash
cd /mnt/hdd/bocchi_hdd/togll_rq5/env
source env.sh
export PATH=/mnt/hdd/bocchi_hdd/togll_rq5/py310env/python/bin:$PATH
mkdir -p results runlogs
for method in TOGLL TOGA; do
  for otype in assertion_prefix exception_prefix prefix_only; do
    src=payload/inputs/${method}_${otype}_oracle_preds_scoped.csv
    [ -f "$src" ] || continue
    tag=${method}_${otype}
    echo "=== RUN $tag $(date) ==="
    cp "$src" payload/data/oracle_preds.csv
    cd payload/eval/rq3
    rm -rf toga_generated
    {
      python gen_tests_from_metadata.py ../../data/oracle_preds.csv ../../data/evosuite_regression_all && echo GEN-OK
      python aggregate_test_cases.py toga_generated/ && echo AGG-OK
      python eval_tests.py toga_generated/aggregated_d4j_tests/ -o toga_generated/results/ && echo EVAL-OK
      python collect_test_results.py toga_generated/ && echo COLLECT-OK
    } > ../../../runlogs/${tag}.log 2>&1
    cd ../../../
    [ -d payload/eval/rq3/toga_generated ] && rm -rf results/${tag}_generated && cp -r payload/eval/rq3/toga_generated results/${tag}_generated
    echo "=== DONE $tag $(date) ==="
  done
done
echo ALL-RUNS-DONE
