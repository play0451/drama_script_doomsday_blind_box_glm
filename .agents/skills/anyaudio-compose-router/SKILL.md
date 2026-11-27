---
name: anyaudio-compose-router
description: >-
  Universal composition and arrangement router uniting the `mc-*` pipeline
  (primary backbone: S0-S4 gates, ARR-SPEC, subtraction, spectral layering,
  AI-tell audit), `music-composition` (secondary theory, genre, and feedback
  diagnosis advisor), and AnyAudio tools (`anyaudio_sources`, `anyaudio_project`,
  `anyaudio_music`, `anyaudio_sing`). Use whenever composing, arranging,
  scoring video/short-drama/game cues, or revising existing AnyAudio tracks so
  skills never conflict and every piece lands cleanly in the ClipBay DAW.
---

# AnyAudio Compose Router（通用作曲编曲与 AnyAudio 落地总路由）

面向所有视频配乐、竖屏短剧母题、游戏 BGM、纯器乐与带词歌曲的**通用作曲编曲总路由技能**。本技能零硬编码任何具体剧目或项目，将三套能力固定为清晰的「主骨架 ＋ 专家顾问 ＋ 唯一执行层」流水线，防止多技能规则冲突、默认值滑坡或直接跳过设计写音符。

---

## 一、技能定位与权限边界（铁律，不可颠倒）

| 层级 | 指定技能 | 唯一职责 | 严禁越界 |
|---|---|---|---|
| **1. 主流程骨架（主）** | **`mc-workflow`** 领衔的 `mc-*`（29 项） | 负责 `S0` 立意 ➔ `S1` 曲式骨架 ➔ `S2a` 动机发展（`mc-development`）➔ `S2b` 旋律和声 ➔ `S3` 编制/能量下降/减法/频谱分层（`mc-arrangement-arch`、`mc-texture-layering`、`mc-style-cinematic`）➔ `S7` 机器指纹验收（`mc-ai-tell-audit`） | 到达 `S5` 时**停止**，**禁止**调用 `mc-render-compile` 编译 Suno / YuE2 提示词；AnyAudio 环境以本路由第四节编译执行 |
| **2. 理论与诊断顾问（辅）** | **`music-composition`** | 仅在 3 类场景按需通过 `references/00-navigation.md` 查表（每次最多读 1～3 份参考）：<br>① **非流行/影视/游戏/介质体裁规范**（`genres/film-tv-scoring.md`、`game-music.md`、`electronic-edm.md` 等）<br>② **特殊调式/紧张张力/非对称拍**（`harmony/modal-harmony.md`、`chromatic-harmony.md`、`rhythm-groove/odd-meters-polyrhythm.md`）<br>③ **用户模糊听感反馈翻译**（`creative-workflows/revision-and-feedback-loops.md`、`instrument-idiom/*.md`、`critique-and-feedback.md`） | 禁止由它接管工程、MIDI 导出、DAW 操作或混音规则 |
| **3. 执行与剪辑台（落地）** | **`anyaudio-scoring` ＋ `anyaudio-clipbay`** | 负责音源真实性核查（`anyaudio_sources`）、ClipBay 工程创建（`anyaudio_project`）、`score.json` 渲染入轨（`anyaudio_music`）、人声演唱（`anyaudio_sing`）与片段级增益平衡（`mode:"update"` / `mode:"render"`） | 禁止绕过工程出散装 WAV；禁止在无工程/无规格时直接猜写音符 |

