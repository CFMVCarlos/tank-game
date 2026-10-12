# Tank Game

[![CI](https://github.com/CFMVCarlos/tank-game/actions/workflows/ci.yml/badge.svg)](https://github.com/CFMVCarlos/tank-game/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![uv](https://img.shields.io/badge/tooling-uv-261230.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

A lightweight 2-player arcade tank battle game built with Pygame, featuring responsive 2D physics, particle effects, and optional LAN multiplayer over UDP multicast. Players navigate destructible terrain obstacles and battle each other using tactical trajectory aiming and weapon power controls.

## Quickstart

Clone the repository, synchronize the environment with `uv`, and run the launcher:

```bash
git clone https://github.com/CFMVCarlos/tank-game.git
cd tank-game
uv sync
uv run python main.py
```

*Alternatively, execute the installed package entrypoint directly:*

```bash
uv run tank-game
```

## Development

All linting, docstring verification, static typing, and test execution are managed with `uv`:

| Task | Command |
| :--- | :--- |
| **Lint & Style** | `uv run ruff check .` |
| **Code Formatting** | `uv run ruff format --check .` |
| **Docstrings (NumPy)** | `uv run pydoclint .` |
| **Type Checking** | `uv run basedpyright` |
| **Alternative Type Check** | `uv run ty check` |
| **Test Suite** | `uv run pytest` |
| **All Checks** | `uv run ruff check . && uv run pydoclint . && uv run basedpyright && uv run pytest` |

To enable automatic commit linting with gitlint:

```bash
git config core.hooksPath .githooks
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
