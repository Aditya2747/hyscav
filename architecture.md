# HySCAV Hybrid Smart Contract Analyzer - Architecture Overview

## 1. System Overview

HySCAV is a hybrid smart contract vulnerability analysis framework that combines static analysis, symbolic execution, and fuzzing techniques with machine learning-driven decision making. The system is designed for dissertation-level research in smart contract security analysis.

## 2. Core Architecture Components

### 2.1 Pipeline Orchestrator (`main.py`)
- **Purpose**: Central coordinator for the entire analysis pipeline
- **Responsibilities**:
  - Input validation and preprocessing
  - Sequential execution of analysis stages
  - Error handling and logging
  - Result aggregation and reporting

### 2.2 Analysis Tools Layer (`analyzers/`)
- **Slither Runner** (`slither_runner.py`): Static analysis engine
  - Executes Slither static analyzer
  - Parses and simplifies output
  - Extracts vulnerability patterns
- **Mythril Runner** (`mythril_runner.py`): Symbolic execution engine
  - Performs symbolic analysis
  - Detects complex vulnerabilities
  - Handles timeout and resource management
- **Echidna Runner** (`echidna_runner.py`): Fuzzing engine
  - Property-based testing
  - Mutation-based fuzzing
  - Coverage-guided exploration

### 2.3 Controller Layer (`controller/`)
- **Feature Extractor** (`feature_extractor.py`): Data preprocessing
  - Extracts numerical features from analysis results
  - Normalizes and structures data for ML models
  - Handles missing data and edge cases
- **Decision Engine** (`decision_engine.py`): Intelligent tool selection
  - ML-based decision making
  - Configurable risk thresholds
  - Dynamic analysis depth adjustment
- **Merger** (`merger.py`): Result consolidation
  - Deduplicates findings across tools
  - Merges overlapping vulnerabilities
  - Prioritizes issues by severity

### 2.4 Machine Learning Layer (`ml/`)
- **Risk Model** (`risk_model.py`): Predictive analytics
  - Risk scoring and classification
  - Feature importance analysis
  - Model training and evaluation interfaces

### 2.5 Reporting Layer (`reports/`)
- **Report Generator** (`report_generator.py`): Output formatting
  - JSON-structured reports
  - Statistical summaries
  - Visualization data export

## 3. Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Smart Contract│───▶│  Static Analysis │───▶│ Feature Extraction│
│     (.sol)      │    │    (Slither)     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Risk Scoring  │◀───│   ML Model       │    │ Decision Engine │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Deep Analysis   │    │   Tool Selection │    │   Result Merge  │
│ (Mythril/Echidna│◀───│                  │───▶│                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐
│   Final Report  │
│                 │
└─────────────────┘
```

## 4. Architectural Patterns

### 4.1 Modular Design
- **Separation of Concerns**: Each component has a single responsibility
- **Dependency Injection**: Loose coupling between modules
- **Interface Abstraction**: Standardized data formats between layers

### 4.2 Pipeline Pattern
- **Sequential Processing**: Linear flow with conditional branching
- **Data Transformation**: Progressive refinement of analysis results
- **Error Propagation**: Comprehensive error handling at each stage

### 4.3 Strategy Pattern (Decision Engine)
- **Pluggable Algorithms**: Interchangeable decision-making strategies
- **Configuration-Driven**: Thresholds and rules defined externally
- **Extensible Design**: Easy addition of new decision criteria

## 5. Quality Attributes

### 5.1 Performance
- **Parallel Execution**: Concurrent tool execution where possible
- **Resource Management**: Timeout handling and memory limits
- **Caching**: Result caching for repeated analyses

### 5.2 Reliability
- **Error Recovery**: Graceful handling of tool failures
- **Data Validation**: Input sanitization and format checking
- **Logging**: Comprehensive audit trails

### 5.3 Maintainability
- **Type Hints**: Full type annotation coverage
- **Documentation**: Detailed docstrings and API docs
- **Testing**: Comprehensive unit and integration test suites

### 5.4 Security
- **Secure Execution**: Sandboxed tool execution
- **Input Validation**: Protection against malicious inputs
- **Output Sanitization**: Safe handling of analysis results

## 6. Deployment Architecture

### 6.1 Development Environment
- **Local Execution**: Direct Python execution
- **Docker Containerization**: Isolated runtime environment
- **Configuration Management**: Environment-specific settings

### 6.2 CI/CD Pipeline
- **Automated Testing**: Unit, integration, and performance tests
- **Code Quality Checks**: Linting, type checking, coverage analysis
- **Artifact Generation**: Docker images and documentation

## 7. Extension Points

### 7.1 Tool Integration
- **Plugin Architecture**: Easy addition of new analysis tools
- **Standardized Interfaces**: Common data formats and APIs
- **Configuration Registry**: Tool capabilities and requirements

### 7.2 ML Model Enhancement
- **Model Interchangeability**: Support for different ML frameworks
- **Feature Engineering**: Extensible feature extraction pipelines
- **Hyperparameter Tuning**: Automated model optimization

### 7.3 Reporting Customization
- **Template System**: Configurable report formats
- **Export Formats**: Multiple output formats (JSON, PDF, HTML)
- **Visualization Integration**: Charts and graphs for results

## 8. Dissertation Research Integration

### 8.1 Experiment Tracking
- **Reproducible Runs**: Versioned configurations and results
- **Statistical Analysis**: Performance metrics and significance testing
- **Comparative Studies**: Benchmarking against other tools

### 8.2 Evaluation Framework
- **Ground Truth Datasets**: Labeled vulnerability datasets
- **Metrics Calculation**: Precision, recall, F1-score computation
- **Result Visualization**: Charts and statistical summaries

This architecture provides a solid foundation for dissertation-level research in hybrid smart contract analysis, with clear separation of concerns, extensibility, and comprehensive quality attributes.
