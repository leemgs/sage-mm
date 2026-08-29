#!/usr/bin/env bash
set -euo pipefail
DOTNET_EnableEventPipe=1 dotnet run --project src/SageMM.Demo -- "$@"
