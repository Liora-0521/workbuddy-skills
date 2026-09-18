#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推送后三源交叉校验：确认 GitHub 远程内容与本地 HEAD 完全一致。

三个来源：
  1. git ls-remote origin <branch>         -> 远程分支真实 tip（权威，不受本地缓存影响）
  2. git rev-parse HEAD                    -> 本地 HEAD
  3. GitHub API git/trees/<sha>?recursive=1 -> 远程文件树（逐 blob 哈希）

判据：三个 SHA 一致 **且** 远程 blob 的 (路径 -> 哈希) 集合与本地 git ls-tree -r HEAD 完全相同。

用法：
    python verify_push.py                      # 自动从 origin 推断仓库与分支
    python verify_push.py --branch main
    python verify_push.py --repo owner/name
    python verify_push.py --skip-api           # 断网时只做 1+2，会明确标注"未完整校验"

退出码：0 = 完全一致   1 = 不一致   2 = 无法完成校验（网络/环境原因）
"""

import argparse
import json
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) verify_push"


def info(msg):
    print(msg, flush=True)


def run_git(args, cwd):
    p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def repo_root():
    code, out, err = run_git(["rev-parse", "--show-toplevel"], None)
    if code != 0:
        info("ERR  当前目录不在 Git 仓库内：%s" % (err or out))
        sys.exit(2)
    return out


def current_branch(root):
    code, out, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    if code == 0 and out and out != "HEAD":
        return out
    return None


def remote_url(root):
    code, out, _ = run_git(["remote", "get-url", "origin"], root)
    return out if code == 0 else ""


def parse_owner_repo(url):
    """从 remote URL 提取 owner/repo，自动剥掉内嵌凭据。"""
    if not url:
        return None
    u = re.sub(r"//[^@/]*@", "//", url)                      # 去掉 user:token@
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", u)
    if not m:
        return None
    return "%s/%s" % (m.group(1), m.group(2))


def gh_api(path, timeout=30):
    """调 GitHub API，先走系统证书校验，失败再降级为不校验证书。"""
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"User-Agent": UA, "Accept": "application/vnd.github.v3+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8")), None
    except Exception as first:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            return None, "HTTP %s" % e.code
        except Exception as e:
            return None, "%s: %s" % (type(first).__name__, e)


def local_blobs(root):
    """本地 HEAD 的 blob 映射：path -> sha（只取文件，不取目录）。"""
    code, out, err = run_git(["ls-tree", "-r", "HEAD"], root)
    if code != 0:
        info("ERR  读取本地文件树失败：%s" % err)
        sys.exit(2)
    blobs = {}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 3 and parts[1] == "blob":
            blobs[path] = parts[2]
    return blobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="owner/name，缺省从 origin 推断")
    ap.add_argument("--branch", help="分支名，缺省取当前分支")
    ap.add_argument("--skip-api", action="store_true", help="跳过 API，只做 ls-remote 对 HEAD")
    args = ap.parse_args()

    root = repo_root()
    branch = args.branch or current_branch(root)
    if not branch:
        info("ERR  处于 detached HEAD 且未指定 --branch")
        sys.exit(2)

    url = remote_url(root)
    repo = args.repo or parse_owner_repo(url)
    info("仓库根目录 : %s" % root)
    info("origin     : %s" % re.sub(r"//[^@/]*@", "//***@", url))
    info("目标仓库   : %s" % (repo or "（无法推断，可用 --repo 指定）"))
    info("分支       : %s" % branch)
    info("-" * 62)

    # --- 来源 1：本地 HEAD -------------------------------------------------
    code, local_sha, err = run_git(["rev-parse", "HEAD"], root)
    if code != 0:
        info("ERR  读取本地 HEAD 失败：%s" % err)
        sys.exit(2)
    info("1) 本地 HEAD        : %s" % local_sha)

    # --- 来源 2：远程真实 tip（ls-remote，权威） ---------------------------
    code, out, err = run_git(["ls-remote", "origin", "refs/heads/%s" % branch], root)
    if code != 0 or not out:
        info("ERR  git ls-remote 失败：%s" % (err or "无输出"))
        if "REVOCATION" in (err or "").upper():
            info("     -> 试：git config --local http.sslBackend openssl")
        sys.exit(2)
    remote_sha = out.split()[0]
    info("2) 远程 ls-remote   : %s" % remote_sha)

    sha_match = local_sha == remote_sha
    info("   SHA 比对         : %s" % ("一致 ✅" if sha_match else "不一致 ❌"))

    # 本地 origin/* 缓存，仅作参考，不作为判据
    code, cached, _ = run_git(["rev-parse", "refs/remotes/origin/%s" % branch], root)
    if code == 0:
        stale = "" if cached == remote_sha else "   << 本地缓存已过期，勿以此为准"
        info("   (参考)本地缓存   : %s%s" % (cached, stale))

    if args.skip_api:
        info("-" * 62)
        info("跳过 API：只完成了 SHA 比对，**文件级一致性未校验**。")
        sys.exit(0 if sha_match else 1)

    # --- 来源 3：远程文件树（API） ----------------------------------------
    if not repo:
        info("WARN 无法推断 owner/repo，文件级校验跳过。")
        sys.exit(0 if sha_match else 1)

    tree, api_err = gh_api("/repos/%s/git/trees/%s?recursive=1" % (repo, remote_sha))
    if tree is None:
        info("WARN GitHub API 不可用（%s），文件级校验跳过。" % api_err)
        info("     可稍后重试；仅凭 SHA 一致**不足以**确认内容一致。")
        sys.exit(0 if sha_match else 1)

    remote_blobs = {
        t["path"]: t["sha"] for t in tree.get("tree", []) if t.get("type") == "blob"
    }
    info("3) 远程文件树(API)  : %d 个文件" % len(remote_blobs))

    local = local_blobs(root)
    info("   本地文件树       : %d 个文件" % len(local))

    only_local = sorted(set(local) - set(remote_blobs))
    only_remote = sorted(set(remote_blobs) - set(local))
    diff = sorted(p for p in set(local) & set(remote_blobs) if local[p] != remote_blobs[p])

    info("-" * 62)
    if not (sha_match and not only_local and not only_remote and not diff):
        if only_local:
            info("仅存在于本地（未推上去）：")
            for p in only_local[:40]:
                info("  - %s" % p)
        if only_remote:
            info("仅存在于远程（本地没有）：")
            for p in only_remote[:40]:
                info("  + %s" % p)
        if diff:
            info("内容不一致（同路径不同哈希）：")
            for p in diff[:40]:
                info("  ~ %s" % p)
        if not sha_match:
            info("SHA 不一致：本地 %s / 远程 %s" % (local_sha[:10], remote_sha[:10]))
        info("结论：❌ 远程与本地不一致")
        sys.exit(1)

    info("逐 blob 哈希比对 : %d 个文件全部一致 ✅" % len(local))
    info("结论：✅ 远程与本地完全一致（%s）" % local_sha[:10])
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(2)
