# PurpleForge -- Detection Engine Architecture

PurpleForge is a modular detection engineering framework designed for
controlled laboratory environments.\
It enables security engineers to simulate adversarial activity and test
detection rules in a safe, isolated setup.

This project is intended strictly for educational and laboratory use
only.\
Do NOT use against production systems or environments without explicit
authorization.

------------------------------------------------------------------------

## Project Purpose

PurpleForge is built to:

-   Simulate attack telemetry in controlled and intentionally vulnerable lab environments (for education/research only)
-   Test and validate detection rules
-   Experiment with rule engine architecture
-   Support threat modeling and security research workflows
-   Demonstrate how intentionally vulnerable lab environments can be safely hardened and improved

The focus of this project is **Security Engineering**, not offensive
tooling.

------------------------------------------------------------------------

## Architecture Overview

The repository follows a modular structure:

    PurpleForge-DetectionEngineArchitecture/
    ├── core/            # Engine core logic
    ├── detector/        # Detection rule and engine
    ├── simulations/     # Controlled adversarial event simulations
    ├── parsers/         # Log parsing components
    ├── mapping/         # MITRE ATT&CK mappings, tactic, severity, and attack descriptions
    ├── state/           # Alert and engine state management
    ├── configs/         # Configuration files
    ├── labs/            # Intentionally vulnerable lab environments
    ├── LAB_SECURITY_GUIDE.md
    ├── THREAT_MODEL.md
    └── README.md

------------------------------------------------------------------------

## Key Concepts

### Detection Engine

Processes telemetry events (system logs, network events, and simulated attack signals) and evaluates them against defined detection rules.

### Event Simulation

Instead of performing real attacks, PurpleForge generates controlled
security events to test detection logic.

### Threat Modeling

The included threat model documents potential abuse cases, trust
boundaries, and mitigation strategies.

### Lab Security Guide

Provides step-by-step guidance on how to safely operate, analyze, and harden the intentionally vulnerable labs, highlighting best practices for mitigating common security risks.

------------------------------------------------------------------------

## Usage

Clone the repository:

    git clone https://github.com/kapatalcs/PurpleForge-DetectionEngineArchitecture.git
    cd PurpleForge-DetectionEngineArchitecture

PurpleForge is intended to be run in an isolated lab environment.

### Running the Engine
After cloning the repository, navigate to the root directory and run the main CLI:
```bash
cd PurpleForge-DetectionEngineArchitecture
python -m core.cli
```


------------------------------------------------------------------------
## Installation / Requirements


PurpleForge requires several Python packages to run correctly.  
All dependencies are listed in the `requirements.txt` file.


## Security Notice

-   All simulations are designed for controlled testing.
-   No real exploitation of external systems is supported.
-   Any offensive-like behavior should remain restricted to local lab
    environments.
-   Do not attempt to run these simulations against production or external systems.

------------------------------------------------------------------------

## License

MIT License



## Scheme

```mermaid
graph LR
    %% Renk ve Stil Tanımlamaları
    classDef lab fill:#2d3436,stroke:#a29bfe,stroke-width:2px,color:#fff,rx:5px,ry:5px;
    classDef core fill:#6c5ce7,stroke:#dfe6e9,stroke-width:3px,color:#fff,rx:10px,ry:10px;
    classDef component fill:#4a3055,stroke:#a29bfe,stroke-width:1px,color:#fff,rx:5px,ry:5px;
    classDef config fill:#2d3436,stroke:#ffeaa7,stroke-width:1px,color:#fff,stroke-dasharray: 5 5;
    classDef storage fill:#2d3436,stroke:#00b894,stroke-width:2px,color:#fff,shape:cylinder;

    %% Sol Kısım: Girdi Ortamı
    subgraph Environment ["Lab & Simulations"]
        direction TB
        L["labs/<br/>(Vulnerable Targets)"]:::lab
        S["simulations/<br/>(Attack Generator)"]:::lab
    end

    %% Orta Kısım: Ana Motor
    subgraph Engine ["⚙️ PurpleForge Detection Engine"]
        direction LR
        P["parsers/<br/>(Normalization)"]:::component
        CORE{"core/<br/>(Orchestration)"}:::core
        D["detector/<br/>(Rule Matching)"]:::component
        
        C["configs/<br/>(Settings)"]:::config
        M["mapping/<br/>(MITRE ATT&CK)"]:::config
        
        P -->|Parsed Data| CORE
        C -.->|Loads| CORE
        CORE -->|Evaluates| D
        M -.->|Context| D
    end

    %% Sağ Kısım: Çıktı
    ST["state/<br/>(Alerts & Storage)"]:::storage

    %% Ana Bağlantılar
    L -->|Raw Logs| P
    S -->|Telemetry| P
    D -->|Detection Hits| ST
```
