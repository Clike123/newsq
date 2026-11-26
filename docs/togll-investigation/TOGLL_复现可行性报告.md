# TOGLL 复现资产与可行性调查报告

调查日期：2026-11-26 ｜ 调查方式：远程检查 figshare 复现包（remotezip 按需提取，未全量下载）+ 精读论文全文 + 精读 2026 竞争论文
资产位置：`H:\togll-inv\`（论文全文 txt、17 个关键源码文件已提取至 `extracted/`）

---

## 一、总体结论

**TOGLL 复现资产高度完整，全部环节不依赖任何商业 API，建议作为基础模型原样复现。**

- 微调后模型权重：已提供（最关键资产）
- 训练数据（已分词 pickle + 原始 csv）：已提供
- 训练/推理/评价脚本：已提供
- 各 RQ 的原始实验输出（预测 csv、执行报告、突变测试结果）：已提供
- 商业 API 依赖：无（唯一外部依赖是 HuggingFace 免费模型权重和 Docker Hub 免费镜像）

唯一平台限制：Defects4J 执行与 PIT 突变测试需要 Linux/Docker；但**模型训练与推理可以在 Windows 本地 5070 上原生运行**，且 RQ5 的 Table IV/V 可以不做任何执行、直接从已包含的结果文件重新算出。

---

## 二、逐项核实结果

### 1. 核心算法源码是否完整 —— 完整

RQ1 含 5 个脚本：`prepare_dataset.py`（数据准备）、`dataset.py`/`dataset_batch.py`（数据集类）、`fine_tune_code_parrot.py`（训练）、`inference.py`（推理）。RQ5 含独立的推理与结果分析脚本。已逐一提取并通读，逻辑完整无截断。

### 2. 七种模型的训练脚本及训练数据 —— 提供

- 训练脚本名义上叫 `fine_tune_code_parrot.py`，实际是**通用脚本**：文件头部的 `model_data` 列表覆盖全部 7 个模型，手动改 `backbone` 变量切换。
- 7 个模型：CodeGPT-small-java (110M)、CodeParrot-small-multi (110M)、CodeGen-350M-multi、CodeGen-2B-multi、PolyCoder-0.4B、PolyCoder-2.7B、Phi-1 (1.3B)。**全部是 110M–2.7B 的开源小模型**。
- 训练数据：每个模型一份已分词 pickle（363–372MB × 7），另有原始 `inputs.csv`（117MB，159,073 样本）和 `meta.csv`（48MB）。SF110 数据集，训练/验证/测试划分已含在 pickle 内。
- 训练配置：全参数微调、batch 10、15 epochs、max_len 512、AdamW lr 2.5e-5、cosine schedule、fp32。原论文用 4×A100-40GB；2B/2.7B 用了 DeepSpeed。
- 注意：脚本用 **test 集 accuracy 做模型选择**（方法学瑕疵，复现时会照搬，但你的改进工作不应继承）。

### 3. 微调后模型权重 —— 部分提供（够用）

| 权重 | 大小 | 位置 |
|---|---|---|
| **TOGLL 最终模型**（CodeParrot-110M, RQ5 用） | 444MB | `RQ5/TOGLL_prediction/model/TOGLL/` |
| codeparrot × 3 种 prompt（tc_mut, tc_mutsig, tc_mut_doc） | 444MB × 3 | `RQ2/inference/run_inference/` |
| codegen-350M × 3 种 prompt | 1.4GB × 3 | 同上 |

未提供全部 7×6=42 个组合的权重，但论文后续实验只用最优组合，**复现主结果不需要重训全部模型**。config.json 确认 TOGLL 权重就是 GPT-2 架构的 codeparrot-small-multi。

### 4. 全部实验评价程序和原始结果 —— 提供

- RQ2：25 个项目的推理结果 JSON（`inference/results/`，59 个文件 94MB）+ 完整项目测试执行输出（surefire 报告）。
- RQ4：25 个项目的 PIT 突变测试完整输出（7GB）。
- RQ5：TOGA 和 TOGLL 的预测 csv + **每个 bug 的测试执行结果**（各约 5500 文件）。
- Table IV/V 可用 `compute_TOGLL_metrics.py`、`compute_TOGA_metrics.py`、`result_analysis.py` **直接从已包含文件重算，无需重新执行**。

### 5. 无商业 API 可否完成全部流程 —— 可以

训练、推理、评价全链路只依赖：HuggingFace 免费基座权重、本地 PyTorch、Maven/PIT（RQ4）、Docker 镜像 `edinella/toga-artifact`（RQ5 从头执行时；已确认 Docker Hub 仍可拉取，1291 次拉取）。无任何 OpenAI/Anthropic 等付费 API。

### 6. 真实缺陷检测实验（RQ5）能否独立复现 —— 能，分两级

- **指标级复现（几分钟）**：直接运行三个分析脚本，从已包含的执行结果重算 Table IV（分类 P/R/F1）和 Table V（TOGLL 检出 65 bugs vs TOGA 56；排除隐含预言机后 64 vs 31）。
- **从头复现（需 Linux/Docker）**：TOGA docker 内含 Defects4J 环境，把预测 csv 用 `docker cp` 传入执行。374 个输入样本（304 断言 + 70 异常），规模很小。

### 7. 论文表格 → 资产映射

| 表格 | 内容 | 复现路径 | 成本 |
|---|---|---|---|
| Table I | 7 模型 × 6 prompt 的 exact match（RQ1） | 需重训（42 组合）；权重未全给 | 最贵，可只做子集 |
| Table II | 断言类型分布统计 | 从 inputs.csv/结果文件统计 | 低 |
| RQ2 正确率表 | 25 项目 oracle 正确率 | 分析已含推理结果+执行报告 | 低 |
| Table III | 突变检测（RQ4，TOGLL vs EvoSuite） | 分析已含 PIT 输出；从头跑需 Maven+长时 CPU | 低/高 |
| Table IV | Defects4J oracle 分类指标 | 直接重算 | 极低 |
| Table V | Defects4J 真实缺陷检出 | 直接重算；从头执行需 docker | 极低/中 |

### 8. GPU 适配性

| 实验 | 5070 (8GB) | 双 3090 (48GB) | 双 4090 (48GB) |
|---|---|---|---|
| 任意模型推理（beam 5） | 充裕（原论文只用 A100-10GB 单卡） | 充裕 | 充裕 |
| 全参数微调 110M/350M/400M | 可行（fp32 约 2–6GB+激活） | 轻松 | 轻松 |
| 全参数微调 Phi-1 1.3B | 紧张（需 8bit 优化器/bf16） | 可行 | 可行 |
| 全参数微调 2B/2.7B | 不可行（fp32 需 32GB+） | 可行（DeepSpeed ZeRO） | 可行且更快 |
| Table IV/V 重算 | 纯 CPU 几分钟 | 同 | 同 |

注意训练脚本内嵌 beam-search 评估（每 epoch 对 test 集生成），是训练时间的主要开销；159K 样本 × 15 epochs，单 prompt 单模型在 5070 上估计需数十小时级，双 3090 可并行两个配置。

### 9. 磁盘占用

- zip 全量：压缩 7.2GB / 解压约 20.5GB（含 25 个 Java 项目源码+执行输出）。
- **按需策略**（remotezip 已验证可行）：
  - RQ5 完整 + TOGLL 权重：约 0.5GB —— 第一批
  - RQ2 推理结果+脚本（不含项目）：约 0.1GB；加重训权重共约 5.6GB
  - RQ1 训练数据+脚本：约 2.4GB —— 需要重训时再下
  - RQ2/RQ4 项目执行输出（10GB+）：仅在需要重算执行级指标时下载
- H 盘 32GB 空闲足够容纳核心资产。

---

## 三、2026 竞争论文判断（arxiv 2608.00884）

**"Documentation vs. Code Patterns: What Drives LLM-Based Exception Oracle Generation?"** —— 同一团队（Hossain, Dwyer）。

已核实的事实：

1. **它已经在用"counterfactual input"这个术语和干预方法论**：删除 Javadoc `@throws` 子句构造反事实输入，观察预测变化；用 gradient×input 归因 + 替代消融找依赖信号。
2. 核心发现：准确率主要由**捷径信号**驱动（表面 token/词汇线索），删除文档后准确率变化不到 1 个百分点。
3. 范围**只覆盖异常预言机的类型分类**，不涉及断言内容正确性。

对你计划方向的判断：

- **未被解决**：错误实现引导（misguidance）——该文不研究"断言是否跟随缺陷实现行为"；不做程序行为层面的干预（变异体）；不涉及断言级诊断；不提出修复机制。
- **已被占用的空间**：在 TOG 领域"输入文本特征的反事实消融诊断"这个方法论标签已被使用。你的 CADA 若投稿，必须把差异钉在：(a) 干预对象是**程序语义/行为**而非输入文本表面特征；(b) 对象是**断言正确性与错误引导**而非异常类型分类；(c) 目标是**检测与修复**而非仅是测量归因。这篇论文必须列为最密切相关工作精读引用。
- 附带收获：它评估了 3 个 TOG 系统（110M–7B），其发现"高准确率来自捷径"恰好**支持**你研究错误引导的必要性——表面准确的预言机可能根本没有语义依据。

---

## 四、风险与注意事项

1. Windows 原生可跑训练/推理，但 RQ4/RQ5 从头执行仍需 Linux/Docker（双 3090 服务器若是 Linux 则可承担）。
2. transformers 4.36.1 + torch 2.1.2 是 2024 年初版本，需注意与 50 系显卡 CUDA 的兼容性——sm_120 需要较新 CUDA toolkit，**torch 2.1.2 很可能不支持 5070**。这是复现的第一个技术风险，可能需要升级 torch 并适配 API 变化（transformers 4.36 与新 torch 通常兼容，但需实测）。
3. 模型选择用 test 集、Table IV 全满分（374 样本小数据集）等，复现时照搬、创新时避免。
4. RQ1 全表（42 组合）重训成本高，建议只复现 TOGLL 实际使用的组合（codeparrot + 最优 prompt）。

## 五、建议的复现顺序

1. **第一批（小时级，纯本地）**：下载 RQ5 全部内容（约 0.5GB）→ 重算 Table IV/V → 与论文数字对齐。
2. **第二批（天级，5070）**：用提供的 TOGLL 权重在 RQ5 输入上做推理，验证推理复现；分析 RQ2 已含结果重算正确率指标。
3. **第三批（按需，3090 服务器）**：重训 codeparrot + 最优 prompt 验证训练管线；docker 内从头执行 RQ5。
4. 全程不重训 42 组合、不下 RQ4 的 7GB 执行输出，除非后续创新实验确实需要。
