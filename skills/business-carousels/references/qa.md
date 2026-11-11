# Quality checks

Check the actual exported files, not the prompt. First run `scripts/slides.py check <folder> --platform <name>`: it names any file of the wrong size or shape, too many slides, or slides out of order. Then view each slide at full size, then at phone size (about 430 px wide). A contact sheet is for navigation only.

## Words and facts

- [ ] Headline and labels match the approved copy exactly: spelling, punctuation, capitals.
- [ ] Every number matches its source, with unit, period and currency.
- [ ] Qualifications that change the meaning are on the slide or the very next one.
- [ ] Hypothetical examples and illustrations are labelled as such.
- [ ] No invented screens, results, reviews, logos, ratings or testimonials.
- [ ] Generated background lettering (signs, books, chalkboards) is spelled correctly or removed.

## Visuals

- [ ] Each slide's visual teaches the point, not just decorates it.
- [ ] Every arrow starts at its label and lands on the right object.
- [ ] Measured charts have correct proportions; artistic comparisons say "Illustrative comparison".
- [ ] Genuine logos keep their colours and proportions and sit on the objects where they matter.
- [ ] People: eyes, teeth, hands and fingers, joints, contact points, reflections and proportions are believable.
- [ ] Brand fonts, handwriting and colours are consistent across the deck.

## Readability and composition

- [ ] Headline readable at phone size without zooming.
- [ ] Labels that carry meaning are readable at phone size (tiny kickers and labels are the usual failure).
- [ ] No text over faces, hands, key objects or figures; comfortable margins.
- [ ] Platform overlays (profile, caption, buttons) do not cover essential text.
- [ ] Interiors have the same finish and detail as the cover.
- [ ] Whitespace came from composition, not from deleting needed information.

## Ending and versions

- [ ] The comment keyword (if any) is visually highlighted and identical in artwork and caption.
- [ ] The promised resource exists; any delivery automation is confirmed or not implied.
- [ ] Approved scenes were preserved in wording-only revisions.
- [ ] `final/`, `alternates/` and `trials/` are separate; finals are numbered in posting order (`scripts/slides.py finalise` does this).

## Report honestly

Say which slides you viewed at full and phone size, which tool produced each image, and anything you could not check. A successful render or file creation is not the same as an inspected result.
