---
name: drama-de-ai
description: >-
  Universal Chinese short-drama script de-AI skill. Dynamically extracts project
  character voices, lore redlines, and format constraints from local bibles into a
  project profile, then strips AI-flavored action cues, template acting tags, and
  over-polished dialogue while running a configurable audit script. Use when
  polishing, auditing, or onboarding any Chinese vertical/short-drama script project.
---

# Drama De-AI（通用短剧剧本去 AI 味规范）

面向所有中文竖屏/横屏短剧剧本的通用去 AI 味技能。融合 `oh-story-claudecode`（`deslop-guide`/`short-deslop`/`banned-words`）、`avoid-ai-writing-zh`、`Humanizer-zh`、`remove-ai-flavor` 与 `plainspoken-writing`（`voice-dissolver`）方法论。

**设计原则**：**技能本身零写死业务设定**；所有人物口癖、禁止词与篇幅红线，均在首次进入新项目时从项目设定文档（或向作者提问）**动态提取**到项目根目录的 `.drama-deai-profile.md` 与 `.drama-deai-config.json`。

---

## 工作流程

### Step 0：动态建档（新项目首次运行必做）

检查当前项目根目录是否已存在 `.drama-deai-profile.md` 和 `.drama-deai-config.json`：

- **若已存在**：直接读取二者，进入 Step 1。
- **若不存在（新剧本项目）**：
  1. 扫描项目内的世界观、人物小传、大纲或格式规范文档（如 `设定/`、`人物/`、`01_设定圣经/`、`README.md`、已有样稿集）；若为空白新项目，向用户询问：**题材/口吻、单集目标时长与格式、主要角色说话风格与忌讳词**。
  2. 参照 [profile.template.md](./resources/profile.template.md) 在当前项目根目录动态生成 **`.drama-deai-profile.md`**（记录每个角色的口头禅、专属微动作保护区，以及本剧的物理/世界观不变量）。
  3. 参照 [config.template.json](./resources/config.template.json) 在当前项目根目录动态生成 **`.drama-deai-config.json`**（填入本剧的单集字数/时长范围、禁用词表、限频词与脚本匹配路径；也可先运行 `python <skill>/scripts/audit_drama_deai.py --init` 生成空白模板再填）。

### Step 1：通读保护区与规则
1. 读取项目根的 `.drama-deai-profile.md`，确认“绝对不可洗平的角色口癖与动作指纹”及“不可违背的设定红线”。
2. 加载通用去味细则 [ai-pattern-rules.md](./references/ai-pattern-rules.md)。

### Step 2：分三层局部改写（严禁借去味篡改剧情）
1. **`△` 动作行**：砍强渲染副词（`猛地/死死/骤然/陡然/瞬间/齐刷刷/缓缓`）、去小说心理概括、删除重复的说明书式长定语（只留“镜头拍得到的物理变化”）。
2. **`（）` 表演括号**：执行「身体反应删除测试」，拆掉 `沉声/高声/一字一顿/冷笑` 等万金油标签，替换为 `.drama-deai-profile.md` 里该角色专属的习惯动作、呼吸气口，或直接让台词说话。
3. **角色台词（大白话还原 + 去 AI 腔）**：砍无靶子`不是…而是…`、控破折号 `——`（建议单集 `≤ 2` 处）、去同义双重表述与翻译腔、拒绝假口语混搭；同时反「电报式过度精简」与机械工整对仗——补全日常称谓、主谓宾、语气助词与完整数词（禁「百二十」类省字数词，与「今日/已过/待记录」等书面压缩词），打磨出贴合角色身份、一听就懂的活人交锋大白话。

### Step 3：回归自检与脚本验货（必过门禁）
1. 回读对照原稿与 `.drama-deai-profile.md`：确认没有删掉关键情节点、人物口癖或破坏时间线/物理设定。
2. 大声朗读检验：凡念起来像播音员朗诵、或不同角色像同一张嘴的句子，重新改口语。
3. 运行通用审计脚本（自动读取项目根目录 `.drama-deai-config.json`，若无配置则按通用中文短剧基线扫描）：
   ```bash
   python .agents/skills/drama-de-ai/scripts/audit_drama_deai.py <目标剧本文件或目录>
   ```
   （全局安装时替换为对应的 `<skill目录>/scripts/audit_drama_deai.py`）
4. 确认**硬合规 `FAIL = 0`**，且 AI 味信号降至阈值内（`PASS` 或仅余剧情/白名单刻意保留项）。

---

## 跨项目复用与全局安装

本 Skill 文件夹本身不含任何特定剧本硬编码，可直接整目录复制到以下任一路径供所有新项目复用：
- Antigravity 全局技能：`~/.gemini/config/skills/drama-de-ai/`
- 项目级共享技能：`<新剧本仓库>/.agents/skills/drama-de-ai/`
