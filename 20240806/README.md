# NCHC End-to-end LLM Bootcamp 2024 - NVIDIA NeMo 大型語言模型框架

<!--
**報名日期**：自即日起到 2024 年 07 月 16 日 截止

**報名網址**（2024/08/07 的實體課程）：<https://www.openhackathons.org/s/siteevent/a0CUP00000L45Bx2AJ/se000345>
  -->

**活動問券**：

您的回饋是我們舉辦類似活動的依據，煩請撥冗填寫以下的問券。

> <https://forms.office.com/r/F9eAqgv1Wy>

**師資陣容**：

 -  Cliff CHIU (NVIDIA)
 -  Johnson SUN (NVIDIA)
 -  Yang-Hsien LIN (NVIDIA)
 -  Virginia CHEN (NVIDIA)
 -  Iven FU (NVIDIA)
 -  Jay CHEN (NVIDIA)

**課程內容**：

 -  **線上課程**：2024 年 08 月 06 日 09:00 AM - 13:00 PM

    透過 [Microsoft Teams](https://teams.microsoft.com/) 連線舉辦

    |        時間         | 活動內容 |
    | :-----------------: | -------- |
    | 09:00 AM - 09:30 AM | Welcome and Connecting to a Cluster |
    | 09:30 AM - 10:20 AM | Introduction to End-to-End Large Language Model Pipeline (Lecture) |
    | 10:20 AM - 10:30 AM | Break |
    | 10:30 AM - 11:20 AM | Hands-on with NeMo Framework (Lab) |
    | 11:20 AM - 11:30 AM | Break |
    | 11:30 AM - 12:30 PM | Hands-on Fine-tuning with Custom Data (Lecture and Lab) |
    | 12:30 PM - 01:00 PM | Q&A |

    **活動影片**：<https://youtu.be/8sXqLQOFgqs>

 -  **實體課程**：2024 年 08 月 07 日 09:00 AM - 16:30 PM

    **活動地點**：國網中心新竹本部（新竹市東區研發六路 7 號）

    |        時間         | 活動內容 |
    | :-----------------: | -------- |
    | 09:00 AM - 09:10 AM | Welcome to the Bootcamp |
    | 09:10 AM - 09:30 AM | Environment setup and connecting to the cluster |
    | 09:30 AM - 12:00 PM | Hands-on with NeMo Framework (Lab) |
    | 12:00 PM - 01:00 PM | Lunch |
    | 01:00 PM - 02:00 PM | Hands-on with NeMo Framework (Lab) |
    | 02:00 PM - 02:10 PM | Break |
    | 02:10 PM - 03:10 PM | Hands-on LLM deployment using TensorRT-LLM (Lab) |
    | 03:10 PM - 03:20 PM | Break |
    | 03:20 PM - 04:20 PM | Introduction to NeMo Guardrails (Lecture and Lab) |
    | 04:20 PM - 04:30 PM | Q&A |

    **活動教材**：<https://github.com/j3soon/LLM-Tutorial>

**預備知識**：

 -  Basic experience with Python and Deep Learning
     -  The Python Tutorial, <https://docs.python.org/3/tutorial/index.html>
     -  Deep Learning with PyTorch: A 60 Minute Blitz, <https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html>
 -  Free [NVIDIA Deep Learning Institute (DLI)](https://www.nvidia.com/zh-tw/training/) course to learn fundamentals, <https://developer.nvidia.com/join-nvidia-developer-program>
 -  End-to-End LLM Bootcamp Open Source, <https://github.com/openhackathons-org/End-to-End-LLM>

**課外讀物**：

 -  [LLM Twin Course: Building Your Production-Ready AI Replica](https://github.com/decodingml/llm-twin-course)
 -  [End-to-end LLM Workflows Guide](https://www.anyscale.com/blog/end-to-end-llm-workflows-guide)
 -  [A Survey of Large Language Models](https://arxiv.org/abs/2303.18223)
 -  [A Comprehensive Overview of Large Language Models](https://arxiv.org/abs/2307.06435)
 -  [A Comprehensive Survey of LLM Alignment Techniques: RLHF, RLAIF, PPO, DPO and More](https://arxiv.org/abs/2407.16216)
 -  [Foundational Challenges in Assuring Alignment and Safety of Large Language Models](https://arxiv.org/abs/2404.09932)
 -  [Awesome Generative AI Guide](https://github.com/aishwaryanr/awesome-generative-ai-guide)
 -  [OpenAI Cookbook](https://github.com/openai/openai-cookbook)
 -  The three-part series on how Imbue trained their 70B model
     -  [Training a 70B model from scratch: open-source tools, evaluation datasets, and learnings](https://imbue.com/research/70b-intro/)
     -  [Sanitized open-source datasets for natural language and code understanding: how we evaluated our 70B model](https://imbue.com/research/70b-evals/)
     -  [From bare metal to a 70B model: infrastructure set-up and scripts](https://imbue.com/research/70b-infrastructure/)
     -  [Open-sourcing CARBS: how we used our hyperparameter optimizer to scale up to a 70B-parameter language model](https://imbue.com/research/70b-carbs/)
 -  [NVIDIA NIM](https://www.nvidia.com/en-us/ai/)
 -  [NVIDIA NeMo](https://www.nvidia.com/en-us/ai-data-science/products/nemo/)
 -  [NeMo: a toolkit for building AI applications using Neural Modules](https://arxiv.org/abs/1909.09577)
 -  [ChipNeMo: Domain-Adapted LLMs for Chip Design](https://arxiv.org/abs/2311.00176)
     -  See also: [SemiKong](https://www.semikong.ai/) and [SemiKong's github](https://github.com/aitomatic/semikong)
<!--

# Performance

**ChipNeMo**

Demonstrates improved performance over baseline models like LLaMA2 across various benchmarks. For instance, ChipNeMo-13B outperforms LLaMA2-13B in several metrics such as MMLU, Reason Code, and others, indicating its effectiveness in adapting to domain-specific tasks like chip design

 -  **Architecture**: ChipNeMo is designed for efficient chip-level neural network model design and optimization. It provides advanced algorithms to improve the accuracy and efficiency of chip designs.
 -  **Optimization**: ChipNeMo integrates with various optimization techniques for both chip design and neural network training, aiming to enhance performance in specific hardware contexts.
 -  **Scalability**: The focus is on scalability and customization for different chip architectures, potentially offering high performance for specific tasks.

**SemiKong**

While specific performance metrics for SemiKong are not provided, similar tools often focus on providing accurate and efficient solutions for their intended domains. Performance would typically be evaluated against industry standards, competitor products, or custom benchmarks relevant to the tool's application area.

 -  **Architecture**: SemiKong is a platform designed to optimize the performance of semiconductors and related technologies. It leverages AI and machine learning for chip design and performance analysis.
 -  **Optimization**: Provides tools for improving semiconductor design and testing, with a focus on enhancing the performance of semiconductor devices.
 -  **Scalability**: Targets broad applications within the semiconductor industry, potentially offering high performance across a range of semiconductor technologies.

# Usability

**ChipNeMo**

Offers enhanced usability through features like automatic generation of EDA scripts and bug summarization and analysis, which are crucial for chip design tasks. These functionalities aim to streamline the workflow for users dealing with complex chip designs.

 -  **Target Users**: Typically used by engineers and researchers specializing in chip design and hardware optimization.
 -  **Complexity**: ChipNeMo might require a deep understanding of both neural network principles and chip design to effectively utilize its features.

**SemiKong**

Usability would likely involve ease of integration into existing workflows, intuitive interfaces for non-experts, and comprehensive documentation. Tools in this space often prioritize user experience to facilitate adoption and effective problem-solving.

 -  **Target Users**: Aimed at semiconductor engineers, designers, and researchers working on semiconductor technology and chip design.
 -  **Complexity**: Offers tools that may be more user-friendly with a focus on practical applications in semiconductor design, potentially making it more accessible to users less specialized in neural network design.

# Features

**ChipNeMo**

Incorporates domain-adapted large language models (LLMs) specifically tailored for chip design, leveraging techniques like tokenizer augmentation and parameter-efficient fine-tuning. This specialization allows ChipNeMo to handle domain-specific tasks more effectively

 -  **Integration**: It integrates with existing EDA (Electronic Design Automation) tools, providing a seamless workflow for chip design.
 -  **Customization**: Offers specialized tools for customizing and optimizing neural networks for specific chip architectures.
 -  **Focus**: Primarily focused on the intersection of hardware design and neural network optimization.

**SemiKong**

Features would typically align with the tool's purpose, whether it's simulation, optimization, verification, or another aspect of chip design. Common features might include support for various file formats, integration with popular EDA tools, and advanced analytics capabilities.

 -  **Platform Integration**: Provides a comprehensive platform with tools for design, simulation, and testing of semiconductor devices.
 -  **AI Integration**: Utilizes AI to optimize semiconductor performance, offering advanced analytics and insights.
 -  **Focus**: Broad focus on the semiconductor industry with tools tailored for various aspects of semiconductor design and optimization.

# Key Differences

 -  **Specialization vs. Generalization**: ChipNeMo is specialized for chip design, incorporating domain-specific adaptations to enhance performance on related tasks. SemiKong, while not explicitly described, would likely offer a broader set of features or applications outside the narrow scope of chip design.
 -  **Performance Metrics**: ChipNeMo demonstrates superior performance in several benchmarks relevant to chip design, suggesting it may outperform SemiKong in these specific areas unless SemiKong has been optimized for similar tasks.
 -  **Usability and Integration**: Both tools would aim for high usability, but ChipNeMo's focus on automating specific aspects of chip design could make it more appealing for users looking for streamlined processes. SemiKong's approach might differ, focusing on broader applicability or integration capabilities.

# Summary

ChipNeMo stands out for its specialized performance in chip design tasks, thanks to its domain-adapted LLMs and innovative features like automatic script generation and bug analysis. Without explicit details on SemiKong, it's challenging to make a direct comparison, but typical tools in this space would compete on features, performance, and usability, potentially offering a broader range of applications or easier integration into existing workflows.

 -  **Usability and Integration**: Both tools would aim for high usability, but ChipNeMo's focus on automating specific aspects of chip design could make it more appealing for users looking for streamlined processes. SemiKong's approach might differ, focusing on broader applicability or integration capabilities.
 -  **ChipNeMo** is specialized for optimizing neural networks in the context of chip design, focusing on high performance for specific chip architectures and requiring a good grasp of both neural network and hardware concepts.
 -  **SemiKong** provides a broader platform for semiconductor design and optimization, integrating AI for performance improvements and being potentially more accessible to a wider range of users in the semiconductor field.
  -->
 -  [AI, Go Fetch! New NVIDIA NeMo Retriever Microservices Boost LLM Accuracy and Throughput](https://blogs.nvidia.com/blog/nemo-retriever-microservices/)
 -  [NVIDIA AI Foundry 為全球企業打造客製化 Llama 3.1 生成式 AI 模型](https://blogs.nvidia.com.tw/blog/nvidia-ai-foundry-custom-llama-generative-models/)
<!--
 -  Repository of NCHC-NVIDIA Joint Lab, <https://github.com/nqobu/nvidia>
 -  [NVIDIA AI-Agent 暑期線上訓練營](https://jsj.top/f/ilF0yi)
 -  [LLM Engineer's Handbook: Master the art of engineering Large Language Models from concept to production](https://www.amazon.com/dp/1836200072)
 -  [Build a Large Language Model (From Scratch)](https://www.manning.com/books/build-a-large-language-model-from-scratch)
 -  [Understanding Large Language Models: Towards Rigorous and Targeted Interpretability Using Probing Classifiers and Self-Rationalisation](https://liu.diva-portal.org/smash/record.jsf?dswid=-2318&pid=diva2%3A1848043). \[[PDF](https://liu.diva-portal.org/smash/get/diva2:1848043/FULLTEXT01.pdf)\]
  -->

**聯絡窗口**：吳先生 &lt;[z@narlabs.org.tw](mailto:z@narlabs.org.tw)&gt;

**聯絡電話**：[(03)5776085 分機 220](tel:+886-3-5776085,220)

**附註**：

 1. **本次活動將完全以中文進行。**\
    **This event will be conducted entirely in Mandarin Chinese.**

 2. **2024/08/07 的實體課程僅限臺灣地區之人士報名參加。**\
    **The offline course on 2024/08/07 is open to those living in Taiwan only.**

 3. 所有活動的通知訊息，都將透過 email 發送，請在報名時務必留下可以聯絡到的 email 信箱。\
    All notifications for this event will be sent via email, so please provide a valid email address when applying.

 4. 本主辦單位保留接受報名及審核報名資格之權利，並於活動前寄發相關通知。\
    The organizer reserves the right to accept applications and review eligibility, and will send relevant notifications before the event.

 5. 活動前如未收到核可通知，即意謂您未通過報名的審核。\
    If you do not receive an approval notice before the event, it means your application has been denied.

 6. 建議您攜帶自已的筆記型電腦參加 2024/08/07 的實體課程，期間將提供免費的 WiFi 連線服務及午餐。\
    You are encouraged to bring your own devices to the offline course on 2024/08/07, during which free WiFi connection and lunch will be provided.

<!--
  vim: ft=markdown ic noet nort wrap ts=8 sts=4 sw=4:
  -->
