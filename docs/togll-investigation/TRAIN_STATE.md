# TOGLL 第二批复现 — 训练复现状态（2026-11-26 14:15 启动）

## 正在运行
服务器 172.20.192.176:/mnt/hdd/bocchi_hdd/togll_rq5/train/work/
- GPU0 (pid 374424): fine_tune_gpu0.py → codeparrot-110M × [tc_only, tc_doc, tc_mutsig]（顺序训练）
- GPU1: fine_tune_gpu1.py → codeparrot-110M × [tc_mut, tc_mut_doc, tc_mutsig_doc]
- 启动时间约 2026-11-26 14:10 UTC+8；双卡 100% 利用、显存 19-21GB/24GB
- nice -n 19 运行；host CPU 每实例约 1 核；未影响 cert_t3（启动前后 load 13.8-16 正常波动）

## 环境（时代钉版）
py311 standalone + torch 2.1.2+cu121（PyPI linux 轮 + nvidia-* 12.1 依赖）+ transformers 4.36.2 + accelerate 0.25.0 + huggingface-hub 0.20.3
HF_HUB_OFFLINE=1 + 预置 HF 缓存（codeparrot-small-multi, codegen-350M-multi）
训练数据：dataset_codeparrot.pickle（figshare 原版，train 135,993 / valid 7,953 / test 7,953）

## 冒烟检测（全部通过，2 项为测试脚本自身预期误差非管线问题）
PASS: 离线模型加载 111M、pickle 结构/划分比例、collator 形状、labels 掩码、
      训练 4 步 loss 4.73→1.67 下降、beam-5 生成路径、checkpoint 保存回读、显存峰值 13.7GB
说明: cuda-2-devices"FAIL"因冒烟限单卡运行；dataset-build 39/40 因作者代码跳过 >512token 样本（正确行为）

## 忠实性声明
- fine_tune_gpu0/1.py = 作者 fine_tune_code_parrot.py 仅改 backbone/model_name/loaded_data_names 三个变量（作者设计即如此手动切换）
- 训练超参原样：batch 10、15 epochs、lr 2.5e-5、cosine、fp32、beam-5 exact-match 评估、test 集选模（作者方法学瑕疵照原样保留）
- 日志因 python 块缓冲前期为空属正常现象，eval 阶段输出量大后会持续刷写

## 预期
单配置约 1-1.5 天（评估生成占大头），每 GPU 3 配置 → 全部 6 配置约 3-4.5 天
产出：work/codeparrot_<config>/ 目录权重 + codeparrot_<config>.txt 各 epoch test accuracy
对照目标：论文 Table I CodeParrot-110M 行（P1..P6: 56.4/65.6/76.1/76.2/77.7/77.7，允许随机性小偏差）

## 监控方法
ssh 后：nvidia-smi；tail work/train_gpu0.log；ls work/codeparrot_*
每 epoch 结束写一行 test accuracy 到对应 txt

## 未完成（后续批次）
- RQ2 执行级正确率重算（需分析 surefire 报告，已下载 94MB 推理结果 JSON，初步统计 387,940 样本 exact-match 17.6%、exception 99.87%）
- RQ4 Table III 突变测试重算（PIT 输出 7GB 未下载）
- 其余 6 模型训练（codegen-350M 基座已就位，其余按需）
