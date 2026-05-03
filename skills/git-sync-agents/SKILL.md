---
name: git-sync-agents
description: 维护 ~/.agents 与远程 GitHub 仓库的双向同步
---

## 默认配置

- 远程仓库: 从 `~/.agents/.env` 中的 `GITHUB_AGENT_REPOSITORY_URL` 读取，默认 `https://github.com/Slarper/agents.git`
- 本地路径: `~/.agents`

## 变量获取

按以下优先级读取配置：

1. 读取 `~/.agents/.env` 中的 `GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN` 和 `GITHUB_AGENT_REPOSITORY_URL`
2. 对应的环境变量 `GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN` 和 `GITHUB_AGENT_REPOSITORY_URL`

将读取到的值赋给 `$TOKEN` 和 `$REPO_URL` 变量。

## 行为

当用户调用时，默认执行完整同步流程：先提交本地改动，再拉取远程，最后推送，完成双向同步。

### Step 0: 获取变量

```bash
if [ -f ~/.agents/.env ]; then
  source ~/.agents/.env
fi
TOKEN="${GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN}"
REPO_URL="${GITHUB_AGENT_REPOSITORY_URL:-https://github.com/Slarper/agents.git}"
```

若 `$TOKEN` 为空，则向用户询问 PAT。若 `$REPO_URL` 为空，则使用默认值 `https://github.com/Slarper/agents.git`。

### Step 1: 确保 ~/.agents 是合法的 git 仓库

如果 `~/.agents/.git` 不存在，执行 init：

```bash
cd ~/.agents
git init
git branch -m main
git config user.email "naivesimple@outlook.com"
git config user.name "Slarper"
REPO_URL_WITH_TOKEN="${REPO_URL/https:\/\//https:\/\/${TOKEN}@}"
git remote add origin "$REPO_URL_WITH_TOKEN"
```

如果 `.git` 存在但 remote 未配置（`git remote get-url origin` 失败），则添加 remote：

```bash
REPO_URL_WITH_TOKEN="${REPO_URL/https:\/\//https:\/\/${TOKEN}@}"
git remote add origin "$REPO_URL_WITH_TOKEN"
```

### Step 2: 暂存并提交本地变更

```bash
git add -A
```

如果有变更，自动提交，提交信息描述变更内容（如 "Update skill: xxx" 或 "Add new skill: xxx"）。

### Step 3: 拉取远程内容

先 fetch 远程信息：

```bash
git fetch origin main
```

判断远程是否有内容以及本地与远程是否有关联历史：

```bash
if ! git rev-parse origin/main >/dev/null 2>&1; then
  echo "Remote empty, skip pull"
elif git rev-parse HEAD >/dev/null 2>&1 && git merge-base HEAD origin/main >/dev/null 2>&1; then
  git pull origin main
else
  git pull origin main --allow-unrelated-histories
fi
```

如果 pull 产生冲突，逐一向用户提供选项：
  - **保留远程版本** → `git checkout --theirs <path>` 后 `git add <path>`
  - **保留本地版本** → `git checkout --ours <path>` 后 `git add <path>`
  冲突全部解决后 `git commit -m "Merge remote into local"`。

### Step 4: 暂存并提交 pull 引入的合并变更

```bash
git add -A
```

如果有变更，自动提交（如 "Merge remote changes"）。

### Step 5: 推送到远程

```bash
git push origin main
```

### Step 6: 反馈结果

告知用户同步结果：新增/修改了哪些文件，推送是否成功。

## 特殊情况：存在未提交的本地改动

如果 Step 2 执行前发现工作区有未跟踪或未暂存的改动干扰了拉取，则回退到 stash 方式：

```bash
git stash push -u -m "git-sync-auto-stash"
```

然后执行 Step 3 拉取。拉取完成后恢复 stash：

```bash
git stash pop
```

如果 pop 产生冲突，逐一向用户提供选项：
- **保留 stash 版本** → `git checkout --theirs <path>` 后 `git add <path>`
- **放弃 stash 版本** → `git checkout --ours <path>` 后 `git add <path>`
  冲突全部解决后 `git stash drop`。

之后回到 Step 4 继续。

## 安全注意事项

1. 通过 `.env` 或环境变量读取 PAT 和仓库 URL，嵌入 remote URL 使用
2. PAT 不会被提交到仓库（`.env` 已加入 `.gitignore`）
3. 建议使用 fine-grained token，授予 agents 仓库 Contents: Write 权限
