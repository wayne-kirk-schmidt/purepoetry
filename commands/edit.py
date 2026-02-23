#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EDIT command for purepoetry.

Contract:

purepoetry edit
    → delegate to show

purepoetry edit <string>
    → if exact dotted path:
         - scalar → prompt for new value
         - list   → enter list edit mode
         - dict   → error (edit child key)
      else:
         → delegate to show <string>

purepoetry edit dotted.path=value
    → update scalar immediately
"""

import sys
sys.dont_write_bytecode = True

from pathlib import Path
import tomlkit
from tomlkit.items import Array
from tomlkit.toml_document import TOMLDocument

# ============================================================
# Helpers
# ============================================================

def _load_document(variables):
    srcfile = variables.get("pyproject_path", "pyproject.toml")
    path = Path(srcfile)

    if not path.exists():
        print(f"[fatal] pyproject.toml not found at: {path}")
        return None, None

    try:
        with path.open("r", encoding="utf-8") as f:
            doc = tomlkit.parse(f.read())
        return doc, path
    except Exception as exc:
        print(f"[fatal] Failed to parse TOML: {exc}")
        return None, None


def _write_document(doc: TOMLDocument, path: Path):
    with path.open("w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))


def _collect_paths(data, prefix=""):
    paths = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            paths.append(new_prefix)
            paths.extend(_collect_paths(value, new_prefix))

    elif isinstance(data, list):
        # do not descend into lists for path discovery
        pass

    return paths


def _resolve_path(doc, dotted_path):
    parts = dotted_path.split(".")
    current = doc

    for part in parts:
        if part in current:
            current = current[part]
        else:
            return None

    return current


def _resolve_parent(doc, dotted_path):
    parts = dotted_path.split(".")
    parent = doc
    for part in parts[:-1]:
        if part in parent:
            parent = parent[part]
        else:
            return None, None
    return parent, parts[-1]


def _delegate_to_show(query, variables):
    from lib.commands.show import run_action as show_run_action
    show_run_action(query, None, variables)


# ============================================================
# List Edit Mode
# ============================================================

def _list_edit_mode(doc, path_obj, path_str, file_path):
    while True:
        print(f"\nCurrent list for {path_str}:\n")
        for i, item in enumerate(path_obj):
            print(f"[{i}] {item}")

        print("\nOptions:")
        print("  e <index> = edit element")
        print("  d <index> = delete element")
        print("  a         = append new element")
        print("  r         = replace entire list")
        print("  q         = quit")

        cmd = input("Enter command: ").strip()

        if cmd == "q":
            return

        if cmd.startswith("e "):
            try:
                idx = int(cmd.split()[1])
                current_value = path_obj[idx]
                print(f"Current value: {current_value}")
                new_val = input("Enter new value: ")
                path_obj[idx] = new_val
                _write_document(doc, file_path)
                print(f"Updated index {idx}")
            except Exception:
                print("[error] Invalid index")

        elif cmd.startswith("d "):
            try:
                idx = int(cmd.split()[1])
                del path_obj[idx]
                _write_document(doc, file_path)
                print(f"Deleted index {idx}")
            except Exception:
                print("[error] Invalid index")

        elif cmd == "a":
            new_val = input("Enter new value: ")
            path_obj.append(new_val)
            _write_document(doc, file_path)
            print("Appended value")

        elif cmd == "r":
            new_val = input("Enter new list as Python list literal: ")
            try:
                new_list = eval(new_val)
                if not isinstance(new_list, list):
                    raise ValueError
                parent, key = _resolve_parent(doc, path_str)
                parent[key] = tomlkit.array(new_list)
                _write_document(doc, file_path)
                print("Replaced entire list")
            except Exception:
                print("[error] Invalid list syntax")

        else:
            print("[error] Invalid command")


# ============================================================
# run_action
# ============================================================

def run_action(obj, value, variables):

    # edit → delegate to show
    if obj is None:
        _delegate_to_show(None, variables)
        return

    # parse assignment
    if value is None and "=" in obj:
        path_str, new_value = obj.split("=", 1)

        doc, file_path = _load_document(variables)
        if doc is None:
            return

        target = _resolve_path(doc, path_str)
        if target is None:
            _delegate_to_show(path_str, variables)
            return

        if isinstance(target, list):
            print("[error] Cannot assign entire list via '='. Use list edit mode.")
            return

        parent, key = _resolve_parent(doc, path_str)
        parent[key] = new_value
        _write_document(doc, file_path)
        print(f"Updated {path_str} to {new_value}")
        return

    # single argument mode
    path_str = obj

    doc, file_path = _load_document(variables)
    if doc is None:
        return

    target = _resolve_path(doc, path_str)

    if target is None:
        _delegate_to_show(path_str, variables)
        return

    # scalar
    if not isinstance(target, (dict, list)):
        print(f"Current value for {path_str}:")
        print(target)
        new_val = input("Enter new value: ")
        parent, key = _resolve_parent(doc, path_str)
        parent[key] = new_val
        _write_document(doc, file_path)
        print(f"Updated {path_str}")
        return

    # list
    if isinstance(target, list):
        _list_edit_mode(doc, target, path_str, file_path)
        return

    # dict
    print("[error] Cannot edit a table directly. Edit a child key.")
    return
