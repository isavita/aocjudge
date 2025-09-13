from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

@dataclass(frozen=True)
class Case:
    name: str
    year: int
    day: int
    part: int
    task: str
    input: str
    answer: str

class Dataset:
    def __init__(self, path: str = "data/cases.jsonl"):
        self.by_name: Dict[str, Case] = {}
        self.all: List[Case] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                c = Case(
                    name=obj["name"],
                    year=int(obj["year"]),
                    day=int(obj["day"]),
                    part=int(obj["part"]),
                    task=obj["task"],
                    input=obj["input"],
                    answer=str(obj["answer"]),
                )
                self.by_name[c.name] = c
                self.all.append(c)

    def list(self, year: Optional[int]=None, day: Optional[int]=None, part: Optional[int]=None):
        res = self.all
        if year is not None:
            res = [c for c in res if c.year == year]
        if day is not None:
            res = [c for c in res if c.day == day]
        if part is not None:
            res = [c for c in res if c.part == part]
        return [{"name": c.name, "year": c.year, "day": c.day, "part": c.part} for c in res]

    def get(self, name: str) -> Optional[Case]:
        return self.by_name.get(name)
