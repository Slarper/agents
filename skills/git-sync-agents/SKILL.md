---
name: git-sync-agents
description: 维护 ~/.agents 与远程 GitHub 仓库的双向同步
---

## 默认配置

- 远程仓库: `https://github.com/Slarper/agents.git`
- 本地路径: `~/.agents`

## 行为

当用户调用时，先判断 `~/.agents` 是否已是 git 仓库，然后分两种情况处理。

### 情况 A: 尚未初始化（`~/.agents/.git` 不存在）

初始化 git：

```bash
cd ~/.agents
git init
git branch -m main
git config user.email "naivesimple@outlook.com"
git config user.name "Slarper"
git remote add origin https://<token>@github.com/Slarper/agents.git
```

首次拉取远程内容并与本地合并（处理本地已有 skills/ 目录的情况）：

```bash
git pull origin main --allow-unrelated-histories
```

如果拉取过程中产生冲突，逐一向用户提供选项：
- **保留远程版本** → 执行 `git checkout --theirs <path>` 后 `git add <path>`
- **保留本地版本** → 执行 `git checkout --ours <path>` 后 `git add <path>`

冲突全部解决后完成合并：

```bash
git commit -m "Merge remote into local init"
```

### 情况 B: 已是本地仓库且跟踪远程

```bash
cd ~/.agents
git pull origin main
```

如果 `pull` 产生冲突，按相同方式逐一向用户提供选项解决。

### 后续步骤（两种情况共用）

暂存所有变更并提交：

```bash
git add -A
```

如果有变更，自动提交，提交信息描述变更内容（如 "Update skill: xxx" 或 "Add new skill: xxx"）。

推送到远程：

```bash
git push origin main
```

### 反馈结果

告知用户同步结果：新增/修改了哪些文件，推送是否成功。

## 安全注意事项

1. 用户需提供 Personal Access Token，嵌入 remote URL 使用
2. PAT 不会被提交到仓库
3. 建议使用 fine-grained token，授予 agents 仓库 Contents: Write 权限
