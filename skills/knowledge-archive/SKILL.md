---
name: knowledge-archive
description: Store and retrieve personal knowledge in ~/knowledge/ as simple Markdown files.
---

# Personal Knowledge Archive

## Location

All knowledge lives in `~/knowledge/` as flat Markdown files — one `.md` file per topic.

## Storing New Knowledge

When the user asks to save something:

1. Pick a concise filename: `~/knowledge/<topic>.md`
2. Write clean Markdown with a `# Title` header
3. Use subheadings, bullet lists, and code blocks as needed — keep it skimmable

## Retrieving Knowledge

- Ask the user what they want, then `ls ~/knowledge/` to find the matching file
- If unsure, ask the user for keywords

## Rules

- One file per topic — don't split a topic across files
- Keep it brief — this is a reference, not a novel
- No deeply nested subdirectories — flat is simpler
