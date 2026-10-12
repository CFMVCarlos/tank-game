# Tank Game

A lightweight, arcade-polished 2-player tank battle game built with Python 3.13 and Pygame, featuring ballistic aim guides, particle burst effects, zero-allocation asset caching, and secure UDP multicast LAN play.

## Table of Contents

- [Tank Game](#tank-game)
  - [Table of Contents](#table-of-contents)
  - [Features & Visual Polish](#features--visual-polish)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Using uv](#using-uv)
  - [Usage](#usage)
    - [Running the Game](#running-the-game)
    - [Game Setup](#game-setup)
  - [Controls](#controls)
  - [Project Architecture](#project-architecture)
  - [Quality & Verification](#quality--verification)
  - [Networking](#networking)
  - [License](#license)
  - [Credits](#credits)

## Features & Visual Polish

- 💥 **Particle Effects Engine**: Dynamic spark trails and radial explosion particle bursts on projectile impact.
- 🎯 **Ballistic Aiming Arc**: Visual segmented trajectory prediction previewing shot angles and velocity.
- 🚀 **Zero-Disk-I/O Asset Cache**: All sprites, damage stages, and sound effects are preloaded into memory once, eliminating 60 FPS disk thrashing.
- 🛡️ **Secure LAN Multiplayer**: Replaced legacy pickle serialization with hardened JSON payloads over UDP multicast.
- 🎮 **Arcade HUD**: Styled health bars, active player turn banners, and real-time power/angle gauges.
- 🧪 **Full Test & Lint Suite**: 100% passing tests with pytest, Ruff, pydoclint (NumPy docstrings), and ty type checking.

## Installation

### Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/) package manager

### Using uv

```bash
uv sync
```

## Usage

### Running the Game

Launch using `uv`:

```bash
uv run main.py
```

Or execute as a module:

```bash
uv run python -m tank_game
```

### Game Setup

- Enter player name (press Enter for default `Tank 1`).
- Choose game mode: `0` for Local hotseat (single machine), `1` for LAN multiplayer.

## Controls

| Action | Player 1 | Player 2 |
| :--- | :---: | :---: |
| **Move Left / Right** | <kbd>A</kbd> / <kbd>D</kbd> | <kbd>J</kbd> / <kbd>L</kbd> |
| **Aim Angle Left / Right** | <kbd>Q</kbd> / <kbd>E</kbd> | <kbd>U</kbd> / <kbd>O</kbd> |
| **Power Down / Up** | <kbd>S</kbd> / <kbd>W</kbd> | <kbd>K</kbd> / <kbd>I</kbd> |
| **Fire Projectile** | <kbd>SPACE</kbd> | <kbd>SPACE</kbd> |
| **Quit Game** | <kbd>ESC</kbd> | <kbd>ESC</kbd> |

## Project Architecture

```text
tank-game/
├── main.py                     # Root CLI launcher entrypoint
├── tank_game/                  # Core game package
│   ├── __init__.py             # Public package exports
│   ├── bullet.py               # Ballistic physics and bullet entity
│   ├── colors.py               # Standardized RGBA/RGB palette constants
│   ├── fsm.py                  # Finite State Machine governing entity states
│   ├── game.py                 # Main game loop, HUD, trajectory guide, and collision
│   ├── input_handler.py        # Command pattern input mapping
│   ├── network.py              # Secure UDP multicast transceiver with JSON encoding
│   ├── particles.py            # Physics particle engine for sparks and debris
│   ├── sprites.py              # In-memory AssetCache, TankSprite, BulletSprite, TerrainSprite
│   ├── tank.py                 # Tank entity, controls, damage calculations, TankSpawner
│   └── terrain.py              # Terrain surface boundaries and properties
├── tests/                      # Automated test suite
│   ├── test_bullet.py
│   ├── test_fsm.py
│   ├── test_input_handler.py
│   ├── test_particles.py
│   ├── test_tank.py
│   └── test_terrain.py
├── images/                     # Sprite assets and sound files
├── pyproject.toml              # Build metadata and tool configuration
└── README.md
```

## Quality & Verification

Run the complete test and linting pipeline:

```bash
# Run unit test suite
uv run pytest

# Check linter rules
uv run ruff check

# Verify NumPy docstring compliance
uv run pydoclint .

# Run Astral type checker
uv run ty check
```

## Networking

LAN play uses UDP multicast for player discovery and lightweight state synchronization. Both players must be on the same local subnet with UDP multicast traffic permitted.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Credits

Created by Carlos Valente. Modernized with clean architecture, zero-allocation asset caching, and arcade visuals.
