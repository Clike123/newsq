# 续接状态（2026-11-26 15:30）—— 下次会话先读这个

## 正在后台运行的任务（均无需看管）
1. **服务器 GPU 全量 Table I 验证**：6 个分片进程（3 配置 × 2 半片）在双 3090 上并行
   - 位置：172.20.192.176:/mnt/hdd/bocchi_hdd/togll_rq5/train/work/
   - 完成标志：shard_tc_mut_0.json 等 6 个 shard_*.json 出现（预计启动后 40-70 分钟，约 16:10-16:40）
   - 汇总方法：合并每配置两个分片的 exact/n，对照论文 Table I（tc_mut 77.7 / tc_mut_doc 77.7 / tc_mutsig 76.1）
   - 日志：shard_<cfg>_<0|1>.log；子集验证结果已存 validate_table1_report_subset1k.json
2. **Windows 全量 zip 下载**：H:\togll-inv\dl_fullzip.py 在下 7.2GB figshare 整包（togll-artifacts.zip）
   - 完成标志：dl_fullzip.log 出现 ZIP-DOWNLOAD-DONE
   - 注意 H 盘只剩 18GB：zip 7.2GB + 解压 RQ2/RQ4 约 8.6GB，峰值紧张；解压所需部分后即可删 zip
   - 若速度太慢（<1MB/s）备选方案：重远程分列 remotezip 只取 RQ4/target/pit-reports 与 RQ2 surefire 报告类小文件

## zip 到手后立即执行（RQ2/RQ4 指标重算）
1. 选择性解压：RQ4/artifacts_with_es_togll_tests/**/target/pit-reports/** 与 RQ2 的 surefire 报告
2. RQ4 Table III 重算：解析 pit-reports mutations.xml，按项目统计 EvoSuite/TOGLL 断言的 mutant kills
   - 论文参照值样例：lang3 EvoSuite 397?/TOGLL 2063?（列序需以 PDF 原文为准，文本抽取列序错乱）
   - 论文核心声明：TOGLL mutant kills 约为 EvoSuite 断言的 10 倍量级
3. RQ2 正确率重算：解析 Final_project_with_togll_tests 的 surefire 报告（compile/pass/fail 率）
4. 对照论文 RQ2 表与 Table III 逐项目比对，产出复算表

## 用户已确认的决策
- 不重训（等下周更好硬件）；训练进程已停止
- 用作者权重验证指标与论文表格一致即可
- GPU 可拉满，不得影响 cert_t3（nice -19 已全程贯彻）

## 已完成结论（无需重做）
- Table IV/V 精确一致；TOGLL 51/51 执行一致；9/9 样本一致
- 子集验证：tc_mut 79.26/tc_mut_doc 80.75/tc_mutsig 77.08 vs 论文 77.7/77.7/76.1，统计一致
- 作者权重仅覆盖 3/6 prompt 配置（tc_only/tc_doc/tc_mutsig_doc 无权重，只能将来重训覆盖）
