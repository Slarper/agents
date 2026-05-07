---
name: git-mastery
description: 为任意本地目录配置 git 远程仓库（含 PAT 鉴权），提供 init / push / pull 等粒度可控的操作工具
---

## 配置读取

执行任何操作前，先读取凭证：

```bash
if [ -f ./.env ]; then
  source ./.env
elif [ -f .env.example ]; then
  echo "⚠️  ./.env 不存在。我已读取 .env.example 模板，请对照创建："
  cat .env.example
  echo ""
  echo "创建方式：cp .env.example .env 并填入真实凭证"
  # 询问用户是否希望 AI 协助创建 .env
  # 若用户同意，逐项询问 TOKEN / EMAIL / NAME 的值并写入 .env
fi
TOKEN="${GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN:-$GITHUB_TOKEN}"
GIT_EMAIL="${GIT_USER_EMAIL}"
GIT_NAME="${GIT_USER_NAME}"
```

若 `$TOKEN` 为空，向用户询问 PAT（提示：需要 GitHub fine-grained token，赋予目标仓库 Contents: Write 权限）。
若 `$GIT_EMAIL` 或 `$GIT_NAME` 为空，向用户询问 git 用户名和邮箱。

### PAT 远程 URL 嵌入（push/pull 前使用）

在执行 push/pull 前，先将 PAT 嵌入 remote URL 进行认证，操作完成后立即恢复：

```bash
ORIGINAL_REMOTE_URL=$(git remote get-url origin)
REPO_URL_WITH_TOKEN="${ORIGINAL_REMOTE_URL/https:\/\//https:\/\/${TOKEN}@}"
git remote set-url origin "$REPO_URL_WITH_TOKEN"
# ... 执行 push/pull 操作 ...
# 操作完成后恢复原始 URL
git remote set-url origin "$ORIGINAL_REMOTE_URL"
```

## 提供的操作工具

以下每个操作都是独立原子步骤，按需调用，不做隐式组合。

### tool: git init

在指定目录初始化仓库并配置 remote（不嵌入 PAT，后续 push/pull 会自动临时嵌入）。

先向用户询问远程仓库 URL，得到后执行：

```bash
cd <target-dir>
git init
git branch -m main
git config user.email "$GIT_EMAIL"
git config user.name "$GIT_NAME"
git remote add origin "$REPO_URL"
```

如果 `.git` 已存在但 remote 未配置：

```bash
git remote add origin "$REPO_URL"
```

如果 `.git` 存在且 remote 已配置，则跳过 init，告知用户。

**注意**：操作前向用户确认目标目录是否正确。

### tool: git push remote

**重要：commit message 不得询问用户，必须由 AI 通过分析 `git diff --staged` 自动生成。**

```bash
cd <target-dir>
# 嵌入 PAT 到 remote URL
ORIGINAL_REMOTE_URL=$(git remote get-url origin)
REPO_URL_WITH_TOKEN="${ORIGINAL_REMOTE_URL/https:\/\//https:\/\/${TOKEN}@}"
git remote set-url origin "$REPO_URL_WITH_TOKEN"
# 暂存所有变更
git add -A
# 如有变更则提交
git commit -m "<AI 根据 git diff --staged 自动生成的提交信息>"
# 推送到远程（若首次推送自动创建分支）
git push -u origin main
# 恢复原始 URL
git remote set-url origin "$ORIGINAL_REMOTE_URL"
```

推送完成后告知用户推送结果。

### tool: git pull remote (override local)

以远程为准覆盖本地，适合"远程是最新权威，本地可丢弃"的场景：

```bash
cd <target-dir>
# 嵌入 PAT 到 remote URL
ORIGINAL_REMOTE_URL=$(git remote get-url origin)
REPO_URL_WITH_TOKEN="${ORIGINAL_REMOTE_URL/https:\/\//https:\/\/${TOKEN}@}"
git remote set-url origin "$REPO_URL_WITH_TOKEN"
# 拉取远程最新
git fetch origin main
# 重置本地到远程版本（丢弃所有本地未推送的改动）
git reset --hard origin/main
# 恢复原始 URL
git remote set-url origin "$ORIGINAL_REMOTE_URL"
```

**安全提示**：

- 此操作会丢弃所有本地未推送的提交和未暂存的修改
- 执行前应明确告知用户此风险，获得确认后再执行

### tool: git pull remote (merge, keep local)

保留本地提交并与远程合并：

```bash
cd <target-dir>
# 嵌入 PAT 到 remote URL
ORIGINAL_REMOTE_URL=$(git remote get-url origin)
REPO_URL_WITH_TOKEN="${ORIGINAL_REMOTE_URL/https:\/\//https:\/\/${TOKEN}@}"
git remote set-url origin "$REPO_URL_WITH_TOKEN"
# 拉取并合并
git fetch origin main
git pull origin main
# 恢复原始 URL
git remote set-url origin "$ORIGINAL_REMOTE_URL"
```

如果 pull 产生冲突，逐一向用户提供选项：

- **保留远程版本** → `git checkout --theirs <path>` 后 `git add <path>`
- **保留本地版本** → `git checkout --ours <path>` 后 `git add <path>`
  冲突全部解决后 `git commit -m "Merge remote into local"`

### tool: git status check

查看当前仓库状态：

```bash
cd <target-dir>
git status
git log --oneline -5
```

## 安全注意事项

1. PAT 只在 remote URL 中临时使用（push/pull 前嵌入，操作后立即恢复），不会写入任何文件
2. `.env` 应已加入 `.gitignore`
3. 每次执行前先确认目标目录，避免操作错误的仓库
4. `git reset --hard` 等破坏性操作必须先向用户说明风险并获取确认
5. 不在一个步骤里组合多个操作（如不要同时提交+拉取+推送），保持粒度可控
