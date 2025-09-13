# AocJudge

A FastMCP-based Advent of Code judging system that runs user code in Docker containers for safe execution.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Aleksandar Dimov

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
│   ├── rust.Dockerfile    # Rust execution environment
│   └── python.Dockerfile # Python execution environment
│   └── javascript.Dockerfile # JavaScript execution environment
│   └── ruby.Dockerfile # Ruby execution environment
│   └── d.Dockerfile # D execution environment
├── requirements.txt     # Python dependencies
├── .env.example        # Configuration template
├── LICENSE             # MIT License
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
docker build -t aocjudge-rs -f docker/rust.Dockerfile .
docker build -t aocjudge-py -f docker/python.Dockerfile .
docker build -t aocjudge-js -f docker/javascript.Dockerfile .
docker build -t aocjudge-rb -f docker/ruby.Dockerfile .
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

## Environment Variables

The server can be configured using the following `AOCJUDGE_*` environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `AOCJUDGE_NAME` | `AocJudge` | Displayed server name |
| `AOCJUDGE_DATA` | `data/cases.jsonl` | Path to the cases dataset |
| `AOCJUDGE_HOST` | `127.0.0.1` | Host interface for the HTTP server |
| `AOCJUDGE_PORT` | `8000` | Port for the HTTP server |
| `AOCJUDGE_TIMEOUT_MS` | `8000` | Sandbox execution timeout in milliseconds |

## Available Tools

- `aoc_info()` - Get server info, supported languages, and agent instructions
- `aoc_list_cases(year?, day?, part?)` - List cases with optional filters
- `aoc_get_case(name, include?)` - Get case details
- `aoc_eval(name, language, code)` - Evaluate user code against a case

## Example Usage

### Server Info
```json
{"tool_name":"aoc_info","arguments":{}}
```

### List Cases
```json
{"tool_name":"aoc_list_cases","arguments":{"year":2017,"day":1}}
```

### Get Case Details
```json
{"tool_name":"aoc_get_case","arguments":{"name":"day1_part1_2017","include":["task","input"]}}
```

### Evaluate Rust Code
```json
{
  "tool_name":"aoc_eval",
  "arguments":{
    "name":"day1_part1_2017",
    "language":"rust",
    "code":"use std::fs;fn main(){let s=fs::read_to_string(\"./input.txt\").unwrap();let b=s.trim().as_bytes();let mut sum=0;for i in 0..b.len(){if b[i]==b[(i+1)%b.len()]{sum+=(b[i]-b'0') as i32}};println!(\"{}\",sum);}"
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

## Pre-installed Libraries

The following libraries are pre-installed in the execution environments:

- **Python**: `numpy`, `pandas`
- **JavaScript**: `lodash`
- **Ruby**: `nokogiri`
- **D**: None
- **Rust**: None

## Language-Specific Configurations

### Rust
- Uses a temporary filesystem at `/tmp` with execution permissions
- Required for Rust's compilation process and temporary file operations
- Configured via `--tmpfs /tmp:exec` Docker option

### Python
- Runs in read-only environment
- No additional filesystem modifications required

### Ruby
- Runs in read-only environment
- No additional filesystem modifications required

## Adding Test Cases

Add new cases to `data/cases.jsonl` in JSONL format:

```json
{"name":"case_name","year":2023,"day":1,"part":1,"task":"Description","input":"test_input","answer":"expected_output"}
```
