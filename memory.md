# Project Memory: Dataset Searcher

## Overview
A Python-based CLI application to search for datasets across multiple online sources including Kaggle, HuggingFace, and OpenML.

## Features
- **Multi-source Search**: Simultaneously queries Kaggle (API), HuggingFace (API), and OpenML (API).
- **Parallel Execution**: Uses `asyncio` to perform searches concurrently for maximum speed.
- **Rich Terminal UI**: Uses `rich` for beautiful tables, progress spinners, and colored output.
- **Extensible Architecture**: Clean separation between search providers and the main application logic.

## File Structure
- `main.py`: Entry point using `typer` for CLI commands.
- `config.py`: Configuration and environment variable management.
- `models.py`: Shared data structures (Pydantic/Dataclasses).
- `searchers/`: Directory containing individual source searchers.
    - `kaggle_search.py`: Kaggle API integration.
    - `huggingface_search.py`: HuggingFace Hub API integration.
    - `openml_search.py`: OpenML API integration.
- `requirements.txt`: Project dependencies.

## Status
- [x] Base architecture and models.
- [x] Kaggle search implementation.
- [x] HuggingFace search implementation.
- [x] OpenML search implementation.
- [x] CLI Entry point with Rich UI.
- [x] Installation of dependencies.
- [x] Pushed to GitHub (https://github.com/bondeto/searching-dataset.git).
- [ ] Testing and validation.

## Next Steps
1. Verify `pip install` completion.
2. Run a test search (e.g., `python main.py search "climate change"`).
3. Add export functionality (CSV/JSON).
4. Add more sources if needed (UCI, Data.gov).
