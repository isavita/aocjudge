# aocjudge (AdventOfCodeJudge)

A FastMCP-based Advent of Code judging system that runs user code in Docker containers for safe execution.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Aleksandar Dimov

## Project Structure

```

aocjudge/
├── server/
│   ├── main.py               # FastMCP HTTP server + tools
│   ├── runner.py             # Docker sandbox execution
│   └── dataset.py            # JSONL case loader
├── data/
│   └── cases.jsonl           # Test cases: name, year, day, part, task, input, answer
├── docker/
│   ├── rust.Dockerfile       # Rust execution environment
│   ├── python.Dockerfile     # Python execution environment
│   ├── javascript.Dockerfile # JavaScript execution environment
│   ├── ruby.Dockerfile       # Ruby execution environment
│   ├── d.Dockerfile          # D execution environment
│   └── racket.Dockerfile     # Racket execution environment
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
├── LICENSE                   # MIT License
└── README.md                 # This file

```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install pytest

# Run tests
pytest -q
```

### 2. Build Docker Images

The runtime images for each language are published on Docker Hub under
[`baruh/aocjudge-*`](https://hub.docker.com/r/baruh).
If you want to build them yourself instead, run:

```bash
# Build sandbox images (run once)
docker build -t baruh/aocjudge-rs -f docker/rust.Dockerfile .
docker build -t baruh/aocjudge-py -f docker/python.Dockerfile .
docker build -t baruh/aocjudge-js -f docker/javascript.Dockerfile .
docker build -t baruh/aocjudge-rb -f docker/ruby.Dockerfile .
docker build -t baruh/aocjudge-d  -f docker/d.Dockerfile .
docker build -t baruh/aocjudge-rkt -f docker/racket.Dockerfile .
docker build -t baruh/aocjudge-server -f docker/server.Dockerfile .

# Push to Docker Hub
docker push baruh/aocjudge-rs
docker push baruh/aocjudge-py
docker push baruh/aocjudge-js
docker push baruh/aocjudge-rb
docker push baruh/aocjudge-d
docker push baruh/aocjudge-rkt
docker push baruh/aocjudge-server
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
# Server runs on http://localhost:8000/mcp

# Basic health check
curl http://localhost:8000/
# -> {"ok": true, "server": "AdventOfCodeJudge", "endpoint": "/mcp"}

# Hitting /mcp without a proper MCP handshake will return HTTP 400
# (that's expected when visiting in a browser)
```

### 5. Expose via ngrok (optional)

```bash
# In separate terminal
ngrok http 8000
# Use the https URL in your MCP client: https://<id>.ngrok-free.app/mcp
```

## Environment Variables

The server can be configured using the following `AOCJUDGE_*` environment variables:

| Variable              | Default            | Description                               |
| --------------------- | ------------------ | ----------------------------------------- |
| `AOCJUDGE_NAME`       | `AdventOfCodeJudge`| Displayed server name                     |
| `AOCJUDGE_DATA`       | `data/cases.jsonl` | Path to the cases dataset                 |
| `AOCJUDGE_HOST`       | `0.0.0.0`         | Host interface for the HTTP server        |
| `AOCJUDGE_PORT`       | `8000`             | Port for the HTTP server                  |
| `AOCJUDGE_TIMEOUT_MS` | `8000`             | Sandbox execution timeout in milliseconds |

## Available Tools

* `aoc_info()` - Get server info, supported languages, and agent instructions
* `aoc_list_cases(year?, day?, part?)` - List cases with optional filters
* `aoc_get_case(name, include?)` - Get case details
* `aoc_eval(name, language, code)` - Evaluate user code against a case

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
    "code":"s=open('./input.txt').read().strip()\nprint(sum(int(s[i]) for i in range(len(s)) if s[i]==s[(i+1)%len(s)]))"
  }
}
```

## Security Features

* Docker containers run with limited resources (256MB RAM, 0.5 CPU)
* Read-only filesystem mounts
* No network access
* Non-root user execution
* Configurable timeout limits

## Deployment

The judge server can be deployed anywhere you have access to Docker. A small
virtual machine or a free-tier provider such as **Fly.io**, **Railway**, or a
similar host is usually sufficient. You will need enough disk space to store
the sandbox images (roughly a few hundred megabytes in total).

### 1. Obtain sandbox images

Runtime images are published at Docker Hub under `baruh/aocjudge-*` and will be
pulled automatically. To build them yourself, run:

```bash
./scripts/build-images.sh
# Optionally tag and push each image
docker tag aocjudge-py baruh/aocjudge-py && docker push baruh/aocjudge-py
# ...repeat for other languages as needed
```

### 2. Run with Docker Compose

The project includes a `docker-compose.yml` that runs the server alongside an
internal Docker daemon. It pulls the published images automatically:

```bash
docker compose up
```

The server will be available on <http://localhost:8000/mcp>. In production you
can publish the port and expose it through your platform's networking or an MCP
connector.

### 3. Deploy to Railway

Railway can deploy the compose stack directly. After installing the
[Railway CLI](https://docs.railway.com/reference/cli), run:

```bash
railway init     # one-time project setup
railway up       # builds/pulls images and deploys the stack
```

The compose file references the `baruh/aocjudge-server` image and the published
runtime images. Make sure your Railway project has access to Docker Hub if the
images are private.

When connecting this repository directly in the Railway dashboard, the included
`Procfile` provides a start command (`python server/main.py`). Add a separate
service using the `docker:24-dind` image and set `DOCKER_HOST=tcp://dind:2375`
on the server service so code evaluation works.


## Pre-installed Libraries

The following libraries are pre-installed in the execution environments:

* **Python**: `numpy`, `pandas`
* **JavaScript**: `lodash`
* **Ruby**: `nokogiri`
* **D**: None
* **Rust**: None
* **Racket**: None

## Language-Specific Configurations

### Rust

* Uses a temporary filesystem at `/tmp` with execution permissions
* Required for Rust's compilation process and temporary file operations
* Configured via `--tmpfs /tmp:exec` Docker option

### Python

* Runs in read-only environment
* No additional filesystem modifications required

### Ruby

* Runs in read-only environment
* No additional filesystem modifications required

## Adding Test Cases

Add new cases to `data/cases.jsonl` in JSONL format:

```json
{"name":"case_name","year":2023,"day":1,"part":1,"task":"Description","input":"test_input","answer":"expected_output"}
```
