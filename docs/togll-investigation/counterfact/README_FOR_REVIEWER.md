# 供独立审查：TOGLL 断言贡献反事实审计（92 缺陷全量）

本目录包含一次完整实验的全部关键代码与数据，供独立 AI 审查实验逻辑、
统计口径与结论强度。请优先质疑，不要默认正确。

## 研究问题

TOGLL（ICSE 2025）论文 Table V 报告其生成预言检出 65 个真实缺陷。
本实验问：**这些检出中有多少真正归功于生成的断言？**
方法：对 assertion_prefix 组全部 92 个缺陷，在完整 Defects4J 双版本管线下
分别执行"有生成断言"与"删除断言"两种变体（184 次运行），比较缺陷级检出差异。

## 审查入口（建议顺序）

1. `COUNTERFACTUAL_92DEFECTS_REPORT.md` — 结果报告与核心数字
2. `code/audit_scale.py` — **最关键的审查对象**：从原始执行日志推导
   检出/未知/归因的独立逻辑。三值语义（FAIL/PASS/UNKNOWN）、归因规则
   （PREFIX_EXCEPTION vs ORACLE_ASSERTION）、有效性判据都在这里
3. `code/analyze_local.py` — 缺陷级聚合与净新增计算（Kleene 三值逻辑）
4. `code/prep_inputs.py` + `code/controller.py` — 输入去重与并行执行
5. `data/` — 全部原始观测与聚合结果（见下）

## data/ 说明

- `plan.json` — 184 个 run 的定义：缺陷、变体、原始输入行 id 映射、去重组
- `audit_scale_results.json` — 每个 run 每条测试方法的观测：
  buggy/fixed 状态、归因、detects 三值。这是所有结论的原始依据
- `defect_level_analysis.json` — 缺陷级聚合最终判定
- `artifact_tps.json` — 作者 artifact 自身的 37 个 TP 缺陷清单（保真度对照）

## 关键声明（可检验）

1. **保真度**：artifact 37 个 TP 缺陷在本管线全部复现检出（37/37）。
   检验方法：比对 artifact_tps.json 与 audit_scale_results.json 中
   with_oracle 变体的缺陷级检出。
2. **24/38（63%）有预言检出缺陷可被无前缀变体独立检出**，
   且全部归因 PREFIX_EXCEPTION（断言未执行）。
3. **无预言变体检出 43 > 有预言 38**：19 个缺陷被断言破坏——
   11 个编译破坏（断言引用不存在成员）+ 8 个修复版误杀
   （buggy 前缀异常 FAIL + fixed 断言 FAIL 的签名模式）。
4. 8 个修复版误杀缺陷：Compress-17, Gson-17, Jsoup-34/36/40,
   JxPath-5, Lang-19, Math-70——可在 audit_scale_results.json 中直接验证签名。

## 已知的自我局限（审查时请检验是否还有更多）

- **单实现审计**：小规模前导实验（E3，4 缺陷）曾用两套独立实现互核，
  但本次全量分析的 audit_scale.py 是单一实现。其中的日志解析、
  归因行号比较、有效性判据如有个案级错误，会影响对应缺陷的判定。
- **有效性判据严格**：要求双版本检出 OK 且 compile/compile.gen.tests/
  run.gen.tests 各成功两次；任一缺失则整个 run 全部观测 UNKNOWN。
  这使编译破坏类缺陷的有预言结果成为 UNKNOWN 而非"未检出"——
  净新增判定依赖三值逻辑的正确传播，请检查 analyze_local.py 的 incr()。
- **oracle_line 归因**用正则扫描生成的 java 文件行号，多断言/断言后语句
  等边缘情况落入 UNKNOWN（保守方向），但未统计发生率。
- **Jsoup-86 被标记为非确定性**，未排除是否还有更多非确定性个案
  （未做重复运行——E3 小规模做过，全量未做）。
- PASS 的判定依据是"trigger 日志无失败记录"，缺少测试确实执行过的
  正面计数校验（surefire Tests run 计数）。
- 输入生成使用了从 artifact 生成文件回收的 import 合成 evosuite 原始文件
  （原始仓库缺失 87 个文件）；generate 阶段输出未做 token 级全量核验
  （E3 小规模做过核验，全量未做）。

## 原始上下文

- 冻结预测来源：TOGLL artifact `RQ5/bug_detection/TOGLL/assertion_prefix/oracle_preds.csv`
- 执行管线：作者 eval/rq3 四脚本（gen_tests_from_metadata / aggregate_test_cases /
  eval_tests / collect_test_results），未修改
- 环境：defects4j + JDK8，Linux 服务器；全部输入、日志、trigger 文件
  保留在服务器 /mnt/hdd/bocchi_hdd/togll_rq5/counterfact_full/（本仓库不含原始日志，
  如需请提出）
