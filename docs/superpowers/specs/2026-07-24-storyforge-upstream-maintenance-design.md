# Storyforge 双上游维护设计

## 目标

在 GitHub 账号 `haojiayu` 下创建 `abrahamp47/storyforge-wiki` 的个人 Fork，并将 Storyforge 的小说专用能力重放到最新版 `SamurAIGPT/llm-wiki-agent` 基线之上。最终仓库应适合分析长篇小说，也应能持续接收通用上游的安全修复和引擎改进。

## 非目标

- 本阶段不分析 `/Users/haojiayu/Documents/qltx/权力的体香@sosdbot.txt`。
- 本阶段不配置或提交任何模型 API 密钥。
- 本阶段不自动合并未来的上游更新。
- 本阶段不初始化 `/Users/haojiayu/Documents/qltx` 根目录为 Git 仓库。
- 本阶段不开发新的 Wiki 前端。

## 已确认的仓库关系

- 小说上游：`https://github.com/abrahamp47/storyforge-wiki`
- 通用上游：`https://github.com/SamurAIGPT/llm-wiki-agent`
- 共同祖先：`82b80782f6b0eed5dd28196d4074174d465a6795`
- 当前 Storyforge 头提交：`e05622343ee2999cef2d547465a28a92f9c673f6`
- 当前通用上游头提交：`d499867afd933cebe3d351596f9a1c43a73e4261`
- 共同祖先之后，Storyforge 有 7 个小说化提交，通用上游有 17 个提交。
- 直接合并会在 README 和 8 个核心工具文件中产生冲突，因此不采用直接合并作为初始整合方式。

## 推荐架构

### GitHub 仓库

创建公开 Fork：

`https://github.com/haojiayu/storyforge-wiki`

分支用途：

- `main`：日常使用和维护的小说分析版本。
- `storyforge-original`：固定指向整合前的 Storyforge 头提交，作为恢复点。
- `sync/llm-wiki-agent`：定时同步任务在无冲突时使用的临时 PR 分支。

本地远端命名：

- `origin`：`haojiayu/storyforge-wiki`
- `storyforge`：`abrahamp47/storyforge-wiki`
- `llm-upstream`：`SamurAIGPT/llm-wiki-agent`

### 初始整合

1. Fork Storyforge，并在个人 Fork 中保存 `storyforge-original` 分支。
2. 以当前 `llm-upstream/main` 为新的基础提交。
3. 按原顺序重放 Storyforge 的 7 个小说化提交。
4. 冲突解决原则：
   - 保留 Storyforge 的小说领域目录、模板、长文本分块和 MapReduce 提取流程。
   - 引入通用上游的安全修复、YAML 标题解析、lint 修复和共享工具抽取。
   - 不引入与功能无关的星标图历史噪声到小说运行逻辑中；仓库级工作流可保留，但不得影响分析流程。
   - README 以小说使用路径为主，并单独说明双上游关系。
5. 将整合结果作为个人 Fork 的新 `main` 推送。

这次历史重排只发生在新创建、尚未被其他人依赖的个人 Fork 中。以后不再重写已发布的 `main` 历史，上游更新通过 PR 合并。

## 小说能力边界

整合后的版本必须继续支持：

- 人物、地点、阵营、文化、物品、力量体系、事件、章节、剧情弧和时间线页面。
- TXT、Markdown、EPUB、PDF、DOCX 等输入转换。
- 长文本分块提取与最终归并，避免将整本小说塞进单次模型请求。
- 人物状态变化、时间线事件、未解决剧情线和设定矛盾提取。
- Wiki 健康检查、内容 lint、查询和关系图构建。
- Quartz 静态发布工具。
- Codex 通过 `AGENTS.md` 使用自然语言执行 ingest、query、lint 和 graph 工作流。

## 定时上游检查

新增 GitHub Actions 工作流，每周一北京时间上午 09:00 运行，并支持手动触发。

工作流只检查 `SamurAIGPT/llm-wiki-agent/main`：

