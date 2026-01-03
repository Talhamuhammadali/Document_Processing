# Document Processing

Exploring tools to create enriched document chunks with metadata for efficient downstream RAG (Retrieval-Augmented Generation) processes.

## Overview

This project focuses on:
- Processing documents into semantically meaningful chunks
- Adding metadata to enhance retrieval accuracy
- Optimizing document representations for RAG workflows

## Tech Stack

- **Python**: 3.14+
- **Document Processing**: [Docling](https://github.com/DS4SD/docling)
- **Audio Processing**: PyTorch Audio
- **Code Quality**: Ruff (linting & formatting), Mypy (type checking), Codespell

## Setup

### Prerequisites

- Python 3.14 or higher
- [UV](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd document-processing
```

2. Install dependencies:
```bash
uv sync --all-groups
```

Or for production only:
```bash
uv sync
```

## Development

### Running the Application

```bash
uv run python main.py
```

### Code Quality

**Lint code:**
```bash
uv run ruff check .
uv run ruff check . --fix  # Auto-fix issues
```

**Format code:**
```bash
uv run ruff format .
```

**Type checking:**
```bash
uv run mypy .
```

**Spell checking:**
```bash
uv run codespell .
```

## Project Structure

```
document-processing/
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
├── README.md           # This file
└── SETUP_GUIDE.md      # Detailed setup instructions
```

## Contributing

This is an exploratory project. Contributions and suggestions are welcome!

## License

[Add your license here]