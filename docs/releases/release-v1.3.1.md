# 奶蛙 on Desk 1.3.1

首个内置奶蛙的 Clawd on Desk 分支版本，基于上游 v1.3.0，首次启动默认显示奶蛙。

- 内置主题 1.3.1：原片惊鸿一瞥待机、托腮思考、六种办公动作、爬行、睡眠及 12 秒大笑。
- 保留 Permission 确认笑声，运行无需生成 API。
- 独立应用名称、bundle ID、偏好目录和本 fork 更新地址。不会接管原版 clawd://。
- 更新三项生产依赖的兼容补丁版本，修复依赖审计发现。
- 已有主题选择保留；内置上游主题仍可切换。

## 安装

Apple Silicon Mac 下载 `Naifrog-on-Desk-1.3.1-arm64.dmg`，拖入 Applications 后打开。也提供 ZIP 和 SHA256SUMS.txt。

本版仅使用 ad-hoc 签名，**未做 Apple 公证**。首次打开可能需要在 macOS「隐私与安全性」中由用户确认。没有验证自动更新安装；后续从本仓库 Releases 手动更新。其他平台和架构尚未验收。

请只运行原版或奶蛙版中的一个：agent hooks 和 ~/.clawd 仍沿用上游共享机制。安装包包含 Node/Electron 运行时，但部分外部 coding agent 集成仍按上游要求使用本机 Node.js 和 hook 审核。

验证详情随 Release 的 verification.json 提供；GUI、跨版本自动更新、其他平台和完整外部 agent 矩阵不自动视为已验证。

基于 rullerzhou-afk 与所有上游贡献者的工作；本分支维护者 @Noboru2UTokyo。源代码与修改在本仓库公开，保留 AGPL-3.0-only 和上游归属说明。
