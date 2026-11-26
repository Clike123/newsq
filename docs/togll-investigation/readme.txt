Artifact: TOGLL: Correct and Strong Test Oracle
Generation with LLMs
1 Purpose
This artifact is prepared for the paper TOGLL: Correct and Strong Test Oracle
Generation with LLMs, published in the ICSE’25 technical track. It provides
all required datasets and scripts, which are publicly available on Figshare.
We are applying for the Available badge, as the artifact meets the criteria for being
fully accessible to the public.
2 Provenance
The artifact can be obtained from https://doi.org/10.6084/m9.figshare.28282721.v3.
Additionally, the preprint of the paper is available at https://arxiv.org/abs/2405.03786.
3 Data
The artifact consists of the following items:
• pyproject.toml: A configuration file listing the required dependencies with
their specific versions.
• RQ1: This folder contains the dataset used for fine-tuning the TOGLL model.
It also includes the necessary scripts to prepare the data, fine-tune the models,
and perform inference on the fine-tuned models.
• RQ2: This folder contains the dataset used in the paper to perform unseen
inference on 25 Java systems. It also includes scripts to perform the inference.
• RQ4: This folder contains 25 Java systems along with:
1
---PAGE---
– EvoSuite-generated tests,
– TOGLL-generated tests, and
– Tests with no assertion oracles.
These test suites were used to perform mutation testing using PIT to assess and
compare their bug detection effectiveness. PIT is a publicly available tool and
can be easily used via a Maven plugin.
• RQ5: This folder contains the necessary resources to perform the real bug
detection study using the Defects4J dataset for RQ5. It includes:
– Resources necessary for conducting the study using TOGA and TOGLL,
– A detailed README file with instructions to:
∗ Regenerate TOGA results using the TOGA Docker container,
∗ Generate test oracles using TOGLL for the Defects4J dataset, and
∗ Scripts to analyze and compare the results.
4 Required Dependencies
The artifact requires the following dependencies, along with their respective versions,
to run successfully:
• Python: 3.11 or above
• Transformers: 4.36.1
• Torch: 2.1.2
• Accelerate: 0.25.0
• Javalang: 0.13.0
• Matplotlib: 3.8.2
• Deepspeed: 0.13.2
2
---PAGE---
