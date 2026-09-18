# 推送至 GitHub —— 环境踩坑与诊断（Windows + 沙箱）

本文件记录的是**本机实测**过的现象，不是推测。每条按「现象 → 根因 → 解法」写。

---

## 一、凭据与配置

### 1.1 打印仓库配置会把 PAT 明文吐出来

**现象**：`git config --list --local` 输出里包含

```
remote.origin.url=https://ghp_<40位令牌>@github.com/<owner>/<repo>.git
```

**根因**：PAT 拼在 remote URL 里就会明文存进 `.git/config`。执行任何"看一眼配置"的命令都会把它带进终端输出、日志、对话记录。

**解法**：所有涉及 remote / config 的输出都过一遍脱敏：

```bash
git config --list --local | sed -E 's#(ghp_|github_pat_)[A-Za-z0-9_]+#***TOKEN***#g'
git remote -v           | sed -E 's#//[^@]*@#//***@#g'
```

**顺带结论**：既然 PAT 就明文躺在 `.git/config`，它随目录拷贝 / 备份 / 打包扩散是真实风险。任务结束提醒用户 revoke；长期改用 SSH 或凭据管理器。

### 1.2 `could not read Username for 'https://github.com'`

**根因**：remote URL 里没有凭据，且本机没有 credential helper、没有 SSH key。

**解法**：

```bash
git remote set-url origin https://<PAT>@github.com/<owner>/<repo>.git
```

---

## 二、网络与证书

### 2.1 `schannel: CRYPT_E_REVOCATION_OFFLINE (0x80092013)`

```
schannel: next InitializeSecurityContext failed: CRYPT_E_REVOCATION_OFFLINE (0x80092013)
由于吊销服务器已脱机，吊销功能无法检查证书是否吊销
```

**根因**：本机无法访问证书吊销列表（CRL/OCSP 被墙或不可达），schannel 严格模式直接拒绝连接。**与仓库配置无关。**

**解法**：

| 工具 | 有效 | 无效 |
| --- | --- | --- |
| git | `git config --local http.sslBackend openssl` | `http.schannelCheckRevoke false` |
| curl | 加 `--ssl-no-revoke` | — |

换成 openssl 后端后 push 持续可用。

### 2.2 `CONNECT tunnel failed, response 502`

**根因**：网络侧波动，代理隧道短暂不可用。

**解法**：**等 30–60 秒重试一次**。不要因此改任何配置——改了反而留下难以排查的残留配置。

### 2.3 `raw.githubusercontent.com` 偶发 `RemoteDisconnected` / `SSLEOFError`

**现象**：

```
http.client.RemoteDisconnected: Remote end closed connection without response
ssl.SSLEOFError: [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol
```

同一个域名，**前一次请求成功、后一次失败**。

**解法**：读单文件改用 GitHub API 的 `contents` 接口（返回 base64，自行解码），并带上 `User-Agent`（GitHub API 对无 UA 的请求不友好）；失败重试一次即可。要拿整个文件树用 `git/trees/<sha>?recursive=1`，一次请求解决，比拼多个 raw 请求稳。

---

## 三、工具链限制

### 3.1 `curl` 在本机**无法写文件**（连 `/tmp` 都写不进去）

**现象**：

```
curl: (23) Failure writing output to destination
```

`curl -o /tmp/x.json ...` 与 `curl ... > /tmp/x.json` **两种都失败**，文件不落地（随后读它会 `FileNotFoundError`）。

**可用**：`curl -sS --ssl-no-revoke -o /dev/null -w "%{http_code}\n" <url>` —— 探测状态码没问题。

**解法**：需要保存或解析响应体时改用 Python：

```python
import json, urllib.request, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                           "Accept": "application/vnd.github.v3+json"})
data = json.loads(urllib.request.urlopen(req, timeout=30, context=ctx).read().decode("utf-8"))
```

写文件用 **Windows 风格路径**（`C:/Users/...`），Git Bash 的 `/tmp` 与 Windows 临时目录不是一回事。

### 3.2 中文提交信息会让 `curl ... | python -c` 读 JSON 崩掉

**现象**：`UnicodeDecodeError`。

**解法**：校验同步状态用 `git ls-remote origin <branch>` 对 SHA，**不要**用 `curl | python -c` 去解析 GitHub API 的 JSON 输出。

### 3.3 GUI 程序无法启动

「帮我打开仓库/文件夹」在这类环境里基本无效：`start ""`、`Start-Process explorer.exe`、`cmd /c`、WScript.Shell COM 会被安全策略拦掉。

**可行替代**：

1. `present_files` 传 https URL → 在内置浏览器面板打开；
2. 写一个 `.url` 文件到桌面（纯文本 INI，双击即用本地浏览器打开）：

   ```
   [InternetShortcut]
   URL=https://github.com/<owner>/<repo>
   ```

3. 如实告知用户这是环境限制，**不要假装命令已生效**。

---

## 四、校验环节的假象（最容易误判）

### 4.1 `git ls-tree origin/main` 显示旧内容 → 看着像"推送丢了"

**根因**：本地的 `refs/remotes/origin/main` 是过期缓存。`git fetch` 在这种环境下可能报告成功但 ref 没真正落盘。

**解法**：

- 校验远程状态**以 `git ls-remote origin <branch>` 和 GitHub API 为准**；
- **不要**尝试用 `git update-ref` 修：本机实测返回 exit 0，但 `.git/packed-refs` 并未真正改写。要改就去编辑 `.git/packed-refs` 里对应那一行。

### 4.2 只比"提交 SHA 相同"不够

**现象**：本地和远程 HEAD 一致，但远程分支上少文件 / 多文件。

**根因**：SHA 相同只说明这个 commit 存在，不保证它就是分支 tip、也不保证工作副本内容没被本地未提交改动带偏。

**解法**：跑**三源交叉校验**——`git ls-remote`（远程 tip）+ `git ls-tree -r HEAD`（本地内容）+ API `git/trees/<sha>`（远程内容），**逐 blob 哈希比对**。一致才算干净。

```bash
python .workbuddy/skills/push-to-github/scripts/verify_push.py
```

### 4.3 "200 就代表能用"

读远程文件时，**状态码 200 不等于内容正确**：可能重定向到占位页（区域不可用 / 登录页），也可能返回的是旧缓存。核对最终跳转地址与内容本体，别只看状态码。

---

## 五、一页诊断命令

```bash
# 我在哪、谁是我
git rev-parse --show-toplevel && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD

# 远程真实 tip（权威）
git ls-remote origin HEAD refs/heads/main

# remote 配置（脱敏）
git remote -v | sed -E 's#//[^@]*@#//***@#g'

# 工作区全貌（每一条都要分类）
git status --porcelain

# 暂存区最终清单（最后一道人工闸门）
git diff --cached --stat

# 交付目录有没有被忽略
git check-ignore -v <path> || echo "未被忽略（正常）"

# 敏感信息扫描
grep -rInE 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|BEGIN (RSA|OPENSSH|PRIVATE)' . --exclude-dir=.git
```

---

## 六、踩坑的共同模式

回头看，这些坑里真正会**让人做出错误结论**的只有两类：

1. **读了中间层/缓存就下结论**——`git ls-tree origin/main` 是缓存，HTTP 状态码是中间层；
2. **信了工具的退出码就下结论**——`git update-ref` 返回 0 却没落盘，`Start-Process -Wait` 返回 1 但安装其实成功。

**对策统一为一条**：关键结论必须由**两个以上独立来源**互相印证，且优先采信更接近真相源的那一个（远程 API > 本地缓存）。
