#!/usr/bin/env python3
import os
import re

# Fix all TSX files in components directory
for root, dirs, files in os.walk("components"):
    for file in files:
        if file.endswith(".tsx"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            original = content

            # Fix corrupted self-closing tags
            content = re.sub(r' /">', ' />', content)

            # Fix missing quotes in attributes
            content = re.sub(r'size=icon\b', 'size="icon"', content)
            content = re.sub(r'size=lg\b', 'size="lg"', content)
            content = re.sub(r'variant=outline\b', 'variant="outline"', content)
            content = re.sub(r'variant=secondary\b', 'variant="secondary"', content)
            content = re.sub(r'variant=ghost\b', 'variant="ghost"', content)

            if content != original:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed: {filepath}")
            else:
                print(f"No changes: {filepath}")

print("\nAll files processed")
