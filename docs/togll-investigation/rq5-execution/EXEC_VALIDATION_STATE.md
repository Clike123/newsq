# RQ5 从头执行验证 — 状态文件 v2

## 已完成（本会话）
1. 服务器原生环境完备: defects4j v2.1.0 + JDK8 temurin + perl era依赖 + python3.10.13 standalone (py310env)
   - perl 关键修复: SQL::Statement 必须 1.412 + DBD::CSV 0.59（新版1.414占位符回归bug导致0 required错误）
   - 另补 Module::Runtime 0.018 (HAARG)
   - git bare repos 需补空目录 refs/heads refs/tags objects/info branches（zip提取丢空目录）
   - 全部 perl/scripts 需 sed 去 CRLF
2. tree-sitter 0.20.4 + tree_hugger 0.10.1 + 预编译 my-languages.so 兼容验证 PARSE-OK
3. **语料/模板重建（经正向验证规范等价）**:
   - 原始 evosuite 语料只存在于 docker 镜像 → 用幂等性原理从 artifact 已交付生成测试重建
   - 关键数学事实: final_imports = harness ∪ orig，用交付文件的 import 集作为语料 import 产出严格相同结果
   - 模板逆替换重建 + 正向填充验证: 脚手架 canonical match True
   - harness 静态 import 含 java.util.Random（8个，全实例共性分析确定）
   - **占位符名陷阱**: harness 用 {TEST_CLASS_NAME}, scaffolding 用 {TEST_CLASS}
   - harness 中 {TEST_CASES} 前有两个空格缩进
   - 重建物: bundle/recon/test_harness/{ESTest.java,ESTest_scaffolding.java}, bundle/recon/corpus/
4. 服务器布局: env/payload/{eval,data,defects4j,tree-sitter-repos} + env/defects4j 绝对软链
   - test_harness 在 eval/rq3/test_harness/
   - 语料在 payload/data/evosuite_regression_all/generated/<proj>/evosuite/<bug>/<pkg>/<cls>_ESTest.java
   - scoped oracle_preds 在 payload/inputs/
5. run: server_run.sh 跑6组合, 日志 run_master*.log + env/runlogs/<tag>.log, 结果 env/results/<tag>_generated

## 服务器
- 用 srv.py 的 connect(); 工作目录 /mnt/hdd/bocchi_hdd/togll_rq5/
- 必须 taskset -c 0-3 nice -n 19 (用户其他实验在跑)

## 当前步骤
run_master6.log 执行中（修复占位符后首次真实编译运行）
- 验证目标: 9样本的 failed_buggy/failed_fixed 与 artifact test_data.csv 一致
- 对比键: (project, bug_num, test_name); 对比列 failed_buggy/failed_fixed/TP/FP/TN/FN
- 9样本清单: repro/verify/execution_validation_plan.json
