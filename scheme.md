graph TD
    subgraph "Lab & Simulation Environment"
        L[labs/ <br> Vulnerable Targets]
        S[simulations/ <br> Attack Generator]
    end

    L --> T(Raw Telemetry / Logs)
    S --> T

    subgraph "PurpleForge Detection Engine"
        C[configs/ <br> Settings] --> CORE
        
        T --> P[parsers/ <br> Normalization]
        P --> CORE[core/ <br> Orchestration Logic]
        CORE --> D[detector/ <br> Rule Matching]
        
        M[mapping/ <br> MITRE ATT&CK Context] --> D
    end
    
    D -- "Detection Hits" --> ST[state/ <br> Alerts & Storage]

    style CORE fill:#5D3F6B,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#5D3F6B,stroke:#fff,stroke-width:2px,color:#fff
    style P fill:#4A3055,stroke:#fff,color:#fff
    style ST fill:#8E24AA,stroke:#fff,color:#fff,shape:cyl
