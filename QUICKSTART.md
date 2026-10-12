# Quick start

Same skill, same steps everywhere. Only the install route differs. Pick yours.

## Claude (claude.ai, desktop or mobile app)

**Option A: paste the prompt (works everywhere)** Paste [PROMPT.md](PROMPT.md) into a chat and attach your source and brand files.

**Option B: install it as a custom skill** If you were given a `business-carousels.zip` file:

1. Settings > Capabilities: turn on **Code execution and file creation**. On Team or Enterprise plans an owner enables Skills for the organisation.
2. Open **Customize > Skills**, click **+**, then **Create skill > Upload a skill**, and upload the ZIP without unzipping it.
3. Start a chat: "Use the business-carousels skill. Here's my source and brand."

Claude plans, writes and builds layouts, diagrams and charts in HTML or SVG, and can work with photos you upload. It does not generate photos itself; for photoreal scenes it will give you a complete prompt to use in an image tool, unless your session has an image tool connected.

## Claude Code

1. Ask Claude Code to follow [SETUP-PROMPT.md](SETUP-PROMPT.md) in this folder. That file is the whole setup.
2. In Claude Code, type `/business-carousels` or just ask for a carousel; the skill loads when relevant.
3. For a one-off, you can instead say: "Read ~/.claude/skills/business-carousels/SKILL.md and follow it."

Images need an image tool or MCP server already connected in your setup. Without one, Claude Code can render HTML/SVG slides locally and write image prompts.

## ChatGPT

1. Paste [PROMPT.md](PROMPT.md) into a new chat, or upload it as a file.
2. Attach your source, brand files and, optionally, a few example images.
3. Say: "Follow this guide. Show me the slide plan first."

If your account has image generation, ChatGPT can make the slides directly. Check spelling and numbers on every image. If your workspace offers a Skills feature, its current help pages explain how to add one; availability varies by plan.

## Codex

1. Ask Codex to follow [SETUP-PROMPT.md](SETUP-PROMPT.md) in this folder. That file is the whole setup.
2. Invoke it with `$business-carousels`, or ask for a carousel and let Codex pick the skill.
3. For a one-off: "Read ~/.agents/skills/business-carousels/SKILL.md and follow it."

Some Codex environments include image generation; others don't. The skill checks before promising images.

## What to have ready

- Your source (reel link or transcript, post, article or notes).
- Logo, colours, fonts or handwriting files, and two or three posts you like.
- Where it will be posted and the size, if known.
- Your ending: the exact comment keyword and the resource you've actually prepared, or "save this".

Making a carousel never posts it. Publishing stays your call.
