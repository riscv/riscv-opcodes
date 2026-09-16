# Reproducible container for riscv-opcodes artifact generation
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /workspace

# Keep the image small while providing the native tools used by the project.
RUN apt-get update \
    && apt-get install --no-install-recommends -y make g++ git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
COPY extensions ./extensions
COPY arg_lut.csv causes.csv csrs.csv csrs32.csv encoding.h ./

RUN python -m pip install --no-cache-dir .

# Generate the same machine-readable artifacts as the project Makefile workflow.
ENTRYPOINT ["riscv_opcodes"]
CMD ["-pseudo", "-c", "-go", "-chisel", "-sverilog", "-rust", "-latex", "rv*", "unratified/rv*"]
