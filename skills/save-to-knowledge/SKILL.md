---
name: save-to-knowledge
description: Save a .md file to a configured knowledge directory and sync to remote git repo
---

## 环境变量

在 `~/.agents/.env` 中配置（或通过同名环境变量覆盖）：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `KNOWLEDGE_DIR` | 本地知识库目录 | `~/Markdown/knowledge/` |
| `KNOWLEDGE_REPOSITORY_URL` | 远程 git 仓库地址 | 空（不推送） |
| `KNOWLEDGE_GITHUB_TOKEN` | GitHub fine-grained PAT | 同 `GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN` |

## 行为

用户给出文件名和内容后，执行以下流程：

### Step 1: 读取变量

```bash
if [ -f ~/.agents/.env ]; then
  source ~/.agents/.env
fi
KNOW_DIR="${KNOWLEDGE_DIR:-$HOME/Markdown/knowledge/}"
REPO_URL="${KNOWLEDGE_REPOSITORY_URL}"
TOKEN="${KNOWLEDGE_GITHUB_TOKEN:-${GITHUB_FINE_GRAINED_PERSONAL_ACCESS_TOKEN}}"
```

### Step 2: 确认文件名与内容

- **文件名**：用户提供（不含 `.md` 则自动补充）。含 `/` 则自动创建子目录。例如 `opencode/foo` → `$KNOW_DIR/opencode/foo.md`
- **内容**：用户提供 markdown 内容，直接写入文件
- **约束**：一次只保存一个 `.md` 文件

### Step 3: 写入文件

```bash
mkdir -p "$(dirname "$KNOW_DIR/$filename")"
cat > "$KNOW_DIR/$filename" << 'EOF'
<content>
EOF
```

告知用户文件已保存到 `$KNOW_DIR/$filename`。

### Step 4: Git 同步

仅在 `REPO_URL` 非空时执行。逻辑参考 `skills/git-sync-agents/SKILL.md`，但操作目录为 `$KNOW_DIR`：

#### 4a: 确保是 git 仓库

```bash
if [ ! -d "$KNOW_DIR/.git" ]; then
  git -C "$KNOW_DIR" init
  git -C "$KNOW_DIR" branch -m main
  git -C "$KNOW_DIR" config user.email "naivesimple@outlook.com"
  git -C "$KNOW_DIR" config user.name "Slarper"
  REPO_URL_WITH_TOKEN="${REPO_URL/https:\/\//https:\/\/${TOKEN}@}"
  git -C "$KNOW_DIR" remote add origin "$REPO_URL_WITH_TOKEN"
fi
```

若 remote 未配置，同 logic 添加。

#### 4b: 暂存并提交

```bash
git -C "$KNOW_DIR" add -A
```

有变更则提交，消息如 `Add knowledge: <filename>`。

#### 4c: 拉取远程

```bash
git -C "$KNOW_DIR" fetch origin main
if ! git -C "$KNOW_DIR" rev-parse origin/main >/dev/null 2>&1; then
  echo "Remote empty, skip pull"
elif git -C "$KNOW_DIR" rev-parse HEAD >/dev/null 2>&1 && git -C "$KNOW_DIR" merge-base HEAD origin/main >/dev/null 2>&1; then
  git -C "$KNOW_DIR" pull origin main
else
  git -C "$KNOW_DIR" pull origin main --allow-unrelated-histories
fi
```

#### 4d: 推送

```bash
git -C "$KNOW_DIR" push origin main
```

### Step 5: 反馈结果

告知用户：
- 文件保存路径
- git 同步结果（推送成功 / 失败 / 未配置远程）

## 安全注意事项

1. PAT 只通过 `.env` 或环境变量读取，嵌入 remote URL 使用
2. `.env` 不会被提交（已在 `~/.agents/.gitignore` 中）
3. `KNOWLEDGE_DIR` 需独立配置 `.gitignore`（如果不想提交某些文件）
