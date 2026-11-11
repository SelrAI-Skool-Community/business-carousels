# Tool routes

The workflow is the same everywhere. Only the production route changes with what the session can actually do.

## Two separate things

- **Planning model:** the assistant you are talking to. It reads the source, plans and writes. Keep the model the user selected; never switch models to reach an image feature.
- **Image tool:** a callable tool that makes or edits pictures (a built-in image generator, a connected image tool, a design tool). It is separate from the planning model. A model's name or this skill's text does not prove an image tool exists. Look at the tools this session actually offers.

If the user asked for a specific image tool or provider and it is not available, say so and prepare the brief. Never substitute another provider silently.

Never install paid services, create accounts, request API keys or spend credit to fill a gap. Use only tools already available and authorised.

## Choose the route

| What this session can do | Route | Describe the result as |
| --- | --- | --- |
| Generate and view images | Whole-slide generation with text and image planned together, then inspect and repair | "Generated with [tool], inspected" |
| Edit a supplied or approved image | Targeted edit that keeps the approved scene | "Edited with [tool], inspected" |
| Use supplied photos plus HTML/SVG/code with rendering | Photo-led layout with exact fonts over the real photo | "Layout built over your photo" |
| HTML/SVG/code with rendering, no photos | Diagram, chart, type-led or illustrated slide | "Rendered design" |
| HTML/SVG/code without a way to view the result | Editable source, with the missing visual check stated | "Unrendered design source" |
| Writing only | Approved copy, whole-slide plan and a complete generation prompt per slide | "Production brief; no image made" |

Measured charts need code or a locked geometry guide whichever route you use. Exact brand fonts need a type layer rendered from the actual font files.

## Host notes

- **Claude (claude.ai and apps):** plans, writes and builds diagrams, charts and visuals with HTML and SVG, and can view uploaded images. Claude itself does not generate photos or photoreal illustrations; that needs a separate image tool or connector in the session. A photo-led layout using the user's real photo is a good route.
- **Claude Code:** reads this skill from disk. `scripts/slides.py render` draws type-led and photo-led slides at the exact size with the Chrome or Edge already on the computer. Raster generation only through an image tool or MCP server that is already connected.
- **ChatGPT:** can usually generate and edit images in the conversation when the account has that feature. Use it for whole-slide scenes; check spelling and figures afterwards.
- **Codex:** reads this skill from disk and can run `scripts/slides.py` the same way. Some environments include a built-in image generation tool; others do not. Check before promising images.

Features vary by plan, account and date. Trust the tools you can see, not these notes.

## Record what produced what

For each delivered image note: planning model, image tool, the image model ID only if the tool shows it, the prompt, reference files used, and which parts were generated, edited, photographed or rendered in code. Tell the user plainly, for example: "Scene generated with the built-in image tool; headline and labels rendered in code with your brand fonts." Never say a model made a photo when it only wrote the prompt.

## When no image tool exists

Say it in one line, for example "Image generation isn't available in this session." Then deliver, per slide: the approved copy, the whole-slide plan, and one complete prompt the user can paste into their image tool (scene, people, brand marks, exact text and its placement, palette, what to avoid). Offer an HTML/SVG version only where it genuinely suits the slide.
