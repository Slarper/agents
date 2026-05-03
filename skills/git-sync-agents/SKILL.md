---
name: git-sync-agents
description: 维护 ~/.agents 与远程 GitHub 仓库的双向同步
---

## 默认配置

- 远程仓库: `https://github.com/Slarper/agents.git`
- 本地路径: `~/.agents`

## 行为

当用户调用时，执行以下步骤。

### Step 1: 确保 ~/.agents 是合法的 git 仓库

如果 `~/.agents/.git` 不存在，执行 init：

```bash
cd ~/.agents
git init
git branch -m main
git config user.email "naivesimple@outlook.com"
git config user.name "Slarper"
git remote add origin https://<token>@github.com/Slarper/agents.git
```

如果 `.git` 存在但 remote 未配置（`git remote get-url origin` 失败），则添加 remote：

```bash
git remote add origin https://<token>@github.com/Slarper/agents.git
```

### Step 2: 处理未暂存的本地改动

如果 `git status --porcelain` 有输出，先 stash（包括未跟踪文件）：

```bash
git stash push -u -m "git-sync-auto-stash"
```

### Step 3: 拉取远程内容

先 fetch 远程信息：

```bash
git fetch origin main
```

判断远程是否有内容以及本地与远程是否有关联历史：

```bash
if ! git rev-parse origin/main >/dev/null 2>&1; then
  # 远程空仓库 — 跳过 pull
  echo "Remote empty, skip pull"
elif git rev-parse HEAD >/dev/null 2>&1 && git merge-base HEAD origin/main >/dev/null 2>&1; then
  # 有关联历史 — 正常 pull
  git pull origin main
else
  # 无关联历史（首次 init 后 pull，或因机器 B 首次同步） — 允许无关联
  git pull origin main --allow-unrelated-histories
fi
```

如果 pull 产生冲突，逐一向用户提供选项：
  - **保留远程版本** → `git checkout --theirs <path>` 后 `git add <path>`
  - **保留本地版本** → `git checkout --ours <path>` 后 `git add <path>`
  冲突全部解决后 `git commit -m "Merge remote into local"`。

如果 Step 2 执行了 stash，恢复：

```bash
git stash pop
```

如果 pop 产生冲突（stash 中的改动与远程拉取后的内容冲突），逐一向用户提供选项：
- **保留 stash 版本** → `git checkout --theirs <path>` 后 `git add <path>`
- **放弃 stash 版本** → `git checkout --ours <path>` 后 `git add <path>`
  冲突全部解决后 `git stash drop`。

### Step 4: 暂存并提交本地变更

```bash
git add -A
```

如果有变更，自动提交，提交信息描述变更内容（如 "Update skill: xxx" 或 "Add new skill: xxx"）。

### Step 5: 推送到远程

```bash
git push origin main
```

### Step 6: 反馈结果

告知用户同步结果：新增/修改了哪些文件，推送是否成功。

## 安全注意事项

1. 用户需提供 Personal Access Token，嵌入 remote URL 使用
2. PAT 不会被提交到仓库
3. 建议使用 fine-grained token，授予 agents 仓库 Contents: Write 权限
