# P3IF - Patterns, Processes, Perspectives Inter-Framework (P3IF)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

P3IF is a sophisticated framework for integrating and visualizing complex data relationships across multiple domains. It provides a flexible, interoperable approach to requirements engineering that bridges gaps between existing methodologies and fosters cross-domain collaboration.

## Architecture Overview

```mermaid
graph TD
    User[User/Client] --> Portal[Web Portal]
    Portal --> |Requests| API[P3IF API Layer]
    
    subgraph "P3IF Core"
        API --> Core[Core Framework]
        Core --> Models[Domain Models]
        Core --> Relationships[Relationship Engine]
        Core --> Analysis[Analysis Tools]
    end
    
    subgraph "Data Layer"
        Models --> Domains[(Domain Repositories)]
        Relationships --> RelationDB[(Relationship Database)]
    end
    
    subgraph "Visualization Layer"
        API --> Viz[Visualization Engine]
        Viz --> Cube[3D Cube Visualization]
        Viz --> Network[Network Graph]
        Viz --> Dashboard[Analytics Dashboard]
        Viz --> Matrix[Matrix View]
    end
    
    style Core fill:#f9f,stroke:#333,stroke-width:2px
    style Viz fill:#bbf,stroke:#333,stroke-width:2px
    style User fill:#dfd,stroke:#333,stroke-width:2px
```

## P3IF Conceptual Model

```mermaid
graph TD
    subgraph "P3IF Domain"
        P[Properties]
        P2[Processes]
        P3[Perspectives]
        
        P <--> |Relationship| P2
        P2 <--> |Relationship| P3
        P3 <--> |Relationship| P
        
        P <--> |Strength/Confidence| P2
        P2 <--> |Strength/Confidence| P3
        P3 <--> |Strength/Confidence| P
    end
    
    subgraph "Multi-Domain Integration"
        D1[Domain 1]
        D2[Domain 2]
        D3[Domain N]
        
        D1 --- D2
        D2 --- D3
        D3 --- D1
        
        D1 --> P
        D2 --> P
        D3 --> P
        D1 --> P2
        D2 --> P2
        D3 --> P2
        D1 --> P3
        D2 --> P3
        D3 --> P3
    end
    
    style P fill:#f96,stroke:#333,stroke-width:2px
    style P2 fill:#9f6,stroke:#333,stroke-width:2px
    style P3 fill:#69f,stroke:#333,stroke-width:2px
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Scripts
    participant Framework
    participant Visualization
    
    User->>Scripts: Execute script
    Scripts->>Framework: Load domain data
    Framework->>Framework: Process relationships
    Framework->>Visualization: Generate visualization
    Visualization->>User: Display interactive view
    
    User->>Visualization: Interact (rotate, zoom, filter)
    Visualization->>Framework: Query relationships
    Framework->>Visualization: Return filtered data
    Visualization->>User: Update view
```

## Features

- **Multi-domain Integration**: Connect and analyze data across multiple domains
- **Flexible Visualization**: Explore data through network diagrams, matrices, 3D cubes, and dashboards
- **Interactive Portal**: Web-based interactive portal for exploring relationships
- **Cross-domain Analysis**: Discover patterns and relationships that span different domains
- **Extensible Architecture**: Easily add new domains, visualization types, and analysis methods
- **Category Theory Foundation**: Rigorous mathematical foundation for framework operations
- **Cognitive Security Support**: Enhanced decision-making integrity and security

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/p3if.git
cd p3if

# Generate a visualization portal
python3 scripts/run_multidomain_portal.py --output-dir output

# Generate the 3D cube visualization
python3 scripts/test_3d_cube_with_domains.py

# Open the 3D visualization
python3 scripts/view_p3if_website.py

# Generate all visualizations
bash scripts/generate_visualizations.sh

