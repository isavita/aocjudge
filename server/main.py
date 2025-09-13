from fastmcp import FastMCP
from typing import Literal, Optional, List, Dict, Any
import os

from dataset import Dataset
from runner import run_go, run_python

NAME = os.getenv("AOCJUDGE_NAME", "AocJudge")
DATA_PATH = os.getenv("AOCJUDGE_DATA", "data/cases.jsonl")

mcp = FastMCP(NAME)
ds = Dataset(DATA_PATH)

@mcp.tool
def aoc_health() -> dict:
    """Health check."""
    return {"ok": True, "cases": len(ds.all), "server": NAME}

@mcp.tool
def aoc_list_cases(year: Optional[int]=None, day: Optional[int]=None, part: Optional[int]=None) -> dict:
    """List cases; optional filters year/day/part."""
    items = ds.list(year=year, day=day, part=part)
    return {"items": items, "total": len(items)}

@mcp.tool
def aoc_get_case(name: str, include: Optional[List[Literal["task","input","answer"]]] = None) -> dict:
    """Get a case by name; include fields from ['task','input','answer']."""
    include = include or ["task"]
    c = ds.get(name)
    if not c:
        return {"error": f"case not found: {name}"}
    base: Dict[str, Any] = {"name": c.name, "year": c.year, "day": c.day, "part": c.part}
    for key in include:
        base[key] = getattr(c, key)
    return base

@mcp.tool
def aoc_eval(name: str, language: Literal["go","python"], code: str) -> dict:
    """
    Evaluate user code for a case.
    Contract: code reads stdin or ./input.txt, prints the answer to stdout.
    """
    c = ds.get(name)
    if not c:
        return {"error": f"case not found: {name}"}
    if language == "go":
        rc, out, err = run_go(code, c.input)
    elif language == "python":
        rc, out, err = run_python(code, c.input)
    else:
        return {"error": f"unsupported language: {language}"}

    got = (out or "").strip()
    expected = str(c.answer).strip()
    passed = (rc == 0) and (got == expected)
    resp = {"pass": passed, "got": got, "expected": None if passed else expected, "exit_code": rc}
    if err.strip():
        resp["stderr"] = err.strip()[:2000] # Truncate the error message
    return resp

if __name__ == "__main__":
    host = os.getenv("AOCJUDGE_HOST", "127.0.0.1")
    port = int(os.getenv("AOCJUDGE_PORT", "8000"))
    print(f"🚀 {NAME} on http://{host}:{port}/mcp  (HTTP transport)")
    mcp.run(transport="http", host=host, port=port)
