# 研究方向分析与立项判断

方案日期：2026年11月25日；归档日期：2026年11月26日。

## 当前结论

建议有条件开展小规模立项验证，尚不能认定新颖性足够支撑顶刊。AROP 全文和直接竞争方法的细粒度机制对照仍是前置门槛。这里没有已完成的基线复现、训练或增益结果。

## 建议主线

以 BugAuditor 的公开实现为起点，研究带程序证据的条件责任转移学习与组合。首先做显式资源泄漏；引用计数与复杂 C++ 生命周期在首轮机制成立后扩展。

核心问题是区分借用、转移和释放，并保留资源对象、返回条件与接手主体的关联。资源逃逸不能直接等同于义务履行。

## 候选贡献与新颖性风险

1. 联合学习条件、资源身份、责任主体、所需动作与证据，组合未履行义务。关系式摘要及条件所有权已有先例，元组表示本身不构成贡献。
2. 通过程序证据定位摘要冲突并有界细化，配合有效上下文对约束语义敏感性。反例引导和对比学习本身并不新。
3. 用未见项目、API 家族与调用组合验证泛化。基准是算法贡献的支撑，不能代替算法增量。

需重点对照 [AROP](https://conf.researchr.org/details/icse-2026/icse-2026-research-track/201/Project-Level-Resource-Leak-Detection-through-Agent-based-Ownership-Analysis-and-Repa)、[POM](https://sat-group.github.io/ruben/papers/pointer-ownership-lctes26.pdf)、[LAMeD](https://arxiv.org/html/2505.02376v1)、[LLMDFA](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ed9dcde1eb9c597f68c1d375bbecf3fc-Abstract-Conference.html)与[资源规范推断](https://homes.cs.washington.edu/~mernst/pubs/resource-inference-oopsla2023-abstract.html)。未读全的机制不能标为不存在。

## 决定是否继续的实验

同一模型、候选、检索权限和总预算下，比较原基线、扩上下文、自然语言摘要、结构化摘要、责任组合器、组合加细化。核心机制若无法胜过强上下文与摘要对照，就不进入长期微调。

真实缺陷检出、合法上下文误判与新仓库报警精度分开报告。不能用没有 issue 作为安全标签，不能把未知案例从召回分母删除，不能在缺陷总量未知时报告全仓库召回。

## 前两周决策

先完成竞争机制证据表、官方最小活跑和约 60 例独立先导审计。若缺口已被覆盖、真实错误稀少，或增加上下文即可解决，应停止原算法分支或重新定义问题。双 3090 的微调是后续条件分支。

详细的数据、统计、资源、任务依赖与门槛见[完整任务书](research-plan.md)和[任务清单](task-checklist.md)。