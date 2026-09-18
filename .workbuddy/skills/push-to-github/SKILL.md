---
name: push-to-github
description: 把本地项目、目录或新建的项目级 Skill 打包、提交并推送到指定的 GitHub 仓库，并在推送后做三源交叉校验（git ls-remote / 本地 HEAD / GitHub API 文件树逐 blob 比对哈希），确认"远程真的和本地一致"。含 Windows + 沙箱环境实测踩坑解法：curl 无法写文件、CRYPT_E_REVOCATION_OFFLINE 证书吊销报错（git 用 http.sslBackend openssl、curl 用 --ssl-no-revoke）、本地远程跟踪引用过期导致误判"推送丢了"、GUI 无法启动、raw.githubusercontent.com 偶发 RemoteDisconnected、打印仓库配置时 PAT 被明文带出。当用户说"把这个推到 GitHub""提交并推送""更新仓库""把新 skill 交到 skill 仓库""确认远程有没有推上去"时使用。
agent_created: true
---

# 推送至 GitHub 仓库 Skill (push-to-github)

## 一、适用场景

这个 Skill 解决的是**"本地改完了，但不确定远程到底长什么样"**这个问题。

**触发**（满足任一）：

- 用户要求把某个本地目录 / 项目 / Skill 提交并推送到一个**已存在**的 GitHub 仓库；
- 新建了项目级 Skill，要交付到 skill 收集仓（如 `Liora-0521/workbuddy-skills`）；
- 用户问"远程推上去了没""远程和本地一致吗"——需要的是**校验**，不是重新推一遍。

**不触发**：

- 只要本地 `git commit`、明确说不推送 → 直接执行即可，不必走本流程；
- 只是读取远程内容（看 README、看文件树）→ 用 API 读，别克隆。

**边界**：

- 不替用户决定仓库可见性（public / private）——建仓前必问；
- **不做 `push --force`**，不重写已推送的历史；
- 不把凭据写进任何被 Git 追踪的文件；
- 建仓（仓库不存在）属于本 Skill 的前置动作，见 Step 0 备注。

---

## 二、输入信息

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `repo_url` | string | ✅ | 目标仓库地址，如 `https://github.com/Liora-0521/workbuddy-skills.git` |
| `paths` | list | ❌ | 本次要提交的路径。**默认只提交本次交付物**，不是"工作区里所有改动" |
| `branch` | string | ❌ | 默认以仓库 `default_branch` 为准（用 API 读，不靠猜） |
| `message` | string | ❌ | conventional commit；未给时由变更内容推导 |
| `mode` | enum | ❌ | `push`（默认）/ `verify`（只校验不推送）/ `dry-run`（只暂存不提交） |
| `credential` | — | ✅ | PAT 或 SSH。缺失时先从已有克隆的 local config 找 |

**关键约束**：`paths` 必须显式。**默认禁止 `git add -A`**——用户的桌面工作副本里常年躺着 `01.py`、`嗡嗡嗡` 这类临时文件，一把梭会全部推上公开仓库。

---

## 三、执行步骤

按顺序执行，**每一步都不可跳过**。

### Step 0 — 仓库不存在时先建仓

```bash
curl -sS --ssl-no-revoke -X POST https://api.github.com/user/repos \
  -H "Authorization: token $PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  --data-raw '{"name":"REPO","description":"...","private":false,"auto_init":true}'
```

返回体里的 `owner.login` 才是**真实用户名**——用户口述的用户名经常有笔误（把 `0521` 写成 `o521`），建仓后必须回读确认，否则克隆地址会错。

### Step 1 — 核实仓库真实状态

```bash
python -c "
import json,urllib.request,ssl
ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
req=urllib.request.Request('https://api.github.com/repos/<owner>/<repo>',
    headers={'User-Agent':'Mozilla/5.0','Accept':'application/vnd.github.v3+json'})
d=json.loads(urllib.request.urlopen(req,timeout=30,context=ctx).read().decode('utf-8'))
print(d['full_name'], '| default_branch =', d['default_branch'], '| private =', d['private'])
"
```

要拿到 404 与否、默认分支、可见性。**默认分支不一定是 `main`**，不要写死。

> 探状态码用 `curl -o /dev/null -w "%{http_code}"` 可用；但**要保存/解析 JSON 一律用 Python**，见 Step 8 坑表。

### Step 2 — 定位或创建本地工作副本

**优先复用已有克隆，不要新开一份。** 两份副本一定会漂移，最后分不清哪份是真：

```bash
find "C:/Users/zay/Desktop" "C:/Users/zay/WorkBuddy" -maxdepth 4 -type d -name "<repo-name>" 2>/dev/null
```

找不到才克隆：

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
```

**一个仓库只有一个工作副本**——这条如果做不到，宁可先把旧副本 `git status` 查清再决定。

### Step 3 — 放置凭据（只在 local config）

```bash
git config --local user.name  "<owner>"
git config --local user.email "<owner>@users.noreply.github.com"
git remote set-url origin https://<PAT>@github.com/<owner>/<repo>.git
```

- 只影响**本仓库的 local config**，不污染全局，也不进入被追踪的文件；
- `http.sslBackend openssl` 若报证书吊销错误时补上（见 Step 8）；
- **打印配置时必须脱敏**——`git config --list --local` 会把 remote URL 里的 PAT 原样吐出来：

```bash
git config --list --local | sed -E 's#(ghp_|github_pat_)[A-Za-z0-9_]+#***TOKEN***#g'
git remote -v           | sed -E 's#//[^@]*@#//***@#g'
```

### Step 4 — 清点工作区，圈出**不提交**的东西

```bash
git status --porcelain
```

把输出逐条过一遍，明确分类：

| 类别 | 处理 |
| --- | --- |
| 本次交付物（新 skill、README 等） | 进 `paths`，Step 6 显式 add |
| 用户散落的临时/练习文件（`01.py`、空文件、随手建的目录） | **不进 `paths`**，在交付说明里列出来 |
| 已被 `.gitignore` 覆盖的 | 不用管 |

这一步的产物是一份**显式的提交清单**，不是"全部"。

### Step 5 — 敏感信息扫描（提交前强制）

```bash
grep -rInE 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|BEGIN (RSA|OPENSSH|PRIVATE)' . --exclude-dir=.git
```

命中即**停止提交**，先清理再继续。同时确认 `.gitignore` 覆盖 `.env*`、`*.pem`、`*.key`、`*.p12`、`id_rsa*`、`.ssh/`、`secrets/`、`credentials*`。

### Step 6 — 选择性暂存

```bash
git add -- .workbuddy/skills/<new-skill> README.md

