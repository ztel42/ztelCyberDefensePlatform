# Honeygrid Agent


## Overview
The **Honeygrid Agent** is a lightweight, distributed honeypot service that listens on configurable ports, logs attacker interactions, and forwards telemetry to a central Collector API for correlation and analysis. It is the first component of the **Cyber Defense Platform** — a modular cybersecurity ecosystem combining threat collection, visualization, and incident response capabilities.


---


## Features
- Emulates multiple network services (e.g., SSH, HTTP, SMB)
- Captures source IP, ports, timestamps, and payloads
- Forwards data to a central Collector API (FastAPI-based)
- Local fallback logging when the collector is unreachable
- Configurable via `config.yaml`
- Runs autonomously or as a Docker container


---


## Directory Structure
```
honeygrid_agent/
├── agent.py
├── config.yaml
├── honeygrid_agent.log
├── requirements.txt
└── Dockerfile
```


---


## Installation


### **1. Clone the Repository**
```bash
git clone https://github.com/ztel42/Honeygrid_Agent.git
cd Honeygrid_Agent
```


### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```


### **3. Configure the Agent**
Create a `config.yaml` file in the root directory:


```yaml
api_endpoint: "http://localhost:8000/api/v1/ingest"
ports:
- 22
- 80
- 445
- 8080
log_level: "INFO"
```


---


## Usage
Run the agent directly:
```bash
python agent.py
```


Expected output:
```
[*] Listening on port 22
[*] Listening on port 80
[*] Listening on port 445
[*] Listening on port 8080
```
Logs are stored in `honeygrid_agent.log`.


---


## Requirements
- Python 3.8+
- `requests`
- `PyYAML`
- `logging`


To install dependencies manually:
```bash
pip install requests PyYAML
```


---


## How It Works
1. Listens on configured ports.
2. When a connection is received, logs source IP, payload, and timestamp.
3. Attempts to send this data to the Collector API.
4. Falls back to local storage (`unsent_logs.json`) if the network call fails.


---


## Example Use Case
You can deploy multiple Honeygrid Agents across your network to gather real-world attacker telemetry. The data can then be ingested by the **ThreatGraph Engine** to visualize attacker behavior, and combined with the **IR-Toolkit** for automated incident response.


---
