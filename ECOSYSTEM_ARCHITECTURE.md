# MCPVots Ecosystem Architecture

```mermaid
graph TB
    subgraph "MCPVots Core Application"
        UI[Dark Theme UI]
        TM[Theme Manager]
        MI[MCP Integration]
        DS[Dashboard Service]
    end

    subgraph "MCP Server Network"
        G[GitHub MCP]
        M[Memory MCP]
        H[HuggingFace MCP] 
        S[SuperMemory MCP]
        SOL[Solana MCP]
        B[Browser Tools MCP]
    end

    subgraph "Trilogy AGI Backend"
        DSP[DSPy Service:8000]
        RL[RL Memory:8001]
        CONV[Conversation:8002]
        DS_R1[DeepSeek R1:8003]
        JEN[Jenova:8004]
        MC[Mission Control:8005]
    end

    subgraph "OWL Integration"
        OWL[OWL Framework]
        QW[Qwen3 MCP]
        PW[Playwright MCP]
        WA[WhatsApp MCP]
        AB[Airbnb MCP]
    end

    subgraph "Advanced Features"
        DGM[Darwin Gödel Machine]
        SH[Self Healing]
        AO[Autonomous Ops]
        AM[Advanced MCP Ecosystem]
    end

    UI --> TM
    UI --> MI
    UI --> DS
    
    MI --> G
    MI --> M
    MI --> H
    MI --> S
    MI --> SOL
    MI --> B
    
    MI -.-> DSP
    MI -.-> RL
    MI -.-> CONV
    MI -.-> DS_R1
    MI -.-> JEN
    MI -.-> MC
    
    OWL --> QW
    OWL --> PW
    OWL --> WA
    OWL --> AB
    
    DGM --> DSP
    DGM --> RL
    SH --> AO
    
    classDef mcpServer fill:#2563eb,stroke:#1d4ed8,color:#fff
    classDef trilogyService fill:#dc2626,stroke:#b91c1c,color:#fff
    classDef owlService fill:#16a34a,stroke:#15803d,color:#fff
    classDef advancedFeature fill:#9333ea,stroke:#7c3aed,color:#fff
    classDef coreApp fill:#ea580c,stroke:#c2410c,color:#fff
    
    class G,M,H,S,SOL,B mcpServer
    class DSP,RL,CONV,DS_R1,JEN,MC trilogyService
    class OWL,QW,PW,WA,AB owlService
    class DGM,SH,AO,AM advancedFeature
    class UI,TM,MI,DS coreApp
```

## Component Status
- 🟢 **Core Application**: Operational with advanced dark theme
- 🟡 **MCP Servers**: 7/7 configured, connections simulated
- 🔴 **Trilogy Services**: Partially operational (3/7 active)
- 🟢 **OWL Framework**: Available with multiple use cases
- 🟡 **Advanced Features**: DGM integrated, others pending
