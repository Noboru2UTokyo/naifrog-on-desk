# 奶蛙 on Desk · Naifrog on Desk

**由 [Noboru2UTokyo](https://github.com/Noboru2UTokyo) 发起、主导设计并维护的奶蛙版 Clawd。**

一只会跟随 AI 编码状态思考、打字、施工和大笑的桌面奶蛙。应用内置完整主题与音效，安装后即可使用，不需要配置视频生成 API。

<p align="center"><img src="themes/naifrog/assets/idle.webp" alt="奶蛙惊鸿一瞥待机" width="280"></p>

**当前版本：1.4.1 · macOS Apple Silicon** ｜ [下载安装](https://github.com/Noboru2UTokyo/naifrog-on-desk/releases/latest) ｜ [版本说明](docs/releases/release-v1.4.1.md)

## 谁做了什么

**Noboru2UTokyo — 奶蛙版发起、设计主导与维护。** 负责产品方向和原始素材选用，确定奶蛙的形象、比例与配色规范；主导动作、循环、抠图与过渡的迭代，工作状态映射与黄绿界面设计，以及效果验收、应用整合、打包发行和后续维护。代码实现和适配素材制作使用了 AI 辅助。

**rullerzhou-afk（Ruller_Lulu / 鹿鹿）及上游贡献者 — 原版 Clawd on Desk。** 本版基于 [Clawd on Desk v1.3.0](https://github.com/rullerzhou-afk/clawd-on-desk/tree/v1.3.0)，继承桌宠运行框架、AI 工具集成、权限气泡、会话管理与设置系统。完整上游介绍和贡献者名单保留在 [README.upstream.md](README.upstream.md)。

奶蛙原角色和原始素材的权利归各自权利人所有；本版署名对应主题适配、创意指导和发行维护。详细归属见 [NOTICE.md](NOTICE.md)，应用代码遵循 [AGPL-3.0-only](LICENSE)。

## 安装与分享

1. 在 [最新 Release](https://github.com/Noboru2UTokyo/naifrog-on-desk/releases/latest) 下载 `Naifrog-on-Desk-1.4.1-arm64.dmg`。
2. 退出正在运行的 Naifrog 或 Clawd，打开 DMG，将 **Naifrog on Desk.app** 拖入 **Applications**。
3. 从 Applications 启动。新安装默认显示奶蛙，升级保留已有主题与设置。
4. 需要联动编码工具时，在 **Settings → Agents** 检查相应集成。部分工具需要本机 Node.js 及宿主自己的 hook 审核，详见[集成安装指南](docs/guides/setup-guide.md)。

同事只需要下载安装包；不需要 Alaya、MiniMax 或 OpenAI API Key。可以直接分享本仓库的 [最新版本链接](https://github.com/Noboru2UTokyo/naifrog-on-desk/releases/latest)。

| 文件 | 用途 |
| --- | --- |
| `Naifrog-on-Desk-1.4.1-arm64.dmg` | 推荐安装方式，适用于 Apple Silicon Mac |
| `Naifrog-on-Desk-1.4.1-arm64.zip` | 同一应用的 ZIP 分发包 |
| `Naifrog-1.4.1.zip` | 独立主题；供原版 Clawd 在设置中导入 |
| `SHA256SUMS.txt` / `verification.json` | 文件校验值与本次验证记录 |

当前包使用 **ad-hoc 签名，未做 Apple 公证**。首次启动如被 macOS 拦截，请核对来源与校验值，再根据系统「隐私与安全性」提示决定是否打开。Intel Mac、Windows 和 Linux 尚无本版验收过的安装包。

## 动作与触发

| 状态 | 奶蛙动作 |
| --- | --- |
| 待机 | 原片「惊鸿一瞥」：正放 1 秒、停留 2 秒、倒放 1 秒、正常姿势休息 2 秒 |
| 提交提示词 / 思考 | 托腮、抱臂 |
| 1 个工作会话 | 打字循环 |
| 2 个工作会话 | 戴耳机循环 |
| 3 个及以上工作会话 | 施工循环 |
| 子代理工作 | 戴耳机循环 |
| 完成 / 点击反应 | 原片大笑 12 秒 |
| 睡眠 | 连续趴下、趴睡呼吸、撑起醒来 |
| 空闲小动作 | 吹泡泡 |
| 权限请求 | 权限气泡与原短确认笑声 |

工作动作持续到状态变化，不按固定时间轮换。保留原大笑变体音效。没有三球接抛或爬行动作，新安装默认关闭自由漫游。具体触发能力取决于所用工具支持的事件，详见[状态映射](docs/guides/state-mapping.md)。

## 更新与共存

从 [Releases](https://github.com/Noboru2UTokyo/naifrog-on-desk/releases) 手动下载新版并替换应用即可。应用更新源指向本仓库；跨版本自动更新安装尚未验收。

奶蛙版拥有独立应用名称、bundle ID 与偏好目录，不会替换 `Clawd on Desk.app`。两版仍共享 agent hooks 与 `~/.clawd`，**请只运行其中一个版本**。此版不会接管原版 `clawd://` 链接，主题可从设置导入。

设置中仍可切换 Clawd、Calico、Cloudling 或导入其他主题。升级不会强行覆盖已保存的主题选择。

## 开发与维护

```sh
npm ci
npm test
npm run verify:release
npm run build:mac:arm64 -- --publish never
```

发行分支为 `codex/naifrog-edition`，`main` 保留上游同步线。维护流程与验证要求见 [NAIFROG.md](NAIFROG.md)。本次发布沿用已验收动画和声音，版本验收范围及未验证项随 Release 的 `verification.json` 一同提供。
