#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
purepoetry.commands.help

Help is intentionally **navigational** and **deterministic**.

Contract (high-level):
  - Every help response shares the same frame (look & feel)
  - Detailed help appends one scoped section after the frame
  - Invalid help appends an error section after the frame

No filesystem side effects.
"""

from __future__ import annotations

import sys
import logging

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from lib.registry.invariants import clumps

sys.dont_write_bytecode = True

# Registry categories are conceptual groupings (not a dump).
_REGISTRY_CATEGORIES: Tuple[str, ...] = ("types", "invariants", "fixes")

# One-line descriptions for known verbs.
_VERB_SUMMARY: Dict[str, str] = {
    "show": "Display configuration or rule domains (read-only)",
    "edit": "Modify keys and values in configuration safely",
    "test": "Evaluate project against invariant rules",
    "list": "Modify lists in configuration files",
    "help": "Show help",
}


@dataclass(frozen=True)
class HelpRequest:
    """ basic definition of the HelpRequest. no methods but data structure """
    topic: Optional[str]
    subtopic: Optional[str]


def _logger() -> logging.Logger:
    return logging.getLogger("purepoetry")


def _frame(logger: logging.Logger) -> None:
    logger.info("PurePoetry — governance CLI for Poetry projects")
    logger.info("")
    logger.info("Usage:")
    logger.info("  purepoetry <verb> <object> [keypath|options]")
    logger.info("")


def _separator(logger: logging.Logger) -> None:
    logger.info("-" * 56)


def _error_block(logger: logging.Logger, message: str) -> None:
    _separator(logger)
    logger.error("Error:")
    logger.error(f"  {message}")
    logger.info("")
    logger.info("Try:")
    logger.info("  purepoetry help")
    logger.info("  purepoetry help commands")
    logger.info("  purepoetry help registry")


def _topic_block_main(logger: logging.Logger) -> None:
    logger.info("Help topics:")
    logger.info("  help commands")
    logger.info("  help commands <command>")
    logger.info("  help registry")
    logger.info("  help registry <item>")
    logger.info("  help <item>")
    logger.info("")
    logger.info("Examples:")
    logger.info("  purepoetry help")
    logger.info("  purepoetry help commands")
    logger.info("  purepoetry help commands show")
    logger.info("  purepoetry help registry")
    logger.info("  purepoetry help registry invariants")


def _topic_block_commands(logger: logging.Logger, registry: Dict[str, str]) -> None:
    logger.info("Commands define what action PurePoetry will perform.")
    logger.info("")
    logger.info("Available commands:")
    for verb in sorted(registry.keys()):
        desc = _VERB_SUMMARY.get(verb, "Command")
        logger.info(f"  {verb:6} {desc}")
    logger.info("")
    logger.info("For details:")
    logger.info("  purepoetry help commands <command>")


def _topic_block_command(logger: logging.Logger, verb: str) -> None:
    logger.info(f"Command: {verb}")
    logger.info("")

    if verb == "show":
        logger.info("Purpose:")
        logger.info("  Display deterministic views of defined domains.")
        logger.info("")
        logger.info("Domains:")
        logger.info("  config   Project configuration (pyproject.toml)")
        logger.info("  rules    Registered invariant rules")
        logger.info("")
        logger.info("Usage:")
        logger.info("  purepoetry show config")
        logger.info("  purepoetry show config <string>")
        logger.info("  purepoetry show config <dotted.path>")
        logger.info("")
        logger.info("  purepoetry show rules")
        logger.info("  purepoetry show rules <string>")
        logger.info("  purepoetry show rules <rule-id>")
        logger.info("")
        logger.info("Examples:")
        logger.info("  purepoetry show config")
        logger.info("  purepoetry show config project.dependencies")
        logger.info("  purepoetry show rules")
        logger.info("  purepoetry show rules PKG-002")
        return

    if verb == "list":
        logger.info("Purpose:")
        logger.info("  Modify configuration values while respecting arrays.")
        logger.info("")
        logger.info("Usage:")
        logger.info("  purepoetry list")
        logger.info("  purepoetry list show <dotted.path>")
        logger.info("  purepoetry list add <dotted.path>=<value>")
        logger.info("  purepoetry list remove <dotted.path>")
        return

    if verb == "edit":
        logger.info("Purpose:")
        logger.info("  Modify configuration values.")
        logger.info("")
        logger.info("Usage:")
        logger.info("  purepoetry edit")
        logger.info("  purepoetry edit <string>")
        logger.info("  purepoetry edit <dotted.path>=<value>")
        logger.info("  purepoetry edit <dotted.path>")
        return

    if verb == "test":
        logger.info("Purpose:")
        logger.info("  Evaluate project configuration against invariant rules.")
        logger.info("")
        logger.info("Usage:")
        logger.info("  purepoetry test")
        logger.info("  purepoetry test <rule-id>")
        return

    if verb == "help":
        logger.info("Purpose:")
        logger.info("  Navigate PurePoetry help topics.")
        logger.info("")
        logger.info("Usage:")
        logger.info("  purepoetry help")
        logger.info("  purepoetry help <item>")
        return

    logger.info("Purpose:")
    logger.info("  Command")
    logger.info("")
    logger.info("Usage:")
    logger.info(f"  purepoetry {verb} ...")


def _topic_block_registry(logger: logging.Logger) -> None:
    logger.info("Registry defines what PurePoetry knows about the system.")
    logger.info("")
    logger.info("It contains conceptual categories:")
    for c in _REGISTRY_CATEGORIES:
        logger.info(f"  {c}")
    logger.info("")
    logger.info("For details:")
    logger.info("  purepoetry help registry <item>")
    logger.info("")
    logger.info("To inspect actual registry contents:")
    logger.info("  purepoetry show rules")


def _topic_block_registry_item(logger: logging.Logger, item: str) -> None:
    logger.info(f"Registry: {item}")
    logger.info("")
    if item == "types":
        logger.info("Purpose:")
        logger.info("  Defines shared data types for invariants and fixes.")
    elif item == "invariants":
        logger.info("Purpose:")
        logger.info("  Defines rules the project is expected to satisfy.")
        logger.info("  Evaluated by test; displayed via show rules.")
    elif item == "fixes":
        logger.info("Purpose:")
        logger.info("  Defines explicit repair actions for failed invariants.")
    else:
        logger.info("Purpose:")
        logger.info("  Registry category.")
    logger.info("")
    logger.info("To inspect entries:")
    logger.info("  purepoetry show rules")


def resolve_help_request(tokens: List[str]) -> HelpRequest:
    """ determine what is required for a specific help request """
    topic = tokens[0] if len(tokens) >= 1 else None
    subtopic = tokens[1] if len(tokens) >= 2 else None
    return HelpRequest(topic=topic, subtopic=subtopic)


def run_help(tokens: List[str], registry: Dict[str, str]) -> int:
    """ invoke the correct help request. expect this gets delegated to correct file """
    logger = _logger()
    req = resolve_help_request(tokens)

    _frame(logger)

    if req.topic is None:
        _topic_block_main(logger)
        return 0

    topic = req.topic.strip().lower()

    if topic == "commands":
        _separator(logger)
        if req.subtopic is None:
            _topic_block_commands(logger, registry)
            return 0
        cmd = req.subtopic.strip().lower()
        if cmd not in registry:
            _error_block(logger, f"Unknown command: {cmd}")
            return 2
        _topic_block_command(logger, cmd)
        return 0

    if topic == "registry":
        _separator(logger)
        if req.subtopic is None:
            _topic_block_registry(logger)
            return 0
        item = req.subtopic.strip().lower()
        if item not in _REGISTRY_CATEGORIES:
            _error_block(logger, f"Unknown registry item: {item}")
            return 2
        _topic_block_registry_item(logger, item)
        return 0

    _separator(logger)
    if topic in registry:
        _topic_block_command(logger, topic)
        return 0
    if topic in _REGISTRY_CATEGORIES:
        _topic_block_registry_item(logger, topic)
        return 0

    _error_block(logger, f"Unknown help topic: {topic}")
    return 2
