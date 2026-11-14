# G0：Chromium 基线构建 Runner 资源测算（Plan only）

> 2026-11-14 计划稿。只供方案比较，不作 Runner 选型，不实施或修改构建代码。以下推荐量级与工时均为粗估，不代表任何一次实测。

## Decision record：2026-11-14 22:57 CST Vultr self-hosted Runner 定版（最新有效）

**用户于 2026-11-14 22:57 CST 最终决定：G0 基线构建机采用 Vultr 按小时租用的临时云服务器，注册为本 fork `Zhanfg/android-titanium-browser` 的 GitHub Actions self-hosted Runner，完成基线构建且确认保存日志与 APK/AAB 产物后删除服务器。** Vultr 为本轮唯一执行落点，不再属于供应商待选方案。具体实例型号、区域、小时费率和磁盘容量未在本次授权消息中给出，不能引用先前 Hetzner CCX33 的配置或价格冒充 Vultr 规格。

| 项目 | 最终决定 / 实施边界 |
|---|---|
| 服务商与计费 | **Vultr 按小时租用**；实际机型、可用磁盘、费用以用户及监督者创建时的订单与实例信息为准，不预设价格 |
| 生命周期 | 为本轮固定基线短期创建，跑完并保存构建证据后**删机**，由用户及监督者确认实际资源已释放 |
| 运行方式 | GitHub 仓库级 **self-hosted Runner**，正常 Linux/x64 标签匹配；不使用 GitHub 或 CircleCI 付费托管 Runner |
| 当前进度 | 用户正在进行 Vultr 账号注册及**支付宝充值**；随后由监督者负责创建服务器、注册 Runner 和实施构建 |
| 权限边界 | 用户与监督者独占账号/付款、虚拟机、Runner 注册/注销、GitHub Build 启用与触发、产物收集及删机操作。实施凭据、注册令牌、API Token、签名密钥均**不进入本会话** |
| 验收状态 | **G0 未过**，尚未取得新服务器的环境实测、基线构建日志和 APK/AAB；G1 PR #2 继续「已写未验（待基线构建）」 |

### 出局与停用链（全部记录于 2026-11-14）

