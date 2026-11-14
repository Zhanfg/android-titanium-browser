# G0：Chromium 基线构建 Runner 资源测算（Plan only）

> 2026-11-14 计划稿。只供方案比较，不作 Runner 选型，不实施或修改构建代码。以下推荐量级与工时均为粗估，不代表任何一次实测。

## Decision record：2026-11-14 用户决定

**2026-11-14 早期决策记录：先选择 GitHub 托管 Runner 进行取证（标准档现已在后续探针中排除）。** 家用高配主机自托管和临时租高配云机两条路线关闭，不再准备。下文第三节原有三种落点对比保留为历史估算，不再代表待选方案。

GitHub 托管分两档，授权与资源边界不得混淆：

| 档位 | GitHub 官方规格与资格 | 当前授权 |
|---|---|---|
| **标准托管 Runner（`ubuntu-latest`，公开仓库）** | 最初列出的标准 runner 规格曾包含 **4 vCPU、16 GB RAM、14 GB SSD**；但这**不是本次 Runner 工作区的实测空闲空间**。实际运行中 `df` 测得取源前 **87.069 GiB**、取源后 **47.440 GiB**，开始时距 Chromium 官方 **100 GB** 最低空闲空间要求缺 **6.510 GB**。最终判定以实测为准。 | **该次探针已完成（Run #43584460871）。标准 Runner 已排除，不进行基线编译。** |
| **Larger runners** | 更大规格需要 GitHub Team / Enterprise Cloud **组织或企业** 才能配置，需付费且不能默认按公开仓免费计算。个人账号仓库当前不可直接启用此档。 | **未授权**：不建组织、不改计划或付款、不配置/启用 Larger runner。 |

调查来源：[GitHub 标准 Runner 规格](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)、[GitHub Larger runner 资格](https://docs.github.com/en/actions/concepts/runners/larger-runners)、[Chromium Android 官方最低要求](https://chromium.googlesource.com/chromium/src/+/main/docs/android_build_instructions.md)。

**执行门槛（已完成）：** 标准 Runner 的只读取证结束，监督者已独立复核；后续仅允许独立 CircleCI 探针，不允许在 GitHub 标准 Runner 上启动基线编译。G1 仍为「已写未验（待基线构建）」。不得将探针结果表述为构建或运行验证。

## Decision record：2026-11-14 GitHub 标准托管探针实测结论

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

**本轮授权的后续工作：** 在 CircleCI 免费计划 Linux VM `xlarge` 做单次、有界的 CPU/RAM/磁盘与源码拉取探针，不编译、不超时、不配置付费和 Larger runners，结果由监督者独立读取 CircleCI API 再对账。

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

## 3. 三种部署落点对比（历史资料，现已选定托管）

| 落点 | 能力与特点 | 风险、成本项与待核对条件 |
|---|---|---|
| **家里高配主机 + self-hosted Runner** | 可保留 Chromium 源码、增量产物、GN/Ninja/Siso 缓存；可自行选择 CPU/RAM/NVMe；长期可重复运行 | 实际硬件规格、SSD 剩余空间、供电散热、宽带稳定性、磁盘磨损、电费；Runner 工作权限及签名密钥隔离；设备必须是受支持的 Linux 构建主机 |
| **临时租高配 Linux 云机** | 独立临时环境，可按需租 vCPU/RAM/高性能磁盘并在结束后销毁，便于控制与生产环境隔离 | vCPU/内存小时单价、磁盘计费、下载速度及出口限速、数据传输费用、冷缓存重复下载、磁盘销毁及签名凭据管理 |
| **GitHub 托管 Runner** | 标准 Runner 免维护、容易触发；部分更大型号可提供更大磁盘与 RAM | 原文档将 `14 GB SSD` 引为规格，但**不能用作本次实例可用磁盘**；实测 `ubuntu-latest` 为 4 核、15.607 GiB RAM、取源前 87.069 GiB 空闲，仍不满足官方 100 GB 最低值；官方 larger runners 中 Ubuntu x64 **8 vCPU/32 GB/300 GB** 与 **16 vCPU/64 GB/600 GB** 等型号可列入比较，但须核实仓库资格、计费、额度及作业时长限制，不等同于标准免费 Runner |

不因标准 GitHub Runner 空间不足就笼统判断“全部 GitHub 托管方案不可行”；large runner 与自托管/云机仍需独立测算。

## 4. 后续做决策前需要的输入（仅记录，不执行）

- 候选家用主机的 CPU 型号、实际 RAM、可用 NVMe 空间、供电/散热、网络；候选云主机的地区、性能和计费方式。
- 每月预期构建次数、最大允许耗时、是否需要长期缓存与多版本并行。
- 真实 baseline 的各阶段 `time`、峰值内存、磁盘、网络流量和 APK/AAB 大小，并独立记录双 ABI。
- 安全隔离方案：PR 构建不使用正式签名密钥、不自动发布 Release、不擅自更新 Vanadium 子模块。

**计划状态：仅文档。GitHub 标准托管探针完成且已排除该构建候选，下一项仅为 CircleCI 的有界源码探针；Larger runners/付费不授权，未执行任何 Chromium 构建。G1 尚未验收，G2/G3 不受本计划更改。**

## 5. 来源

- 本仓构建流程： https://github.com/Zhanfg/android-titanium-browser/blob/main/build.sh
- 本仓发布流程： https://github.com/Zhanfg/android-titanium-browser/blob/main/.github/workflows/build.yml
- 本仓编译参数： https://github.com/Zhanfg/android-titanium-browser/blob/main/args.gn
- Chromium Android 官方构建要求： https://chromium.googlesource.com/chromium/src/+/main/docs/android_build_instructions.md
- GitHub 托管标准 Runner： https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- GitHub Larger Runners： https://docs.github.com/en/actions/reference/runners/larger-runners