1. 检出个人 Fork 的 `main`。
2. 获取通用上游最新提交。
3. 如果记录的上游 SHA 未变化，正常结束，不创建 PR 或 Issue。
4. 如果有新提交，在临时分支尝试合并。
5. 无冲突时：
   - 运行无模型验证。
   - 在同步分支的 `UPSTREAMS.md` 中把“最近成功整合 SHA”更新为本次上游 SHA；该值只有在 PR 被人工合并后才进入 `main`。
   - 推送或更新 `sync/llm-wiki-agent`。
   - 创建或更新标题固定的同步 PR。
6. 有冲突时：
   - 中止合并，不修改 `main`。
   - 创建或更新一个固定标题的 Issue。
   - Issue 正文列出旧 SHA、新 SHA 和冲突文件。
7. 工作流永远不自动合并 PR。

原 Storyforge 上游仍通过 GitHub 标准 Fork 关系跟踪。其后续小说功能更新由维护者在 GitHub 的 Fork 同步提示中查看，并按需单独合并，避免两个上游同时改写同一批核心文件。

## 同步状态记录

仓库根目录新增 `UPSTREAMS.md`，记录：

- 两个上游仓库地址和职责。
- 初始共同祖先。
- 最近成功整合的通用上游 SHA。
- 最近检查时间。
- 手动检查、创建同步分支和解决冲突的命令。
- 冲突解决优先级。

GitHub Action 只有在同步 PR 被人工合并后，才允许更新“最近成功整合 SHA”。失败或冲突不能推进同步状态。

## 安全与权限

- GitHub Actions 只使用仓库自动提供的 `GITHUB_TOKEN`。
- 工作流权限限定为 `contents: write`、`pull-requests: write` 和 `issues: write`。
- 不在工作流、仓库文件、日志或提交中保存模型密钥。
- 定时检查仅拉取公开上游代码，不运行模型分析，也不上传小说原文。
- `raw/` 和生成的 `wiki/` 内容继续按 Storyforge 的忽略规则留在本地，除非维护者明确选择发布。

## 本地布局

个人 Fork 克隆到：

`/Users/haojiayu/Documents/qltx/storyforge`

现有小说文件保持在：

`/Users/haojiayu/Documents/qltx/权力的体香@sosdbot.txt`

首次搭建只建立空环境，不将小说复制到 `raw/`。

## 验证标准

初始整合和每次无冲突同步 PR 必须至少通过：

1. `python -m compileall -q tools`
2. `python tools/health.py`
3. `python tools/ingest.py --validate-only`
4. 检查 Wiki 模板目录完整存在。
5. 检查 `AGENTS.md` 包含小说 ingest、query、lint 和 graph 工作流。
6. 检查长文本分块函数及 MapReduce 提取路径仍存在。
7. 检查 GitHub Actions 工作流 YAML 能被解析。

由于这些验证不调用模型，定时检查不会产生模型费用。真正的小说分析质量验证留到后续导入样章时进行。

## 失败处理与恢复

- 初始重放失败：丢弃本地重放分支，从 `storyforge-original` 和记录的通用上游 SHA重新开始；不改写远端恢复分支。
- 定时同步冲突：保持 `main` 不变，通过 Issue 通知人工处理。
- 同步 PR 验证失败：保留 PR 供检查，不合并、不更新成功同步 SHA。
- 错误合并：从 `storyforge-original`、已合并 PR 和 Git 历史定位恢复点，使用新的修复提交恢复，不对已发布的 `main` 强制回退。

## 完成条件

- `haojiayu/storyforge-wiki` Fork 存在。
- `storyforge-original` 和整合后的 `main` 均已推送。
- `main` 同时包含当前通用上游修复和 Storyforge 小说能力。
- 双上游及维护流程记录完整。
- 每周自动检查工作流已启用，且支持手动运行。
- 本地 `storyforge/` 克隆配置了三个远端。
- 所有无模型验证通过。
- 现有小说文件未被移动、修改、提交或分析。
