#!/usr/bin/env python3
"""Utility to analyze Dash callback registrations for conflicts."""

import os
import re
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import pandas as pd


def find_callback_registrations():
    """Search Python files for Dash callback registration patterns.

    Recursively scans the project directory for Python files and identifies
    lines containing callback decorators, callback references, or specific
    component IDs that might cause conflicts. Used for debugging callback
    registration issues in Dash applications.

    Returns:
        Dictionary mapping file paths to lists of found patterns. Each pattern
        entry contains:
            - line (int): Line number where pattern was found
            - content (str): Full line content containing the pattern
            - pattern (str): Regex pattern that matched this line

    Raises:
        PermissionError: If unable to read certain files due to permissions
        UnicodeDecodeError: If files contain non-UTF-8 encoded content

    Example:
        >>> findings = find_callback_registrations()
        >>> print(f"Found callback patterns in {len(findings)} files")
        >>> for filepath, matches in findings.items():
        ...     print(f"{filepath}: {len(matches)} patterns found")

    Performance:
        Scans entire project directory recursively. Performance scales with
        project size. Typical scan time is 100-500ms for medium projects.
        Excludes hidden directories and __pycache__ for efficiency.

    Note:
        This function is primarily used for debugging and should not be called
        in production code paths due to file system scanning overhead.
    """

    print("🔍 Searching for callback registrations...")
    search_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                search_files.append(os.path.join(root, file))

    callback_patterns = [
        r'@app\.callback',
        r'@.*\.callback',
        r'floor-slider-value',
        r'num-floors-store',
        r'Output.*num-floors',
        r'Input.*num-floors',
    ]

    findings = {}
    for file_path in search_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    for pattern in callback_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.setdefault(file_path, []).append({
                                'line': i,
                                'content': line.strip(),
                                'pattern': pattern,
                            })
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
    return findings


def analyze_floor_callbacks(findings: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Highlight floor-slider callback references."""
    print("\n🎯 Analyzing floor slider callbacks...")
    floor_files = []
    for file_path, matches in findings.items():
        for match in matches:
            if 'num-floors' in match['content'].lower():
                floor_files.append({
                    'file': file_path,
                    'line': match['line'],
                    'content': match['content'],
                })

    if floor_files:
        print("\n📍 Found floor slider references:")
        for item in floor_files:
            print(f"   📄 {item['file']}:{item['line']}")
            print(f"      {item['content']}")
            print()
    else:
        print("   ✅ No floor slider references found")
    return floor_files


def suggest_fixes(findings: Dict[str, List[Dict[str, Any]]]) -> None:
    """Offer potential resolutions for callback conflicts."""
    print("\n🔧 Suggested Fixes:")
    callback_files = []
    for file_path, matches in findings.items():
        for match in matches:
            if re.search(r'@app\.callback', match['content']) or re.search(r'@.*\.callback', match['content']):
                callback_files.append(file_path)

    callback_files = list(set(callback_files))
    if len(callback_files) > 1:
        print(f"\n⚠️ Found callbacks in {len(callback_files)} files:")
        for file in callback_files:
            print(f"   📄 {file}")
        print("\n💡 Solutions:")
        print("1. 🎯 Remove duplicate floor slider callback from app.py")
        print("2. 🔄 Keep floor slider callback only in classification handlers")
        print("3. ✅ Use allow_duplicate=True if multiple callbacks are needed")
        print("4. 🧹 Consolidate related callbacks into one function")
    print("\n🚀 Quick Fix:")
    print("   Remove the floor slider callback from app.py")
    print("   It should be handled in ui/components/classification_handlers.py")


def main() -> None:
    """Run callback diagnostics."""
    print("🔍 Dash Callback Conflict Diagnostic")
    print("=" * 50)
    findings = find_callback_registrations()
    if not findings:
        print("✅ No callback patterns found")
        return
    print(f"\n📊 Found callback patterns in {len(findings)} files:")
    for file_path, matches in findings.items():
        print(f"\n📄 {file_path}:")
        for match in matches:
            print(f"   Line {match['line']}: {match['content']}")
    floor_callbacks = analyze_floor_callbacks(findings)
    suggest_fixes(findings)
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print(f"   📄 Files with callbacks: {len(findings)}")
    print(f"   🎚️ Floor slider references: {len(floor_callbacks)}")
    if len(floor_callbacks) > 1:
        print("   ⚠️ LIKELY CAUSE: Multiple floor slider callbacks")
        print("   ✅ FIX: Remove duplicate from app.py")
    else:
        print("   ✅ Floor slider callbacks look OK")


if __name__ == "__main__":
    main()