# Open the visualization portal
open output/index.html
```

## Documentation

For comprehensive documentation, see the [docs](docs/README.md) directory:

- [Getting Started Guide](docs/guides/getting-started.md)
- [Technical Documentation](docs/technical)
- [API Reference](docs/api/README.md)
- [Tutorials](docs/tutorials)
- [Concepts and Theory](docs/concepts)
- [3D Visualization](docs/visualization/README.md)

## LLM & AI Development Resources

P3IF includes resources to assist LLMs and autonomous agents with development:

- [LLM Development Guide](docs/LLM_DEVELOPMENT_GUIDE.md) - Comprehensive guide for AI working on P3IF
- [AI Prompt Library](docs/AI_PROMPT_LIBRARY.md) - Collection of prompts for generating P3IF-compatible code
- [Project Rules](.cursorrules) - Structured rules for code organization and standards

These resources help ensure code quality, consistency, and adherence to P3IF architectural patterns.

## Project Structure

```mermaid
graph TD
    p3if[p3if/] --> api[api/]
    p3if --> core[core/]
    p3if --> data[data/]
    p3if --> analysis[analysis/]
    p3if --> visualization[visualization/]
    p3if --> utils[utils/]
    p3if --> scripts[scripts/]
    
    scripts --> s1[run_multidomain_portal.py]
    scripts --> s2[test_3d_cube_with_domains.py]
    scripts --> s3[update_domain_files.py]
    scripts --> s4[view_p3if_website.py]
    scripts --> s5[generate_visualizations.sh]
    
    docs[docs/] --> d1[api/]
    docs --> d2[concepts/]
    docs --> d3[guides/]
    docs --> d4[technical/]
    docs --> d5[examples/]
    docs --> d6[diagrams/]
    docs --> d7[visualization/]
    docs --> d8[LLM_DEVELOPMENT_GUIDE.md]
    docs --> d9[AI_PROMPT_LIBRARY.md]
    
    tests[tests/] --> t1[core/]
    tests --> t2[api/]
    tests --> t3[data/]
    tests --> t4[analysis/]
    tests --> t5[visualization/]
    tests --> t6[utils/]
    
    style p3if fill:#f96,stroke:#333,stroke-width:2px
    style docs fill:#9f6,stroke:#333,stroke-width:2px
    style tests fill:#69f,stroke:#333,stroke-width:2px
```

## Core Components Relationships

```mermaid
classDiagram
    class P3IFFramework {
        +add_pattern(pattern)
        +add_relationship(relationship)
        +get_patterns()
        +get_relationships()
        +analyze()
    }
    
    class Pattern {
        +id: str
        +name: str
        +domain: str
        +type: PatternType
        +metadata: Dict
    }
    
    class Property {
        +type = PatternType.PROPERTY
    }
    
    class Process {
        +type = PatternType.PROCESS
    }
    
    class Perspective {
        +type = PatternType.PERSPECTIVE
    }
    
    class Relationship {
        +id: str
        +property_id: str
        +process_id: str
        +perspective_id: str
        +strength: float
        +confidence: float
    }
    
    class Visualizer {
        +generate_visualization()
    }
    
    class InteractiveVisualizer {
        +generate_3d_cube_html()
        +generate_network_graph()
        +generate_matrix_view()
    }
    
    Pattern <|-- Property
    Pattern <|-- Process
    Pattern <|-- Perspective
    
    P3IFFramework --> "0..*" Pattern : contains
    P3IFFramework --> "0..*" Relationship : contains
    
    Visualizer <|-- InteractiveVisualizer
    Visualizer --> P3IFFramework : uses
```

## Visualizations

### 3D Cube Visualization

The P3IF framework includes an interactive 3D cube visualization that represents the three dimensions of the framework (properties, processes, and perspectives) across 16 different domains. This visualization allows users to explore relationships between elements from each dimension.

```mermaid
graph TD
    subgraph "3D Cube Visualization"
        Prop[Properties Axis]
        Proc[Processes Axis]
        Persp[Perspectives Axis]
        Rel[Relationship Points]
        
        Prop --- Rel
        Proc --- Rel
        Persp --- Rel
        
        Rel --> Size[Point Size = Strength]
        Rel --> Color[Point Color = Confidence]
    end
    
    Domain[Domain Selector] --> |Updates| Prop
    Domain --> |Updates| Proc
    Domain --> |Updates| Persp
    
    User[User Interaction] --> |Rotate| Cube[3D Visualization]
    User --> |Zoom| Cube
    User --> |Pan| Cube
    User --> |Select| Cube
    
    style Prop fill:#f96,stroke:#333,stroke-width:2px
    style Proc fill:#9f6,stroke:#333,stroke-width:2px
    style Persp fill:#69f,stroke:#333,stroke-width:2px
    style Rel fill:#f9f,stroke:#333,stroke-width:2px
```

To generate and view the 3D visualization:

```bash
# Generate the 3D visualization
python3 scripts/test_3d_cube_with_domains.py

