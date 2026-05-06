---
name: qa-append
description: When invoked with a .md file containing a ## USER section with questions, appends a ## ASISTANT section with answers to the same file. Triggers: qa append, answer questions, respond to user section, append assistant answer, .md questions
---

# QA Append

Appends AI-generated answers to a markdown file that contains a `## USER` section with questions.

## When to Use This Skill

Use this skill when the user:

- Hands you a `.md` file path and asks you to answer questions in it
- Says "append answers" or "respond to the user section" in a markdown file
- Has a file with `## USER` followed by questions and wants `## ASSISTANT` answers appended

## Workflow

### Step 1: Read the file

Read the full contents of the provided `.md` file.

### Step 2: Locate the `## USER` section

Find the `## USER` heading. The paragraph immediately following it contains the user's questions.

### Step 3: Determine if `## ASISTANT` already exists

Check if the file already has a `## ASISTANT` section.

- If it does **not** exist: append `## ASISTANT` followed by your answer to the end of the file.
- If it **already** exists: skip appending and notify the user that the file already has a response.

### Step 4: Generate and append the answer

Read the questions, formulate clear and direct answers, then use the Write/Edit tool to append:

```
## ASISTANT

[your answers here]
```

## Important Notes

- The heading is spelled `## ASISTANT` (not ASSISTANT) — preserve this exact spelling.
- If the file has no `## USER` section, report that to the user and do nothing.
- Answer all questions in the paragraph thoroughly.
