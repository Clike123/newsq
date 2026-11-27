# 反事实实验全量结果：断言贡献的因果分解（92 缺陷）

日期：2026-11-27。实验：对 artifact assertion_prefix 组全部 92 个缺陷、295 条输入，
分别执行"有生成预言"与"删除预言"两种变体的完整 Defects4J 双版本管线（共 184 run，
服务器 12 worker 并行 nice-19，未干扰其他实验）。保真度验证：artifact 37 个 TP 缺陷
在本管线全部复现（37/37），零遗漏。

## 核心数字

| 类别 | 缺陷数 | 占比 |
|---|---|---|
| 有预言时可检出（缺陷级） | 38 | 100% |
| 其中：前缀独立即可检出（预言无贡献） | 24 | 63% |
| 其中：预言真正带来新增检出 | 14 | 37% |
| **预言主动破坏检出（总计）** | **19** | — |
| 其中：编译破坏（断言引用不存在成员等） | 11 | — |
| 其中：修复版误杀（断言拒绝正确行为） | 8 | — |

注：19 = 11 + 8 为去重后合计（编译破坏 11 全部 + 修复版误杀 8 全部，无重叠）。
无预言变体检出 43 个缺陷，超过有预言变体的 38 个。

## 归因分布（38 个有预言检出缺陷）

- PREFIX_EXCEPTION（断言未执行，检出与断言无关）：25
- ORACLE_ASSERTION（断言实际触发）：13

## 修复版误杀机制签名（8 缺陷全部同一模式）

buggy 版 PREFIX_EXCEPTION 失败 + fixed 版 ORACLE_ASSERTION 失败：
前缀本可区分两版，但断言对正确行为也报错，检出被抵消。
涉及：Compress-17, Gson-17, Jsoup-34/36/40, JxPath-5, Lang-19, Math-70

## 编译破坏实例

Cli-23: assertEquals(true, options0.isSet()) — Options 无 isSet() 方法
JacksonCore-14/ID252: assertEquals(true, iOContext0.useDirectByteBuffer) — 字段不存在
受影响 11 个缺陷的前缀本可独立检出，全部因编译失败丢失。

## 已标记异常

Jsoup-86：with_oracle 检出但 no_oracle 未检出且归因 PREFIX_EXCEPTION——
前缀异常为非确定性行为，不作为可靠证据。

## 方法与口径

- 输入：artifact 冻结预测，无重新推理/训练
- 检出定义：buggy FAIL 且 fixed PASS（三值逻辑，编译失败/证据缺失=UNKNOWN）
- 缺陷级：任一同缺陷测试检出即为检出（与论文口径一致）
- 语义：paper 的 65 个检出缺陷若含类似比例，则"预言贡献"被系统性高估
