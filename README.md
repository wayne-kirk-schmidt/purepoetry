# PurePoetry

A DevOps-style CLI for inspecting, governing, and repairing Python Poetry projects.

PurePoetry treats a Poetry project as a **system**, not a package.  
It provides deterministic, explainable commands for reading state, understanding constraints, and applying controlled fixes.

This tool is intentionally **not** a generic Poetry wrapper.

It is designed for environments where:

- correctness  
- auditability  
- repeatability  

matter more than convenience or automation magic.

---

## Justification

Poetry projects in real environments are often:

- Modified by multiple tools and humans  
- Subject to policy, security, and compliance constraints  
- Consumed by CI, CD, audits, and automation pipelines  
- Debugged long after the original intent is lost  

PurePoetry exists to make project state:

- Observable  
- Explainable  
- Governable  

without guessing or hidden behavior.

---

## Core principles

- **Deterministic**  
  No inference, guessing, or silent normalization

- **Explainable**  
  Every action can be inspected and reasoned about

- **Read-first**  
  Inspection precedes enforcement or repair

- **Registry-driven**  
  Known types, invariants, and fixes are explicit

- **CLI-first**  
  Designed for pipelines and operators, not interactive wizards

---

## Command model

PurePoetry uses a strict Subject–Verb–Object style:

```
purepoetry <verb> <object> [keypath|options]
```

Examples:

```bash
PurePoetry — governance CLI for Poetry projects

Usage:
  purepoetry <verb> <object> [keypath|options]

Help topics:
  help commands
  help commands <command>
  help registry
  help registry <item>
  help <item>

Examples:
  purepoetry help
  purepoetry help commands
  purepoetry help commands show
  purepoetry help registry
  purepoetry help registry invariants
```

---

## What it does

- Reads Poetry project state (pyproject, lock, environment)
- Exposes registered commands, objects, and rules
- Explains system invariants and constraints
- Surfaces violations in a controlled, inspectable way
- Applies explicit, registry-defined fixes when requested

---

## What it does not do

- No guessing or inference
- No automatic normalization
- No silent mutation of project files
- No “smart” behavior without explanation
- No interactive prompts or hidden state

These are intentional design decisions.

---

## Help system

Help is **layered and scoped**, not a text dump.

### Global help

```bash
purepoetry help
```

Shows:
- What PurePoetry is
- Command grammar
- Available help topics

### Command help

```bash
purepoetry help commands
```

Shows:
- Global help summary
- List of available commands with descriptions

### Registry help

```bash
purepoetry help registry
```

Explains:
- What the registry is
- What kinds of rules and types it contains
- How it is used by the system

> **Note**  
> `help` explains concepts and usage  
> `show` enumerates what exists

They are intentionally separate.

---

## Project structure

```
bin/        CLI entrypoints
lib/        Commands, registry, and core logic
cfg/        Configuration
var/        Runtime and generated artifacts
doc/        Design and reference documentation
```

See:
- `doc/STRUCTURE.md`
- `doc/DESIGN.md`
- `doc/EXAMPLES.md`

---

## Installation

PurePoetry is typically run inside a Poetry-managed environment.

```bash

poetry config virtualenvs.in-project true
poetry install
source .venv/bin/activate
```

---

## Status

Early but operational.

Behavior is stabilized first.  
Semantics are refined second.  
Polish comes last.

---

## Design philosophy

PurePoetry favors:

- Explicitness over abstraction  
- Predictability over cleverness  
- Inspection over automation  

If you are looking for a convenience wrapper around Poetry, this is probably not the right tool.

If you need a **governance-grade CLI for Poetry projects**, it likely is.

---

## License

Copyright 2026  

**Wayne Kirk Schmidt**  
wayne.kirk.schmidt@gmail.com  

Licensed under the Apache 2.0 License.  
https://www.apache.org/licenses/LICENSE-2.0

---

## Support

Best-effort support is provided via e-mail:

+ wayne.kirk.schmidt@gmail.com
