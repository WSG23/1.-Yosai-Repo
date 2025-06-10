#!/usr/bin/env python3
"""Utility to analyze Dash callback registrations for conflicts."""

import os
import re


def find_callback_registrations():
    """Search all Python files for callback-related patterns."""
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


def analyze_floor_callbacks(findings):
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


def suggest_fixes(findings):
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


def main():
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
