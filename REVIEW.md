# Review

What was checked before this package was prepared, and what was not. Checked 3 October 2026.

## Visual review of the 15 examples

Every PNG original was viewed at full size and again at phone size (432 × 540). Faces and hands in all five people examples were also cropped and checked up close.

- **Spelling:** all headlines, kickers and labels read correctly. Background signs, books and chalkboards in examples 12 to 15 contain generated slogans; they are spelled correctly but are set dressing.
- **Figures:** $386M to about $4.6B is roughly 12x (example 24). $34B plus about $8B makes the $42B on the cover (examples 21 and 25). Units, year and currency appear on the slides. These figures belong to a Reuters report dated 28 September 2026 and were not re-verified for this package.
- **Anatomy:** eyes, teeth, fingers, grips, joints, feet on floors and the salon mirror reflection are believable. No blocking defect found.
- **Readability at phone size:** headlines read clearly on all 15. Small kickers (01, 03, 05, 11) and some labels are hard to read: the electrician's "SWITCHBOARD" label and the skincare labels most of all. They are noted in the examples guide as a lesson.
- **Composition:** no text over faces, hands or key objects. Arrows land on their objects.
- **Honest gaps in the examples:** example 25 compares two objects that are not to scale without an "Illustrative comparison" label, and the cover sculpture in 21 is also not to scale. Both are flagged in the examples guide rather than edited, because they are approved, finished files. The skincare labels repeat text already printed on the products.

## Static package checks (passed)

- Every relative link in every Markdown file resolves. Links inside the skill stay inside the skill folder, so the installed skill is self-contained.
- Privacy scan: no personal names, emails, phone numbers, handles, private paths, credentials, internal tools or ask-a-person fallbacks in any text file.
- `SKILL.md` name `business-carousels`; description 195 characters (Claude's upload limit is 200).
- Each skill image is a quality-90 JPEG at original resolution of its PNG original (PSNR 38 to 44 dB); hashes of all 15 PNG originals are recorded in `index.json` and re-checked.
- The Claude upload ZIP of the skill folder (built separately, not stored in the repository): integrity test passed, skill folder at the archive root, contents identical to the folder (27 files, about 5 MB).
- `gallery.html`: all 15 images load; no sideways scrolling at 375 px phone width.
- Prompts in `example-prompts.md` and `GENERATION-PROMPTS.json` were copied from the original records by script, not retyped.

## Live installation tests

| Host | Result |
| --- | --- |
| Claude Code | **Passed.** Installed from the ZIP into a fresh project's `.claude/skills/` and run headless with Sonnet. It loaded the skill, read the references, flagged a contradiction in the test idea instead of inventing figures, planned in chat with a story-led slide count, put the measured chart in code, used a "save this" ending because no resource existed, and named its real image tool without claiming output. |
| Claude (claude.ai upload) | Not tested. Needs an account upload through Customize > Skills. |
| ChatGPT | Not tested. |
| Codex | **Passed.** Codex CLI read the skill from a folder and made a four-slide carousel with its built-in image tool, inspected it at full and phone size, fixed four defects and reported its tool honestly. The configured default model was refused on a ChatGPT-account login, so it ran on gpt-5.6-sol. |
| Image generation through the skill | **Passed in Claude and Codex.** Same brief in both; see `examples/live-tests/`. |

## Provenance of the examples

Examples 01 to 05 and 11 to 15: one whole-slide generation each with a built-in image tool in a Codex session. Their PNG originals keep embedded Content Credentials (C2PA) that mark them as AI-generated and name ChatGPT / gpt-image as the generator; no more specific model version is recorded. The credentials contain no personal data. The JPEG copies inside the skill have metadata stripped. One accountant correction and one plumbing kicker repair were targeted edits; the plumbing edit prompt was not recorded. Examples 21 to 25: a generated scene with built-in image generation plus headline, figures and handwriting rendered in code from the bundled font files.

None of these images is approved for any business other than as a teaching example.