### 技能目录自动解析顺序（跨项目通用）
读取 `mc-*` 或 `music-composition` 下属文件时，按以下顺序定位首个存在路径（兼容不同宿主与设备）：
1. `<当前工作区>/.agents/skills/`
2. `~/.agents/skills/`
3. `~/.dsh/skills/`（如 `C:\Users\admin\.dsh\skills\`）

---

## 二、Step 0：任务定型与模式路由（先判型，再干活）

每次接到新创作或修改任务，先从对话与工作区文档动态识别当前模式：

| 模式 | 典型需求 | 流程裁剪与核心约束 |
|---|---|---|
| **Mode A：影视 / 短剧 / 视频 Cue** | 短剧情绪母题（15～60s）、贴画面配乐、宣传片/动画背景音 | • **单一情绪严格隔离**：悬疑推演、紧张对峙、阴森恐怖、喜剧闹剧、温情舒缓**严禁混进同一首**；情绪跨越即独立立项做新曲<br>• **短剧紧凑节奏**：前奏不拖沓（0～2 秒内确立律动或悬念钩子），允许精简为 2～4 段短弧线（豁免流行 3 分钟分段与强制 bridge，但仍须保留能量起伏与减法留白）<br>• **人声避让**：主声部避开 `300Hz～3kHz` 对白核心区或保持极稀疏留白；统一 `stems: true` 输出分轨 |
| **Mode B：独立器乐 / 游戏循环** | 完整纯器乐曲、游戏大世界/战斗循环 BGM | • 走完整 `mc-workflow` S0～S4 门禁（`vocal` 留空豁免 15、16 条）；循环曲检查首尾小节与混响尾无缝衔接 |
| **Mode C：带人声歌曲** | 有歌词的歌曲、唱段 | • 走完整 `mc-workflow` S0～S4 ＋ 上游词作对齐（若有）；人声走 `anyaudio_sing`（已有歌曲必须先查真实曲谱）或 `anyaudio_tts` |
| **Mode D：已有工程修改 / 诊断** | 用户反馈“钢琴太密/太刺耳/不够悬疑/某轨太响”或剪辑台微调 | • **先执行 `anyaudio_project(mode:"read")`**：若提示存在未保存草稿 `project.draft.json`，先读取核对用户在剪辑台的试听改动再动手<br>• **分流执行**：仅改音量/静音/淡变 ➔ 只调 `clip` 或 `track` 属性（**严禁重渲**）；需改音符密度/换音色/推翻重构 ➔ 进第三节诊断路径 |

---

## 三、标准创作执行流（S0 ➔ 剪辑台交付）

### 阶段 1：立意与规模定调（`mc-workflow` S0～S1 + `music-composition` 顾问）
1. 明确 4 件事：**单一核心情绪**、**目标时长与 BPM**、**主/辅调式与禁用元素**（如悬疑/恐怖禁用大三和弦分解与流行沙锤反拍）、**服务对象**（贴画面垫底 vs 独立听觉主体）。
2. 若涉及特定影视/游戏/地域风格或调式色彩（如弗里吉亚、小二度、三全音、奇数拍），先读 `music-composition/references/00-navigation.md` 加载对应的 1～2 份 `genres/` 或 `harmony/` 参考。

### 阶段 2：动机、和声与减法骨架（`mc-workflow` S2a～S3）
写任何音符前，先在脑内/规格草稿过完以下 4 道硬门禁：
1. **动机与展开（`mc-development`）**：写明核心动机（音程轮廓 + 节奏型），后续段落必须是对动机的变奏/裁截/移位/再现，**禁止每段另起炉灶堆砌新旋律**，也不得直接复制旧废案硬改。
2. **和声与情感一致性（`mc-harmony` + `music-composition`）**：确认无误触反情绪的“默认大三和弦”或“套路流行进行”。
3. **编曲结构与减法（`mc-arrangement-arch`）**：必须设计至少 1 次**能量下降 / 抽空留白 / 乐器提前退场**，禁止所有乐器从第 0 秒铺满到尾、禁止能量单调递增。
4. **织体与频段预算（`mc-texture-layering` + `mc-style-cinematic`）**：
   - 分清**前景 / 中景 / 背景**三层；
   - 按 `mc-style-cinematic` §3 标出各声部是**纯音色层**还是**混合音色层**；
   - **碰撞优先在谱面解决**（错开音区、减少密集点、交替出现），不要把编曲拥挤留给混音硬压。

### 阶段 3：真实音源核查与建工程（`anyaudio-scoring` + `anyaudio-clipbay`）
1. **查真实清单**：每次会话写谱前必须调用 `anyaudio_sources(action:"list")`，对具体 SF2/VST3 再调用 `anyaudio_sources(action:"presets", source:"<id>")`。
   - **铁律**：绝不凭 GM 常识盲猜非 GM 音色库（如管弦乐库 `Sonatina`、`squidfont`）的 program 号；慎用部分 SF3 里依赖未发送 CC 才发声的 `Expr.` 扩展预设（实测前先确认或优先使用 bank 0 标准预设）。
   - **鼓组铁律**：鼓组固定来自默认 SoundFont，写 `drums:true` 时使用 `DRUM_MAP` 名称（如 `kick-soft`、`hat-closed`）。
2. **建工程与上限控制**：
   - 调用 `anyaudio_project(mode:"create", name:"<内容语义名>")` 获取 `projectId`。
   - **单个工程上限 20 轨 / 15 分钟**：若系列母题库多首均用 `stems: true` 分轨导致总轨数将超 20 轨，按每首独立建工程（如 `<系列>_M1<情绪>`）或按相同配器职能归并分轨。

### 阶段 4：编译 `score.json` 并分轨渲染
1. **落盘谱文件**：长谱面统一写入 `<工作区>/.anyaudio/scores/<曲名>.json` 再传文件路径给 `anyaudio_music`，避免参数内联出错。
2. **音符写法与人味**：
   - `stems: true`，单首建议控制在 `3～6` 轨（总不超过 16 轨）；
   - 加入合理的 `humanize: { timingMs, velocity }` 与渐强/渐弱 `expr`（CC11）呼吸曲线，避免所有音符同力度死板对齐网格（`mc-ai-tell-audit` #8）。
   - 需要骤断收尾（如断电/强卡点）设 `tailSec: 0`；常规曲目留 `1.5～2.5s` 自然尾音。

### 阶段 5：电平平衡、去 AI 味终检与交付
1. **读实测电平并改片段增益**：读取 `anyaudio_music` 返回的每轨 `rmsDb` 与警告，用 `anyaudio_project(mode:"update", target:"clip", field:"gainDb")` 拉齐各轨相对平衡（**严禁为了调平衡重渲整首**）。
2. **过 `mc-ai-tell-audit` 终检**：重点自检第 2 条（是否有下降与留白）、第 6 条（是否有非人声记忆钩子）、第 8 条（是否全曲机械网格化）、以及频段是否抢占对白中频或高频刺耳。
3. **导出试听**：调用 `anyaudio_project(mode:"render", format:"wav", output:"...")` 输出试听混音（核验无削波 `peak <= -1 dBFS`，RMS 合理），同步交出工程名、`projectId`、分轨构成与可调建议。

---

## 四、收到听感反馈时的快速路由（诊断闭环）

| 用户反馈症状 | 先查原因归属 | 路由动作 |
|---|---|---|
| **“某轨太响 / 太轻 / 某两轨放一起刺耳想去掉”** | 剪辑台平衡问题 | 读 `project.draft.json` / `read` ➔ 直接 `update` 调 `gainDb` 或 `muted:true` + 重新 `render`（不重渲素材） |
| **“节奏太慢 / 拖沓 / 不像短剧”** | 曲式密度与律动问题 | 读 `mc-rhythm-section` / `music-composition` `rhythm-groove/` ➔ 提速 + 改用短促脉冲/切分低音，砍掉拖沓铺底 |
| **“还是有点欢快 / 味道不对”** | 调式与伴奏织体错配 | 读 `music-composition` `harmony/modal-harmony.md` ➔ 清查并删除大三和弦与流行 2/4 拍反拍/沙锤，改用持续音、小二度、三全音、非对称拍 |
| **“钢琴 / 某乐器点太多、太满”** | 织体密度与前景冲突 | 读 `mc-texture-layering` §3-4 ➔ 大幅删减音符做减法（例如主奏钢琴减至稀疏冷点），将推进任务移交给低频脉冲或弦乐 |
| **“一首曲子塞了不同场面的情绪，不搭”** | 情绪混装违规 | **不许修补凑合**，立刻按 Mode A 拆分情绪，独立建新工程从头创作 |
