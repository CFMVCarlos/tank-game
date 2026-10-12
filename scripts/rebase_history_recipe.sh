#!/usr/bin/env bash
# ==============================================================================
# Git History Conventional Commit Rewriter Recipe
# Generated as part of Prompt 4 (Git Audit & Rebase Recipe)
#
# NOTE: Executing this script will rewrite commit hashes on branch 'main'.
# Run only if you explicitly choose to rewrite public commit history.
# ==============================================================================

set -euo pipefail

cat << 'EOF'
To rewrite non-conforming commit messages on main to follow Conventional Commits:

Method 1: Interactive Rebase
----------------------------
Run:
    git checkout main
    git rebase -i --root

In the editor, mark non-conforming commits with 'reword' ('r'):
- 458e7f1 -> feat(init): initial commit of tank game prototype
- a973fd0 -> feat(movement): implement tank rectangular motion
- 66bf19c -> feat(combat): implement projectile shooting and oop structure
- 4038013 -> feat(assets): add tank sprites and visual assets
- 5984676 -> refactor(fsm): introduce finite state machine and command pattern
- 2a5aafa -> feat(physics): add boundary and obstacle collision detection
- 8704ddf -> style(types): clean code comments and annotate return types
- 175a6fa -> feat(hud): add player health bar and damage calculation
- 64d7978 -> feat(effects): add frame animations
- c1e5094 -> fix(physics): adjust bullet bounding box for accurate hit detection
- cae3e24 -> docs(code): add function docstrings and explanatory comments
- 7f2b07f -> style(sprites): correct sprite orientations and assign player names
- e541404 -> feat(multiplayer): add basic two player network support
- 4b9c40c -> feat(network): enable lan multiplayer via udp multicast
- fd66552 -> chore(cleanup): remove legacy code and polish files
- 471a4a3 -> docs(readme): initial readme documentation
- b0d35b0 -> docs(readme): update initial readme overview
- af86240 -> fix(fsm): remove duplicate state class definition
- 2962583 -> docs(presentation): add game demo presentation materials
- 250ead1 -> perf(math): optimize distance calculation using math.dist
- 7f0accb -> perf(math): optimize distance calculation using math.dist
- 72ac950 -> chore(build): configure modern tooling and dependencies with uv and python 3.13
- 22265ec -> refactor(engine): modernize architecture into tank_game package with arcade polish
- 38153d7 -> feat(ui): add interactive start screen and fix responsive controls

Method 2: Non-interactive Git-Filter-Repo
-----------------------------------------
Install git-filter-repo:
    uvx git-filter-repo --version

Create message callback map and execute:
    git-filter-repo --message-callback '
commit_map = {
    b"Initial commit": b"feat(init): initial commit of tank game prototype",
    b"Moving rectangles": b"feat(movement): implement tank rectangular motion",
    b"Shooting Tanks with some OOP": b"feat(combat): implement projectile shooting and oop structure",
    b"Sprites and assets": b"feat(assets): add tank sprites and visual assets",
    b"FSM and Command Pattern": b"refactor(fsm): introduce finite state machine and command pattern",
    b"Collisions": b"feat(physics): add boundary and obstacle collision detection",
    b"Pretty comments and return types": b"style(types): clean code comments and annotate return types",
    b"Health bar and damage calculation": b"feat(hud): add player health bar and damage calculation",
    b"Animations": b"feat(effects): add frame animations",
    b"Bullet size corrected to better collision detection": b"fix(physics): adjust bullet bounding box for accurate hit detection",
    b"Function descriptions and comments": b"docs(code): add function docstrings and explanatory comments",
    b"Sprite correction and tank names": b"style(sprites): correct sprite orientations and assign player names",
    b"Simple multiplayer": b"feat(multiplayer): add basic two player network support",
    b"LAN Gaming added": b"feat(network): enable lan multiplayer via udp multicast",
    b"Last Clean up": b"chore(cleanup): remove legacy code and polish files",
    b"First version of ReadMe": b"docs(readme): initial readme documentation",
    b"First version of the readme": b"docs(readme): update initial readme overview",
    b"State class was duplicated": b"fix(fsm): remove duplicate state class definition",
    b"Presentation commit": b"docs(presentation): add game demo presentation materials",
}
for old_msg, new_msg in commit_map.items():
    if message.startswith(old_msg):
        return new_msg + b"\n"
return message
'
EOF
