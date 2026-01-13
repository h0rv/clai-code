#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pydantic_ai"]
# ///
"""clai-code - minimal pydantic-ai cli coding agent"""

import os, re, glob as g, subprocess
from pydantic_ai import Agent

agent = Agent(os.environ.get("MODEL", "anthropic:claude-sonnet-4-5"), instructions=f"Concise coding assistant. cwd: {os.getcwd()}")

@agent.tool_plain(description="Read file with line numbers")
def read(path: str, offset: int = 0, limit: int = 10000) -> str:
    return "".join(f"{offset + i + 1:4}| {l}" for i, l in enumerate(open(path).readlines()[offset : offset + limit]))

@agent.tool_plain(description="Write content to file")
def write(path: str, content: str) -> str:
    return str(open(path, "w").write(content)) and "ok"

@agent.tool_plain(description="Replace old with new in file")
def edit(path: str, old: str, new: str, replace_all: bool = False) -> str:
    text = open(path).read()
    if old not in text: return "error: not found"
    if not replace_all and text.count(old) > 1: return f"error: {text.count(old)} matches"
    return str(open(path, "w").write(text.replace(old, new) if replace_all else text.replace(old, new, 1))) and "ok"

@agent.tool_plain(description="Find files by glob pattern")
def glob(pattern: str, path: str = ".") -> str:
    files = sorted(g.glob(f"{path}/{pattern}".replace("//", "/"), recursive=True), key=lambda f: os.path.getmtime(f) if os.path.isfile(f) else 0, reverse=True)
    return "\n".join(files) or "none"

@agent.tool_plain(description="Search files for regex")
def grep(pattern: str, path: str = ".") -> str:
    hits = []
    for f in g.glob(f"{path}/**", recursive=True):
        try: hits.extend(f"{f}:{n}:{l.strip()}" for n, l in enumerate(open(f), 1) if re.search(pattern, l))
        except: pass
    return "\n".join(hits[:50]) or "none"

@agent.tool_plain(description="Run shell command")
def bash(cmd: str) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return (r.stdout + r.stderr).strip() or "(empty)"

if __name__ == "__main__": agent.to_cli_sync(prog_name="clai-code")