# 确认交付目录没被 .gitignore 误伤（退出码非 0 = 未被忽略 = 正常）
git check-ignore -v .workbuddy/skills/<new-skill>/SKILL.md || echo "未被忽略（正常）"

# 复核真正要提交的内容
git diff --cached --stat
git status --porcelain
```

`git diff --cached --stat` 是最后一道人工闸门：**没在这里出现的文件不会被推上去**，多出来的立刻查。

### Step 7 — 提交

```bash
git commit -F - << 'EOF'
feat(skill): add push-to-github project skill

- <改了什么>
- <为什么>
EOF
```

提交信息写**做了什么 + 为什么**，不要写"update files"。

### Step 8 — 推送

```bash
git push -u origin <branch>
```

错误对照（完整表见 `references/troubleshooting.md`）：

| 现象 | 处理 |
| --- | --- |
| `CRYPT_E_REVOCATION_OFFLINE (0x80092013)` | `git config --local http.sslBackend openssl` 后重试；`http.schannelCheckRevoke false` **无效** |
| `CONNECT tunnel failed, response 502` | 网络侧波动，**等 30–60 秒重试一次**，不要改配置 |
| `could not read Username` | 凭据没放对，回 Step 3 |

### Step 9 — 推送后校验（**本 Skill 的重点**）

推送返回成功 ≠ 远程内容正确。必须做**三源交叉校验**：

```bash
python .workbuddy/skills/push-to-github/scripts/verify_push.py
```

脚本做三件事并交叉比对：

1. `git ls-remote origin <branch>` → 远程真实 SHA；
2. `git rev-parse HEAD` → 本地 SHA；
3. GitHub API `git/trees/<sha>?recursive=1` → 远程文件树，与本地 `git ls-tree -r HEAD` **逐 blob 哈希**比对。

三者一致才算交付完成。**局部一致不算**：只比"提交 SHA 相同"会漏掉历史被改写、分支推错的情况；逐 blob 比对才能确认"内容真的一样"。

**不要只信本地 `origin/*`**：本环境下远程跟踪引用可能是过期的缓存，`git ls-tree origin/main` 会显示旧内容，看着像"推送丢了"。以 `git ls-remote` 和 API 为准。

---

## 四、输出结构

交付说明必须包含：

1. **提交清单**——本次实际提交的文件路径 + 每个文件是什么；
2. **提交 SHA 与提交信息**；
3. **推送结果 + 三源校验结论**（三个 SHA 值并排列出，附"逐 blob 一致"的判断）；
4. **本次未提交的文件及原因**（如疑似用户临时文件）——这条不能省，用户需要知道什么被留下了；
5. **剩余风险**——例如凭据明文存在于 local config、仓库可见性、token 待 revoke。

---

## 五、凭据与安全要求（硬红线）

1. **PAT 绝不进入任何被 Git 追踪的文件**，也不出现在 commit message、代码注释、README 里；
2. **PAT 也不应出现在对话与日志里**——打印 remote / config 必须走脱敏管道（Step 3）；
3. **把 PAT 拼进 remote URL 是已知取舍**：它明文落在 `.git/config`。该文件不被追踪，但会**随目录拷贝、备份、压缩包一起扩散**。这是"非交互推送能跑通"的最低成本方案，用之前先说清、任务结束提醒 revoke；
4. 长期方案：改用 SSH key，或系统凭据管理器（`git config --global credential.helper manager`）；
5. 任务结束提醒用户：GitHub → Settings → Developer settings → Personal access tokens → **revoke**；
6. 公开仓库要在 Step 5 扫描之后再推——公开仓库的历史一旦推上去，清除代价极高。

---

## 六、自检清单

推送前逐项确认，**未通过不得推送**：

- [ ] 目标仓库的 `full_name` / `default_branch` 是由 API 读到的，不是靠记忆或用户口述；
- [ ] 本地工作副本是**唯一**一份，没有第二个克隆在别处；
- [ ] `git status --porcelain` 的每一条都已分类，临时文件已明确排除；
- [ ] 提交用的是**显式路径**，没用 `git add -A` / `git add .`；
- [ ] `git check-ignore` 确认交付目录未被忽略；
- [ ] 敏感信息扫描已跑且无命中；
- [ ] `git diff --cached --stat` 列出的文件与预期完全一致；
- [ ] 提交信息说清了"做了什么 + 为什么"；
- [ ] 没有使用 `push --force`；
- [ ] 推送后跑了三源校验，且**逐 blob 哈希全部一致**；
- [ ] 交付说明里列出了"未提交的文件"；
- [ ] 已提醒用户 revoke / 轮换凭据。

---

## 七、参考

- 环境踩坑与诊断命令：[`references/troubleshooting.md`](references/troubleshooting.md)
- 推送后校验脚本：[`scripts/verify_push.py`](scripts/verify_push.py)
