---
name: business-carousels
description: Plan, make and check social carousels for a business. Use for a carousel, post slides, or turning a reel, post, article or notes into one. Plans first, keeps the facts, checks every slide's size.
---

# Business carousels

Turn an idea, reel, carousel, article or notes into a carousel a busy business owner understands at a glance. The route changes with the tools this session has; the standard does not.

`scripts/slides.py` in this skill's folder does the fixed steps: platform sizes and slide limits (`sizes`), rendering type-led or photo-led slides at the exact size with text fitted and readable on a phone (`render`), checking any set of slide images (`check`), and numbering approved files into `final/` (`finalise`). Run it with `python3` (Windows: `py`). Its docstring shows the plan format.

## 1. Understand the source

Read [source and plan](references/source-and-plan.md). Before rewriting, note the hook, memorable wording, examples, numbers (with units, dates and the place or group they apply to), qualifications and reveal order. Keep what makes the framing work. Mark source facts apart from your own examples. If the source cannot be opened, say what is missing; never invent its content.

## 2. Plan in chat first

Show a slide-by-slide table: headline, one short supporting line where needed, essential labels, and what each visual explains. Plain words. The story sets the slide count. Then stop and wait for approval, unless this exact plan is already approved. Never add a price, statistic, guarantee or claim the source did not make.

## 3. Design each whole slide

Read [slide design](references/slide-design.md). Plan headline, imagery, logos, labels and empty space together. Visuals teach: real examples, the relevant app screen, a comparison, a diagram. Numbers carry units and context. Measured charts use accurate geometry; artistic comparisons say "Illustrative comparison". Interiors get the same care as the cover.

## 4. Brand, people and the promise

- Brand: [brand and identity](references/brand-and-identity.md). Use the business's colours, fonts and logos; generated lettering is not the brand font.
- People: [people](references/people.md). Believable, ordinary, never presented as staff, customers or testimonials.
- Ending: [CTA and revisions](references/cta-and-revisions.md). A comment keyword stands out and matches a resource that really exists. Never imply an automation or download that is not set up.

## 5. Make the slides with the tools you have

Read [tool routes](references/tool-routes.md). Check this session's real tools; do not assume a model can make photographs, and never install services, ask for keys or switch providers.

- An image tool: generate whole slides as planned, then inspect them.
- No image tool, or a type-only or photo-led slide: write a plan file and run `slides.py render <plan.json> --out <folder>`. It uses the Chrome or Edge already on the computer, puts headline, support line, label and comment keyword in clear space over a colour or the person's own photo, in their font file if they have one. Set `highlight` to the payoff words of each headline so the brand colour carries through. If it says a slide does not fit, cut words or split the slide.
- No way to make images at all: give the approved copy and one complete generation prompt per slide.

Say which tool made each image.

## 6. Check, then finish

Run [qa](references/qa.md) on the real files, at full size and at phone size. Run `slides.py check <folder> --platform <name>` on every set, whatever made it: image tools often return 1024x1536, which Instagram crops. Fix what it names. When the person approves, `slides.py finalise <files in posting order> --project <folder> --name <name> --platform <name>` numbers them into `final/`; earlier finals move to `alternates/`, never overwritten. A wording change keeps the approved scene.

Say what you inspected and what you could not. Publishing and sending stay separate steps the person approves.

[Style options](references/style-options.md), [examples](references/examples.md) and [example prompts](references/example-prompts.md) show possibilities; their colours, people, wording and layouts are never defaults.

Made by Selr AI.

<!-- Provenance marker: sk-uq5b1e --><!-- Provenance signature: ⁠​‌​‌​​‌‌​‌​​​‌​‌​‌​​‌‌​​​‌​‌​​‌​​​‌‌​​​‌⁠ -->