# Open the visualization in your browser
python3 scripts/view_p3if_website.py
```

For more information about the 3D visualization, see the [visualization documentation](docs/visualization/README.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to P3IF.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Technical Architecture Details

### Pattern Type Hierarchy

```mermaid
graph TD
    Pattern[Pattern Base Class] --> Property[Property]
    Pattern --> Process[Process]
    Pattern --> Perspective[Perspective]
    
    Property --> Domain1Property[Domain 1 Properties]
    Property --> Domain2Property[Domain 2 Properties]
    Property --> DomainNProperty[Domain N Properties]
    
    Process --> Domain1Process[Domain 1 Processes]
    Process --> Domain2Process[Domain 2 Processes]
    Process --> DomainNProcess[Domain N Processes]
    
    Perspective --> Domain1Perspective[Domain 1 Perspectives]
    Perspective --> Domain2Perspective[Domain 2 Perspectives]
    Perspective --> DomainNPerspective[Domain N Perspectives]
    
    style Pattern fill:#f9f,stroke:#333,stroke-width:2px
    style Property fill:#f96,stroke:#333,stroke-width:2px
    style Process fill:#9f6,stroke:#333,stroke-width:2px
    style Perspective fill:#69f,stroke:#333,stroke-width:2px
```

### Data Model

```mermaid
erDiagram
    PATTERN {
        string id PK
        string name
        string domain
        enum type
        json metadata
        datetime created_at
        datetime updated_at
    }
    
    PROPERTY {
        string id PK
        string name
        string domain
        json attributes
    }
    
    PROCESS {
        string id PK
        string name
        string domain
        json steps
        json inputs
        json outputs
    }
    
    PERSPECTIVE {
        string id PK
        string name
        string domain
        json viewpoint
        json constraints
    }
    
    RELATIONSHIP {
        string id PK
        string property_id FK
        string process_id FK
        string perspective_id FK
        float strength
        float confidence
        json context
        datetime created_at
    }
    
    DOMAIN {
        string id PK
        string name
        string description
        json metadata
    }
    
    PATTERN ||--o{ RELATIONSHIP : "participates in"
    PROPERTY ||--o{ RELATIONSHIP : "connects to"
    PROCESS ||--o{ RELATIONSHIP : "connects to"
    PERSPECTIVE ||--o{ RELATIONSHIP : "connects to"
    DOMAIN ||--o{ PATTERN : "contains"
```

### Analysis Pipeline

```mermaid
flowchart TD
    input[Domain Data Input] --> load[Load Domain Data]
    load --> extract[Extract Patterns]
    extract --> identify[Identify Relationships]
    identify --> calculate[Calculate Metrics]
    calculate --> analyze[Analyze Network Properties]
    analyze --> cluster[Cluster Similar Patterns]
    cluster --> discover[Discover Cross-Domain Patterns]
    discover --> visualize[Generate Visualizations]
    visualize --> export[Export Results]
    
    subgraph "Data Processing"
        load
        extract
        identify
    end
    
    subgraph "Analysis"
        calculate
        analyze
        cluster
        discover
    end
    
    subgraph "Output"
        visualize
        export
    end
    
    style Data Processing fill:#f96,stroke:#333,stroke-width:2px
    style Analysis fill:#9f6,stroke:#333,stroke-width:2px
    style Output fill:#69f,stroke:#333,stroke-width:2px
```

### Visualization Components

```mermaid
graph TD
    subgraph "Visualization Components"
        Base[Base Visualizer]
        Dashboard[Dashboard Generator]
        Interactive[Interactive Visualizer]
        Portal[Visualization Portal]
        
        Base --> Dashboard
        Base --> Interactive
        Dashboard --> Portal
        Interactive --> Portal
    end
    
    subgraph "Dashboard Components"
        Dashboard --> Overview[Overview Dashboard]
        Dashboard --> Domain[Domain Dashboard]
        Dashboard --> Compare[Comparative Dashboard]
        Dashboard --> Custom[Custom Dashboard]
    end
    
    subgraph "Interactive Components"
        Interactive --> Cube[3D Cube]
        Interactive --> Network[Network Graph]
        Interactive --> ForceDirected[Force-Directed Graph]
        Interactive --> Timeline[Timeline View]
    end
    
    subgraph "Portal Features"
        Portal --> Filters[Interactive Filters]
        Portal --> DataSelect[Dataset Selector]
        Portal --> ComponentSelect[Component Selector]
        Portal --> Export[Export Functionality]
        Portal --> Responsive[Responsive Design]
    end
    
    style Base fill:#f9f,stroke:#333,stroke-width:2px
    style Dashboard fill:#f96,stroke:#333,stroke-width:2px
    style Interactive fill:#9f6,stroke:#333,stroke-width:2px
    style Portal fill:#69f,stroke:#333,stroke-width:2px
```

## Acknowledgments

- The P3IF framework builds on concepts from category theory, cognitive security, and requirements engineering
- Special thanks to all contributors who have helped shape and improve this framework
