#!/usr/bin/env bash
set -euo pipefail
make -C native/peflush
dotnet build src/SageMM.Core
dotnet build src/SageMM.Demo
dotnet build src/RoslynAnalyzer
dotnet test tests/SageMM.Core.Tests
