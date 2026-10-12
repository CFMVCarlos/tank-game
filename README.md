# Tank Game

[![CI](https://github.com/CFMVCarlos/tank-game/actions/workflows/ci.yml/badge.svg)](https://github.com/CFMVCarlos/tank-game/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.13%20%7C%20uv-blue.svg)](https://docs.astral.sh/uv/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

A lightweight 2-player arcade tank battle game built with Pygame, featuring responsive 2D physics, particle effects, and optional LAN play via UDP multicast. Players navigate destructible terrain obstacles and battle each other using tactical trajectory aiming and weapon power controls.

## Quickstart

```bash
git clone https://github.com/CFMVCarlos/tank-game.git
cd tank-game
uv sync
uv run python main.py
```

## Development

| Task | Command |
| :--- | :--- |
| **Linting** | `uv run ruff check .` |
| **Docstrings** | `uv run pydoclint .` |
| **Type Checking** | `uv run basedpyright` |
| **Tests** | `uv run pytest` |

## License

This project is licensed under the terms of the [MIT License](LICENSE).
