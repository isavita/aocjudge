from fastmcp import FastMCP
from typing import Literal, Optional, List, Dict, Any
import os

from dataset import Dataset
from runner import run_code
from langs import SUPPORTED_LANGUAGES

NAME = os.getenv("AOCJUDGE_NAME", "AocJudge")
DATA_PATH = os.getenv("AOCJUDGE_DATA", "data/cases.jsonl")

mcp = FastMCP(NAME)
ds = Dataset(DATA_PATH)

CONTRACT_TEXT = (
    "Your program MUST read the puzzle input from a local file path './input.txt' "
    "and print ONLY the final answer to stdout. Stdin is NOT provided."
)

@mcp.tool
def aoc_health() -> dict:
    """Health & contract info for agents."""
    return {
        "ok": True,
        "cases": len(ds.all),
        "server": NAME,
        "supported_languages": SUPPORTED_LANGUAGES,
        "contract": CONTRACT_TEXT,
    }

@mcp.tool
def aoc_list_cases(year: Optional[int]=None, day: Optional[int]=None, part: Optional[int]=None) -> dict:
    """List cases; optional filters year/day/part."""
    items = ds.list(year=year, day=day, part=part)
    return {"items": items, "total": len(items)}

@mcp.tool
def aoc_get_case(name: str) -> dict:
    """
    Get only the case metadata and task text.
    Input and answer are intentionally NOT exposed by this API.
    """
    c = ds.get(name)
    if not c:
        return {"error": f"case not found: {name}"}
    return {
        "name": c.name,
        "year": c.year,
        "day": c.day,
        "part": c.part,
        "task": c.task,
    }

@mcp.tool
def aoc_eval(name: str, language: Literal[*SUPPORTED_LANGUAGES], code: str) -> dict:
    """
    Evaluate user code for a case.

    CONTRACT: Your code must read the input from './input.txt' and print ONLY the answer to stdout.
    Stdin is NOT provided.
    """
    c = ds.get(name)
    if not c:
        return {"error": f"case not found: {name}"}

    rc, out, err = run_code(language, code, c.input)

    got = (out or "").strip()
    expected = str(c.answer).strip()
    passed = (rc == 0) and (got == expected)

    resp: Dict[str, Any] = {
        "pass": passed,
        "got": got,
        "exit_code": rc,
        "language": language,
    }
    # Helpful guidance on failure
    if not passed:
        resp["hint"] = "Ensure your program reads from './input.txt' and prints only the final answer."
    if err.strip():
        resp["stderr"] = err.strip()
    return resp

if __name__ == "__main__":
    host = os.getenv("AOCJUDGE_HOST", "127.0.0.1")
    port = int(os.getenv("AOCJUDGE_PORT", "8000"))
    print(f"🚀 {NAME} on http://{host}:{port}/mcp  (HTTP transport)")
    print(f"📜 CONTRACT: {CONTRACT_TEXT}")
    mcp.run(transport="http", host=host, port=port)
