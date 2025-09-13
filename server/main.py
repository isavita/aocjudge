from fastmcp import FastMCP
from typing import Literal, Optional, List, Dict, Any
import os

from dataset import Dataset
from runner import run_code
from langs import LANGS

MAX_CODE_CHARS = 10_000_000
MAX_OUTPUT_CHARS = 4000
MAX_STDERR_CHARS = 4000

NAME = os.getenv("AOCJUDGE_NAME", "AocJudge")
DATA_PATH = os.getenv("AOCJUDGE_DATA", "data/cases.jsonl")

mcp = FastMCP(NAME)
ds = Dataset(DATA_PATH)

CONTRACT_TEXT = (
    "Your program MUST read the puzzle input from a local file path './input.txt' "
    "and print ONLY the final answer to stdout. Stdin is NOT provided."
)

@mcp.tool()
def aoc_info() -> dict:
    """
    Get server info, supported languages (including pre-installed libraries), and agent instructions.
    
    Returns:
        Dictionary containing server status, case count, supported languages (with pre-installed libraries), and instructions
    """
    return {
        "ok": True,
        "cases": len(ds.all),
        "server": NAME,
        "languages": LANGS,
        "agent_instructions": CONTRACT_TEXT,
    }

@mcp.tool()
def aoc_list_cases(year: Optional[int] = None, day: Optional[int] = None, part: Optional[int] = None) -> dict:
    """
    List available Advent of Code cases with optional filtering.
    
    Args:
        year: Filter by specific year (e.g., 2017, 2018)
        day: Filter by specific day (1-25)
        part: Filter by specific part (1 or 2)
    
    Returns:
        Dictionary containing filtered cases and total count
    """
    items = ds.list(year=year, day=day, part=part)
    return {"items": items, "total": len(items), "agent_instructions": CONTRACT_TEXT}

@mcp.tool()
def aoc_get_case(name: str, include: Optional[List[str]] = None) -> dict:
    """
    Get case metadata and task description for a specific case.
    
    Args:
        name: The case identifier (e.g., "day1_part1_2017")
        include: Optional list of fields to include (ignored, for compatibility)
    
    Returns:
        Dictionary with case metadata and task description, or error if not found
    
    Note:
        Input and answer are intentionally NOT exposed by this endpoint.
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
        "agent_instructions": CONTRACT_TEXT,
    }

@mcp.tool()
def aoc_eval(name: str, language: Literal[*LANGS.keys()], code: str) -> dict:
    """
    Evaluate user code against a specific Advent of Code case.
    You can use pre-installed libraries for each language.
    
    Args:
        name: The case identifier (e.g., "day1_part1_2017")
        language: Programming language ("python" or "go")
        code: The complete source code to evaluate
    
    Returns:
        Dictionary with evaluation results including pass/fail status, output, and any errors
    
    CONTRACT:
        Your code must read the input from './input.txt' and print ONLY the answer to stdout.
        Stdin is NOT provided.
    """
    c = ds.get(name)
    if not c:
        return {"error": f"case not found: {name}"}
    if len(code) > MAX_CODE_CHARS:
        return {"error": f"code too long: {len(code)} > {MAX_CODE_CHARS}"}

    rc, out, err, metrics = run_code(language, code, c.input)

    full_output = (out or "").strip()
    got = full_output[:MAX_OUTPUT_CHARS]
    expected = str(c.answer).strip()
    passed = (rc == 0) and (full_output == expected)

    resp: Dict[str, Any] = {
        "pass": passed,
        "got": got,
        "exit_code": rc,
        "language": language,
        "metrics": metrics,
        "agent_instructions": CONTRACT_TEXT,
    }
    # Helpful guidance on failure
    if not passed:
        resp["hint"] = "Ensure your program reads from './input.txt' and prints only the final answer."
    err = err.strip()
    if err:
        resp["stderr"] = err[:MAX_STDERR_CHARS]
    return resp

if __name__ == "__main__":
    host = os.getenv("AOCJUDGE_HOST", "127.0.0.1")
    port = int(os.getenv("AOCJUDGE_PORT", "8000"))
    print(f"🚀 {NAME} on http://{host}:{port}/mcp  (HTTP transport)")
    print(f"📜 CONTRACT: {CONTRACT_TEXT}")
    mcp.run(transport="http", host=host, port=port)
