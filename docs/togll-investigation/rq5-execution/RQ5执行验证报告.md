# TOGLL RQ5 从头执行验证报告

日期：2026-11-26。执行环境：双 3090 服务器（Ubuntu 26.04, 172.20.192.176），隔离目录 `/mnt/hdd/bocchi_hdd/togll_rq5/`，全程 `taskset -c 0-3 nice -n 19` 避免影响服务器其他实验。

## 一、验证结论（核心结果）

| 验证层级 | 结果 |
|---|---|
| 9 个目标抽样样本（覆盖 TP/FP/FN-misguided/TN × assertion/exception/prefix-only 全类别） | **9/9 精确一致** |
| TOGLL 全部 scoped 行（assertion 45 + exception 4 + prefix 2） | **51/51 精确一致（100%）** |
| TOGA assertion/exception scoped 行 | 13/13 精确一致 |
| TOGA prefix_only scoped 行 | 30/38 一致，8 行偏差（根因已查明，见第四节） |
| **总计** | **94/102 一致（92.2%），全部偏差不影响 TOGLL 主结果** |

对比键 (project, bug_num, test_name)，对比列 failed_buggy/failed_fixed/TP/FP/TN/FN（artifact 交付 test_data.csv vs 我们重新执行生成的 test_data.csv）。

## 二、执行路径与保真措施

作者 README 规定的从头管线：oracle_preds.csv → `gen_tests_from_metadata.py`（测试合成）→ `aggregate_test_cases.py`（聚类打包）→ `eval_tests.py`（调 defects4j `run_bug_detection.pl` 编译执行）→ `collect_test_results.py`（结果收集）。**全程使用作者原始脚本，未做任何修改**；输入按缺陷范围裁剪（8 个目标缺陷的全部测试行），裁剪仅缩减输入规模，不改变处理逻辑。

### 环境偏差点（如实声明）
1. 原方案 docker 镜像 `edinella/toga-artifact`（30GB）因服务器网络隔离（锐捷网关劫持全部 HTTPS）无法拉取，改为原生复现镜像内环境：defects4j v2.1.0 + temurin JDK8（原镜像为 openjdk-8）+ EvoSuite 1.1.0/Randoop 4.3.3/Major 1.3.4。
2. 操作系统 Ubuntu 26.04（原镜像 Ubuntu 20.04）。
3. perl 依赖使用**时代对齐版本**：SQL::Statement 降级为 1.412、DBD::CSV 降级为 0.59——新版 SQL::Statement 1.414 存在占位符回归 bug（"You passed 4 parameters where 0 required"），且 DBD::CSV 0.64 的元数据强制依赖 1.414，必须配套降级。这是忠实复现的必要条件而非改动。
4. Python 侧使用 python-build-standalone 3.10.13 离线环境（服务器仅有 3.14），tree-sitter 0.20.4 + tree_hugger 0.10.1 + 官方预编译 my-languages.so，语法解析实测通过。

### 语料与模板重建（按"缺失则从 artifact 倒推"原则）
原始 EvoSuite 测试语料与 test_harness 模板**仅存在于 docker 镜像内部**（GitHub 仓库、Zenodo 存档、TOGLL artifact 均不含）。重建方法：
- **语料重建（严格等价，非近似）**：`gen_tests` 仅从原始语料提取 import 块，且最终 import = harness静态集 ∪ 原始import。用 artifact 已交付生成测试的 import 集作为语料 import，数学上产出严格相同结果（幂等性：harness ∪ ((harness ∪ orig) − harness) = harness ∪ orig）。
- **模板重建（经正向验证）**：从 125 个交付实例逆替换重建 ESTest.java/ESTest_scaffolding.java 模板；正向填充后与交付文件**规范等价**（import 顺序本身在原作者管线中由 Python set 迭代产生，跨运行不可复现，故采用排序规范化比对）。
- 重建发现的关键细节：harness 静态 import 含 `java.util.Random` 共 8 项（全实例共性分析确定）；harness 占位符为 `{TEST_CLASS_NAME}` 而脚手架为 `{TEST_CLASS}`；`{TEST_CASES}` 前有两个空格缩进。

### 复现过程中排除的环境障碍（供后人参考）
1. Windows git autocrlf 污染全部文本文件为 CRLF → `git apply` 严格校验失败（补丁上下文含 CR）→ 字节级去 CR 后解决。**这是最后一个阻塞点**。
2. bare git 仓库 zip 提取丢失空目录（refs/heads 等）→ git 拒绝识别仓库。
3. Ubuntu `python3 -m venv` 缺 pip（无 ensurepip）→ 改为 wheel 直解或 standalone python。

## 三、执行规模与资源
- 6 个组合（TOGLL/TOGA × 3 类预言机），覆盖 8 个缺陷（Cli-29/40, Compress-1/27, Gson-4, JacksonCore-2/8/14/22）的全部 scoped 测试行。
- 每个套件完整流程：双版本检出 → 补丁应用 → 项目编译 → 生成测试编译 → 双版本执行 → 结果判定。单套件约 2-4 分钟。
- 服务器 CPU 占用限制在 4 核低优先级，未影响同机其他实验。

## 四、TOGA prefix_only 8 行偏差的根因分析（重要复现发现）

偏差行全部位于 TOGA/prefix_only/Gson-4，且呈 failed_buggy/failed_fixed 镜像翻转。逐层排查确认根因链：
1. `aggregate_test_cases.py` 用 `glob(bug_dir+'/*')` 遍历测试目录且**不排序**——聚合后类内测试方法顺序依赖文件系统枚举顺序，跨机器不可复现。
2. 去重改名 `test_name + counter` 同样依赖遍历顺序（test421/422/423 实为 test42 的重复实例）。
3. Gson JsonReader/JsonWriter 流式测试存在顺序依赖（共享状态），不同执行顺序产生不同 pass/fail。
4. 对比证实：我们聚合文件方法序（test451, test452, ...）与 artifact（test681, test411, ...）完全不同。

**结论：该偏差是原作者管线固有的跨机器不确性，而非我们的环境或重建偏差。** 即使作者换机重跑，这些行也可能翻转。这是论文 artifact 可复现性的一个实质性 caveat，应写入最终报告。值得强调：TOGLL 自身全部 51 行（含全部 assertion/exception 触发样本）不受此影响。

## 五、与指标级复现的衔接

此前已完成指标级复现（Table IV/V 精确匹配，含 65 vs 56 缺陷计数、泄漏审计干净）。本次从头执行验证补强了最后一环：**artifact 记录的执行结果可以被独立重建**。唯一遗留问题：Table V FP 列定义（TOGA 0.45 vs 各候选计算 0.442）仍未对齐，已排除执行层面原因，倾向认为论文该列口径不明或作者脚本外手工调整——建议列入给作者的问题清单。

## 六、GO/NO-GO 结论

**GO**——批准进入第二批复现。依据：
1. 指标级复现精确匹配 + 执行级验证 9/9 样本、TOGLL 100% 一致，两级证据链完整。
2. 全流程零商业 API、零付费依赖，训练/推理/评价均可本地化。
3. 环境已固化在服务器隔离目录，第二批（RQ1 训练复现等）可直接复用基础设施（py310 环境、defects4j、JDK8、传输通道）。

建议第二批顺序：(a) RQ5 全量 374 样本从头执行（可选，约 2-4 小时机时，进一步固化基线）；(b) RQ1 训练管线复现（双 3090，codeparrot-110M 全参数微调）；(c) RQ2 推理分析。