- **GitHub 标准托管 Runner（2026-11-14）**：探针 [Run #43584460871](https://github.com/Zhanfg/android-titanium-browser/actions/runs/43584460871) 拉取前可用 **87.069 GiB**、取源后 **47.440 GiB**，起始磁盘不足 Chromium 官方约 100 GB 的构建规划要求，**出局**。
- **CircleCI 免费档（2026-11-14）**：Machine large 探针 [Pipeline #6](https://circleci.com/api/v2/pipeline/97d5265c-0137-422d-9057-41569d85ee5d) 取源成功后余约 **95 GiB**（精确 **101591863296 字节**），且单 Job 最长 **60 分钟**，完整构建未验证、耗时与空间存在结构性限制，**出局**。注意 95 GiB 与 100 GB 的单位差异，不将取源成功误写为编译成功。
- **Hetzner（2026-11-14；20:43 CST 曾选 CCX33，22:57 CST 撤销）**：用户注册卡在身份验证，**出局**；此前 CCX33 规格、净价和部署计划均为历史废止方案。
- **GCP（2026-11-14）**：用户无试用资格，且 Google 风控不接受用户银行卡，开通失败，**出局**。
- **付费 CI（2026-11-14）**：GitHub Larger runners、CircleCI Performance，**本轮关闭**。
- **其他路线（2026-11-14）**：家用大主机、Oracle 及其他未授权执行落点，**本轮不启用**。

### 启用前的核查范围

- 监督者上线 Vultr 服务器和 Runner 后，以只读方式确认运行环境、标签、磁盘实测与构建适用性；由监督者独立完成付款和凭据保管。
- 现有 `.github/workflows/build.yml` 手动输入默认可选 `self-hosted`，但还含定时触发、Vanadium 自动更新并可能推送、Release 发布及 Attestation；它**不能原样作为固定基线的无发布验证流程**。
- [Draft PR #6](https://github.com/Zhanfg/android-titanium-browser/pull/6) 仅提供不发布版本的手动基线工作流提案及详细启用清单。**未授权合并、启用或触发任何 Build 工作流。**
- 等待监督者明确通知 Runner 已上线并给出后续执行指令；在此之前不再选型、探针、构建或改 G1/G2/G3。

## 历史证据（2026-11-14）：CircleCI large 探针及当时待决事项（已由 22:57 决策覆盖）

**G0 尚未通过，不能将取源 success 写成可构建 Chromium。** 当前仅证明两个标准/免费托管来源具备拉取 Chromium `157.0.8103.78` 源码的能力，均未尝试 `gclient runhooks`、`gn gen`、`autoninja`、APK/AAB、签名与发布。

| 证据 | GitHub 标准托管 Runner | CircleCI Machine large |
|---|---|---|
| 来源 | [GitHub Run #43584460871](https://github.com/Zhanfg/android-titanium-browser/actions/runs/43584460871) | [CircleCI Pipeline #6](https://circleci.com/api/v2/pipeline/97d5265c-0137-422d-9057-41569d85ee5d)、[Job #2](https://circleci.com/gh/Zhanfg/android-titanium-browser/2)、[`probe-report.txt` 原始 Artifact](https://output.circle-artifacts.com/output/job/2e5be9e0-5b9a-489c-b3e1-a4b9fe734211/artifacts/0/g0/probe-report.txt) |
| Job 结论 | success，仅完成取源 | **success**，2026-11-14 11:54:07 UTC 结束，job 耗时 **758915 ms** |
| CPU / RAM | 4 核 / 15.607 GiB | **4 核** / `MemTotal 16083220 kB`（约 **15.34 GiB**） |
| 磁盘 | GitHub 工作区取源前可用 **87.069 GiB**；取源后 **47.440 GiB** | `lsblk` NVMe **150G**，根文件系统约 **145G**；取源前可用 `144291934208` 字节（`df -h` **135G**），取源后可用 `101591863296` 字节（`df -h` **95G**） |
| 源码磁盘增长 | 源码工作目录 `40G` | 取源消耗 **42700070912 bytes**（约 **42.7 GB** 十进制），源码目录 `40G` |
| 标签 / 同步 | `157.0.8103.78`，`sync_complete`、exit `0` | 同标签，`gclient sync -D --no-history --nohooks`、exit `0`，`stage=sync_complete`，取源 **750 秒** |
| 观察项 | `.gclient_entries missing` 非致命告警 | 同一 `.gclient_entries missing` 告警重现，另见 Git 版本建议；均不影响 `exit=0` |
| 对完整构建的结论 | **已排除作为本轮标准 Runner 构建候选**：取源前只有 87.069 GiB，未满足 Chromium 官方最低 100 GB 空闲前提 | **仅取源证据成立，不能宣布具备完整构建能力**：取源后约 95 GiB 的可用空间尚未验证是否足以容纳 hooks、生成文件、双架构 `out/` 输出和缓存 |

**单位核查注意：** CircleCI 的取源后 `101591863296` bytes = **101.592 GB**（十进制）≈ **94.615 GiB**（二进制），`df -h` 因取整显示为 95G。Chromium 官方写 `100GB` 却未明确此处是否采用 GiB；如按 **100 GiB** 的工作规划门槛，它确实低于门槛；按严格十进制 **100 GB** 则略高。因此不能单靠 `95 GiB < 100 GB` 的字符串比较作绝对结论。**无论哪种单位，当前剩余空间尚不足以证明双架构构建可行**；追加 `out/` 构建占用可能达到数十 GB，属于工程风险估算，尚非本仓实测失败。

**报告修正：** CircleCI Job API 记录执行档位为 `large`，4 核、约 15.34 GiB；原 `probe-report.txt` 首部的 `xlarge` 来自脚本静态文案错误，不是实际资源档。已在 <https://github.com/Zhanfg/android-titanium-browser/pull/5> 正文注明，并通过文案修正提交 `69c549a0558ebf1e545235a775a011759c325111` 改为 `large`，提交包含 `[ci skip]`，未授权重新执行探针。历史 Artifact 不做篡改。

**结构性时间限制：** CircleCI Free 计划单个 Job 最长 **60 分钟**；全量 Chromium 双架构构建预计数小时，属于**计划耗时估算与产品时长约束的结构性冲突**，并非一次实际编译超时。不得自行将探针延展为构建。

**历史状态（22:57 CST Vultr 决策前）：** 是否考虑付费档位、其他执行机器、或拆分 Job/缓存等构建架构，需要另行授权和更详细测算。此前关闭的家用主机及租机方案不会自动恢复。**CircleCI 探针线已结束，停止进一步重跑、降档、换 executor、修改仓库/付款设置。G0 未过，G1 PR #2 保持「已写未验（待基线构建）」，G2/G3 停止在原阶段。**

## 历史决策记录（2026-11-14）：最初选择 GitHub 托管进行探针，现已被 Vultr 决策取代

**2026-11-14 早期决策记录：先选择 GitHub 托管 Runner 进行取证（标准档现已在后续探针中排除）。** 家用高配主机自托管和临时租高配云机两条路线关闭，不再准备。下文第三节原有三种落点对比保留为历史估算，不再代表待选方案。

GitHub 托管分两档，授权与资源边界不得混淆：

| 档位 | GitHub 官方规格与资格 | 当前授权 |
|---|---|---|
| **标准托管 Runner（`ubuntu-latest`，公开仓库）** | 最初列出的标准 runner 规格曾包含 **4 vCPU、16 GB RAM、14 GB SSD**；但这**不是本次 Runner 工作区的实测空闲空间**。实际运行中 `df` 测得取源前 **87.069 GiB**、取源后 **47.440 GiB**，开始时距 Chromium 官方 **100 GB** 最低空闲空间要求缺 **6.510 GB**。最终判定以实测为准。 | **该次探针已完成（Run #43584460871）。标准 Runner 已排除，不进行基线编译。** |
| **Larger runners** | 更大规格需要 GitHub Team / Enterprise Cloud **组织或企业** 才能配置，需付费且不能默认按公开仓免费计算。个人账号仓库当前不可直接启用此档。 | **未授权**：不建组织、不改计划或付款、不配置/启用 Larger runner。 |

调查来源：[GitHub 标准 Runner 规格](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)、[GitHub Larger runner 资格](https://docs.github.com/en/actions/concepts/runners/larger-runners)、[Chromium Android 官方最低要求](https://chromium.googlesource.com/chromium/src/+/main/docs/android_build_instructions.md)。

**执行门槛（已完成）：** 标准 Runner 的只读取证结束，监督者已独立复核；后续仅允许独立 CircleCI 探针，不允许在 GitHub 标准 Runner 上启动基线编译。G1 仍为「已写未验（待基线构建）」。不得将探针结果表述为构建或运行验证。

## 历史证据（2026-11-14）：GitHub 标准托管探针实测结论

**用户已决定：GitHub 标准托管 Runner 作为本轮基线构建候选出局；转向 CircleCI 再进行同口径探针。** 此处是标准规格实测排除，不是 GitHub 的 Larger runners 已被实测排除；后者受计划与付费限制，仍不授权启用。家用大主机与临时租云机两条线继续关闭。

证据来源： [GitHub Actions Run #43584460871](https://github.com/Zhanfg/android-titanium-browser/actions/runs/43584460871)，job `132415876065`，结论 `success`，2026-11-14 **10:31:35 UTC** 完成（北京时间 18:31:35），总 job 约 15 分 25 秒。直接取自 GitHub job log，不是文档规格或模拟值。

| 观察项 | 实测值 / 日志证据 |
|---|---|
| `nproc` | **4** 逻辑处理器 |
| RAM | **15.607 GiB**（`16758398976` 字节） |
| 源码拉取前 workspace 可用 | **87.069 GiB**（`93489852416` 字节） |
| `gclient sync` 后 workspace 可用 | **47.440 GiB**（`50937958400` 字节） |
| Chromium 源码目录占用 | `du -sh` 回报 **40G**（包含该探针工作目录） |
| 标签及源码拉取 | Chromium `157.0.8103.78`；`gclient sync -D --no-history --nohooks` 完成，`stage=sync_complete`、退出码 `0` |
| 源码尝试耗时 | 约 **14 分钟**（10:16 到 10:30 UTC） |
| 与 Chromium 100 GB 可用空间最低要求的差距 | 开始时就少 **6.510 GB**（十进制），完成同步后磁盘余量更低 |

日志中的 `.gclient_entries missing` / `.gclient file in parent directory ... might not be the file you want to use` 是同步阶段告警，**不是该次同步的失败点**。该 Run **没有 Artifacts**；取证保存在 Job 日志及 Job Summary。

**分层结论：** (1) 源码获取已证可行；(2) 标准托管在开始前即达不到 Chromium 官方 100 GB 空闲硬要求，故不再作为完整基线双架构编译候选；(3) `gclient runhooks`、`gn gen`、`autoninja`、APK/AAB、签名发布从未在探针中执行，不能凭推断声称曾发生编译失败。G0 尚未通过基线构建验收，G1 继续为「已写未验（待基线构建）」。

**历史授权（已执行并结案）：** 当时在 CircleCI 免费计划 Linux VM `xlarge` 做单次、有界的 CPU/RAM/磁盘与源码拉取探针，不编译、不超时、不配置付费和 Larger runners，结果由监督者独立读取 CircleCI API 再对账。

## 1. 依据与现有构建流程

仓库：`Zhanfg/android-titanium-browser`，`main` 分支当前的 `build.sh`、`common.sh`、`args.gn` 和 `.github/workflows/build.yml`。

1. `build.sh` 从 `vanadium/args.gn` 提取 `VERSION`，使用该版本的 Chromium Git tag，而不是由此计划文件固定任何版本；本轮查得的基线版本为 `157.0.8103.78`。
2. 安装 Linux/i386 依赖，拉取 `depot_tools`，下载 Chromium 源码并检出指定 tag。
3. 准备 Vanadium 补丁，执行 `git am`，然后 `gclient sync -D --no-history --nohooks`、`gclient runhooks`、`install-build-deps.sh`。
4. 执行 `patch.sh`，复制项目 `args.gn`，`gn gen out/Default`。GN 参数包含 `is_desktop_android = true`、`is_official_build = true`、`use_siso = true`，初始 `target_cpu = "arm"`。
5. 第一次运行 `autoninja -C out/Default chrome_public_apk`，生成 ARM32 APK；将 `target_cpu` 改为 `arm64`，再次运行 `autoninja -C out/Default chrome_public_apk chrome_public_bundle`，生成 ARM64 APK 与 AAB。
6. `build.sh` 签署 APK/AAB，工作流还包含更新 Vanadium 子模块、GitHub Release 发布与 provenance attestation。该构建入口带有仓库写操作和密钥使用环节，**不应直接拿它做未经隔离的 PR 验证**。

因此资源需求不能仅按一次单 ABI、只编译少量 Java 的项目估算。双 ABI 在同一输出目录切换 `target_cpu` 会导致部分对象失效和重新构建；缓存复用比例需实测确认。

## 2. 容量与耗时

| 资源 | Chromium 官方最低值 / 说明 | 本项目**推荐规划量级（估算）** | 需要实测的指标 |
|---|---|---|---|
| 系统 | Linux x86-64；官方 Android 构建不支持 Windows/macOS 主机 | Ubuntu x86-64 或兼容 Linux | 依赖兼容性 |
| RAM | **至少 8 GB**；**大于 16 GB** 强烈推荐 | **32–64 GB** | `MemAvailable`、swap、peak RSS、OOM |
| 可用磁盘 | **至少 100 GB 空闲** | **250–400 GB 可用 NVMe SSD**，长期留缓存可再扩大 | `du -sh chromium/src`、`out/Default`、峰值磁盘占用 |
| CPU | 官方没有给出固定最低核心数 | **16–32 逻辑线程**作为初始容量测算点 | `autoninja` 各阶段 CPU 利用率、热降频 |
| 首次源码/依赖同步 | 官方写明：快速网络也可能需要 **30 分钟**，慢网可能数小时 | **0.5–3 小时以上**，受出口、代理、缓存影响 | 下载量、网络速度、失败重试 |
| 两次 `autoninja` | 官方没有通用单次工时保证 | 高配冷构建**约 3–12 小时以上**的宽范围预估；较小机器可远超 24 小时 | ARM32、ARM64 各自 walltime、对象增量比例 |
| 签名/上传 | 官方没有 Chromium 统一时长指标 | **数分钟至数十分钟**，不含排队 | 产物大小、上传速率 |

**口径声明：** 8 GB、100 GB 与 >16 GB 来自官方构建文档；32–64 GB、250–400 GB、16–32 线程、3–12+ 小时及其他区间是工程估算，未经本仓实测。这里的磁盘指构建期间的**空闲空间**，不是磁盘总容量。估时包含显著不确定性，不能作为交付承诺。

## 3. 曾讨论的部署落点（历史对比，已由 Vultr 决策取代）

| 落点 | 能力与特点 | 风险、成本项与待核对条件 |
|---|---|---|
| **家里高配主机 + self-hosted Runner** | 可保留 Chromium 源码、增量产物、GN/Ninja/Siso 缓存；可自行选择 CPU/RAM/NVMe；长期可重复运行 | 实际硬件规格、SSD 剩余空间、供电散热、宽带稳定性、磁盘磨损、电费；Runner 工作权限及签名密钥隔离；设备必须是受支持的 Linux 构建主机 |
| **临时租高配 Linux 云机** | 独立临时环境，可按需租 vCPU/RAM/高性能磁盘并在结束后销毁，便于控制与生产环境隔离 | vCPU/内存小时单价、磁盘计费、下载速度及出口限速、数据传输费用、冷缓存重复下载、磁盘销毁及签名凭据管理 |
| **GitHub 托管 Runner** | 标准 Runner 免维护、容易触发；部分更大型号可提供更大磁盘与 RAM | 原文档将 `14 GB SSD` 引为规格，但**不能用作本次实例可用磁盘**；实测 `ubuntu-latest` 为 4 核、15.607 GiB RAM、取源前 87.069 GiB 空闲，仍不满足官方 100 GB 最低值；官方 larger runners 中 Ubuntu x64 **8 vCPU/32 GB/300 GB** 与 **16 vCPU/64 GB/600 GB** 等型号可列入比较，但须核实仓库资格、计费、额度及作业时长限制，不等同于标准免费 Runner |

不因标准 GitHub Runner 空间不足就笼统判断“全部 GitHub 托管方案不可行”；large runner 与自托管/云机仍需独立测算。

## 4. 历史测算输入清单（不代表当前路线待选）

- 候选家用主机的 CPU 型号、实际 RAM、可用 NVMe 空间、供电/散热、网络；候选云主机的地区、性能和计费方式。
- 每月预期构建次数、最大允许耗时、是否需要长期缓存与多版本并行。
- 真实 baseline 的各阶段 `time`、峰值内存、磁盘、网络流量和 APK/AAB 大小，并独立记录双 ABI。
- 安全隔离方案：PR 构建不使用正式签名密钥、不自动发布 Release、不擅自更新 Vanadium 子模块。

**最新状态（2026-11-14 22:57 CST）：Vultr 按小时租用、仓库级 self-hosted Runner 已定版；用户注册并通过支付宝充值，监督者随后负责建机/Runner。此前 Hetzner 决策废止。G0 未过，G1 PR #2 已写未验（待基线构建），G2/G3 不动。**

## 5. 来源

- 本仓构建流程： https://github.com/Zhanfg/android-titanium-browser/blob/main/build.sh
- 本仓发布流程： https://github.com/Zhanfg/android-titanium-browser/blob/main/.github/workflows/build.yml
- 本仓编译参数： https://github.com/Zhanfg/android-titanium-browser/blob/main/args.gn
- Chromium Android 官方构建要求： https://chromium.googlesource.com/chromium/src/+/main/docs/android_build_instructions.md
- GitHub 托管标准 Runner： https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- GitHub Larger Runners： https://docs.github.com/en/actions/reference/runners/larger-runners
