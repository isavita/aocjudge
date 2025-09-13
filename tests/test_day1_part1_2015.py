import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "server"))
from main import aoc_eval

SOLUTIONS = {
    "python": "s=open('./input.txt').read().strip();print(s.count('(')-s.count(')'))",
    "javascript": "const fs=require('fs');const s=fs.readFileSync('./input.txt','utf8').trim();let f=0;for (const c of s){if(c==='(')f++;else if(c===')')f--; }console.log(f);",
    "ruby": "s=File.read('./input.txt').strip;f=s.count('(')-s.count(')');puts f",
    "rust": "use std::fs;fn main(){let s=fs::read_to_string('./input.txt').unwrap();let mut f=0;for c in s.chars(){if c=='(' {f+=1;} else if c==')' {f-=1;}}println!(\"{}\",f);}",
    "d": "import std.stdio, std.file;void main(){auto s=readText('./input.txt');int f=0;foreach(c; s){if(c=='(')f++;else if(c==')')f--; }writeln(f);}",
}

@pytest.mark.parametrize("lang,code", SOLUTIONS.items())
def test_day1_part1_2015(lang, code):
    resp = aoc_eval.fn("day1_part1_2015", lang, code)
    assert resp["pass"], f"{lang} failed: {resp}"
    assert resp["got"] == "280"
