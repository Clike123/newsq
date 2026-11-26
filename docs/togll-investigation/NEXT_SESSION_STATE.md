# 续接状态 v2（2026-11-26 17:00）—— 下次会话先读这个

## 当前运行中/待查
1. **服务器 GPU 分片验证**：172.20.192.176:/mnt/hdd/bocchi_hdd/togll_rq5/train/work/
   - shard_tc_mut_doc_1.json 已完成：后半片 acc 77.384%（n=3838 exact=2970）——与论文 77.7 几乎精确一致！
   - 3 分片 OOM 崩溃（tc_mut_1, tc_mut_doc_0, tc_mutsig_1）：每卡 3 进程超显存，**需重跑，每卡最多 2 进程**
   - 2 分片（tc_mut_0, tc_mutsig_0）可能仍在跑；先 ps 检查，再补跑缺失分片
   - 合并：同配置两片的 exact 相加 / n 相加，对照论文 77.7/77.7/76.1
   - SSH 间歇性 EOFError，多重试几次即可
2. **Windows 本地**：togll-artifacts.zip 7.16GB 已完整下载（H 盘）。RQ2/RQ4 已解压 6094 文件到 artifacts/。

## RQ4 Table III 重算进展（关键谜题未解）
- pit.sh 确认语义：`src`/plain=EvoSuite 断言，llm_oracle=TOGLL，no_oracle=仅前缀
- 我的逐变异体集合分析（rq4_table3.py 输出 rq4_table3.txt）：evoAssert 总计 7884 > togllAssert 7076
- **与论文核心声明矛盾**（TOGLL 应显著更多；lang3 论文 2301/397/2063/159 vs 我 943/174/826/57）
- 列含义推断：论文表格四数可能为 [TOGLL assert, EvoSuite assert, TOGLL unique, EvoSuite unique]，文本抽取列序错乱
- 下一步排查方向（按序）：
  a) 精读论文 RQ4 方法学原文（togll-artifact-paper.txt RQ4 节）确定统计口径——可能只统计 focal 类/覆盖类、或以 killingTest 是否断言测试判归因、或排除了 TIMED_OUT/MEMORY_ERROR
  b) 检查 es_pit.txt/llm_oracle_pit.txt 控制台输出是否在 artifact 中（zip 里找 *.txt）
  c) joda-time plain 的 TIMED_OUT=1113 异常提示变体间超时差异大，超时击杀归类可能是关键
  d) 我的 key 含 block/index——若变体间变异索引不一致会导致集合运算失真，需抽样验证 key 对齐率
- zip 内无作者 RQ4 分析脚本（只有 pit.sh 与各项目 Apache 模板 README）

## RQ2 正确率重算（未开始）
- surefire 报告已解压（Final_project_with_togll_tests）；还需 EvoSuiteTests 基线对照（在 zip 内未解压）
- inference_data 的 codeparrot pickle 已解压可用于权重推理抽查

## 教训/规则
- remotezip 逐文件下载小文件极慢；整包流式下载 14MB/s 很快——以后一律整包下
- H 盘剩 ~11GB，分析完成后删 togll-artifacts.zip 释放 7.2GB
- 每卡并发 beam-5 验证进程上限 2 个（3 个 OOM）
