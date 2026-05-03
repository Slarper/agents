---
name: git-commit-skills
description: 维护 ~/.agents 与远程 GitHub 仓库的双向同步
---

## 默认配置

- 远程仓库: `https://github.com/Slarper/agents.git`
- 本地路径: `~/.agents`

## 行为

当用户调用时，执行以下步骤：

### Step 1: 确保 ~/.agents 是 git 仓库

如果 `~/.agents/.git` 不存在，自动初始化：

```bash
cd ~/.agents
git init
git branch -m main
git config user.email "naivesimple@outlook.com"
git config user.name "Slarper"
git remote add origin https://<token>@github.com/Slarper/agents.git
```

### Step 2: 拉取远程最新内容

```bash
git pull origin main --rebase
```

处理冲突：如果存在冲突，告知用户手动解决。

### Step 3: 暂存并提交本地变更

```bash
git add -A
```

如果有变更，自动提交（提交信息描述变更内容，如 "Update skill: xxx" 或 "Add new skill: xxx"）。

### Step 4: 推送到远程

```bash
git push origin main
```

### Step 5: 反馈结果

告知用户同步结果：新增/修改了哪些文件，推送是否成功。

## 安全注意事项

1. 用户需提供 Personal Access Token，嵌入 remote URL 使用
2. PAT 不会被提交到仓库
3. 建议使用 fine-grained token，授予 agents 仓库 Contents: Write 权限