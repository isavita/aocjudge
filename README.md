# AocJudge

A FastMCP-based Advent of Code judging system that runs user code in Docker containers for safe execution.

## Project Structure

```
aocjudge/
├── server/
│   ├── main.py          # FastMCP HTTP server + tools
│   ├── runner.py        # Docker sandbox execution
│   └── dataset.py       # JSONL case loader
├── data/
│   └── cases.jsonl      # Test cases: name,year,day,part,task,input,answer
├── docker/
│   ├── go.Dockerfile    # Go execution environment
│   └── python.Dockerfile # Python execution environment
├── requirements.txt     # Python dependencies
├── .env.example        # Configuration template
└── README.md           # This file
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Build Docker Images

```bash
# Build sandbox images (run once)
docker build -t aocjudge-go -f docker/go.Dockerfile .
docker build -t aocjudge-py -f docker/python.Dockerfile .
```

### 3. Configure Environment

```bash
# Copy and customize environment file
cp .env.example .env
# Edit .env as needed
```

### 4. Start Server

```bash
python server/main.py
# Server runs on http://127.0.0.1:8000/mcp
```

### 5. Expose via ngrok (optional)

```bash
# In separate terminal
ngrok http 8000
# Use the https URL in your MCP client: https://<id>.ngrok-free.app/mcp
```

## Available Tools

- `aoc_health()` - Health check and case count
- `aoc_list_cases(year?, day?, part?)` - List cases with optional filters
- `aoc_get_case(name, include?)` - Get case details
- `aoc_eval(name, language, code)` - Evaluate user code against a case

## Example Usage

### Health Check
```json
{"tool_name":"aoc_health","arguments":{}}
```

### List Cases
```json
{"tool_name":"aoc_list_cases","arguments":{"year":2017,"day":1}}
```

### Get Case Details
```json
{"tool_name":"aoc_get_case","arguments":{"name":"day1_part1_2017","include":["task","input"]}}
```

### Evaluate Go Code
```json
{
  "tool_name":"aoc_eval",
  "arguments":{
    "name":"day1_part1_2017",
    "language":"go",
    "code":"package main\nimport(\"bufio\";\"fmt\";\"os\")\nfunc main(){in:=bufio.NewScanner(os.Stdin);in.Scan();s:=in.Text();sum:=0;for i:=0;i<len(s);i++{if s[i]==s[(i+1)%len(s)]{sum+=int(s[i]-'0')}};fmt.Println(sum)}"
  }
}
```

### Evaluate Python Code
```json
{
  "tool_name":"aoc_eval",
  "arguments":{
    "name":"day1_part1_2017",
    "language":"python",
    "code":"import sys\ns=sys.stdin.read().strip()\nprint(sum(int(s[i]) for i in range(len(s)) if s[i]==s[(i+1)%len(s)]))"
  }
}
```

## Security Features

- Docker containers run with limited resources (256MB RAM, 0.5 CPU)
- Read-only filesystem mounts
- No network access
- Non-root user execution
- Configurable timeout limits

## Adding Test Cases

Add new cases to `data/cases.jsonl` in JSONL format:

```json
{"name":"case_name","year":2023,"day":1,"part":1,"task":"Description","input":"test_input","answer":"expected_output"}
```
