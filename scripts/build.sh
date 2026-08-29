#!/usr/bin/env bash
set -euo pipefail
make -C native/peflush
dotnet build src/SageMM.Core
dotnet build src/SageMM.Demo
dotnet build src/RoslynAnalyzer
dotnet test tests/SageMM.Core.Tests
python3 scripts/validate_expected_results.py
python3 scripts/generate_simulated_results.py --check
