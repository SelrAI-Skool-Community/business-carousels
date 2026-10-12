# Business Carousels: setup prompt

This file is written to you, the attendee's AI agent (Claude Code or Codex). Follow it from start to finish to install the Business Carousels skill on this computer: it plans image-led carousels that teach, with the attendee, slide by slide, then has you make the slides with the image tools you already have.

**This folder is the kit.** "The kit folder" below means the folder this file is in, wherever it came from (Loup's copy under `~/.loup/kits/business-carousels/`, a zip, a School download). Never clone, pull or download the kit from GitHub, and never ask the attendee for a GitHub account, sign-in, password or token. Never write, change, delete or run anything inside the kit folder itself when it is under `~/.loup/kits/`: Loup re-verifies every byte there. You only copy out of it.

**How to work.** The attendee is not a developer. Do all of this yourself: run the commands, do not hand them over, and do not ask for a go-ahead. Explain each step in one plain sentence as it finishes. The only place you might pause is a restart at the end, if the skill does not show up yet. If a step fails, show the real error, fix it yourself and try again; never report a failed step as done. Never ask the attendee for a password, a sign-in, an account, a token or a code: nothing here needs one.

**What the attendee should expect.** Under five minutes. The skill is a folder of instructions, reference pages and fifteen example images (about 5MB). It needs no extra runtime, account or API key, and it never posts or publishes anything. It uses whatever image tools the attendee's app already has; those may have their own plan limits or charges, and when no image tool is available the skill says so and writes a complete image prompt instead.

## 0. Work out where you are (do not ask)

- **Mac or Windows.** On Windows, run the PowerShell block below in Windows PowerShell (`powershell.exe`, 5.1 is fine). If your shell tool is Git Bash, save the block to a temporary `.ps1` file and run `powershell -NoProfile -ExecutionPolicy Bypass -File <that file>`. Never use WSL: it has a different home folder.
- **Claude Code or Codex.** The skill folder is `~/.claude/skills` for Claude Code and `~/.agents/skills` for Codex (Windows: `$HOME\.claude\skills` or `$HOME\.agents\skills`). The blocks below are written for Claude Code; in Codex, change the second line as its comment says. Wherever this file says "restart Claude", Codex restarts the Codex app instead.

## 1. Copy the skill into the skill folder

This is a skill-only kit: the kit's `skills/business-carousels` folder is copied into the skill folder as `business-carousels`, and nothing else is installed. The rest of the kit folder (the full-size examples, the showcase panels and the chat prompt) stays where it is.

- **A folder is this skill** only if it has `references/source-and-plan.md` and a `SKILL.md` whose frontmatter (between the first two `---` lines) has `name: business-carousels`.
- **Never write through a link, and never copy from one.** Stop if the kit folder, or a folder above it inside the home folder, is a symbolic link or a Windows junction, or if anything inside the kit folder is one. Stop too if `<skill folder>/business-carousels`, the skill folder itself, a folder above them inside the home folder (for example `~/.claude`), or anything inside the skill's folder is a link.
- **An earlier install of this skill is refreshed, never deleted.** If `<skill folder>/business-carousels` is already there and is this skill, the kit's copy is copied over it: the skill's own files are brought up to date and anything the attendee added inside it is kept. If any file the attendee had in it differs from the kit's copy of that file (they edited the skill, or it is an older release), the whole earlier folder is first saved to `~/.loup/installed/business-carousels.previous-<date and time>` (Windows `$HOME\.loup\installed\...`), beside Loup's folders and outside the skill folder, so the agent never loads the skill twice. That saved copy is never deleted. Nothing else under `~/.loup` is written.
- If `<skill folder>/business-carousels` is there but is a file, or a folder that is not this skill, stop and tell the attendee you found something there that is not this skill. Never overlay or delete it. Stop too, before copying anything, if it holds a file where the skill has a folder or a folder where the skill has a file: the copy never replaces one with the other.
- `.git` and the attendee-owned names `.env`, `secrets`, `memory`, `.state` and `agents.json` are never copied, so nothing of the attendee's by those names is overwritten.
- There is no older home to move: earlier versions of this setup used a temporary download that they deleted, and copied the same skill folder to the same place. A `~/skool-kits/business-carousels` folder belongs to Kit Feed: leave it alone.

Put the kit folder's full path in place of `<kit folder>` (in Git Bash, write it with forward slashes, for example `/c/Users/sam/...`). The block prints a `STOP:` line and ends with an error (exit 1), having written nothing after that point, if the kit folder is missing, is not this kit, is reached through a link or holds one; if the skill folder, a folder above it or anything inside the skill's folder is a link; if something that is not this skill is in the way, or a file sits where the skill has a folder (or the other way round); or if saving the earlier copy or any step of the copy fails.

Mac or Linux (runs in bash or zsh, or Git Bash on Windows). In Codex, the second line is `SKILLS="$HOME/.agents/skills"`:

```bash
KIT="<kit folder>"
SKILLS="$HOME/.claude/skills"
SRC="$KIT/skills/business-carousels"
DEST="$SKILLS/business-carousels"
SAVED="$HOME/.loup/installed/business-carousels.previous-$(date +%Y%m%d-%H%M%S)"
# skill_named FILE: FILE opens with a frontmatter block holding the line name: business-carousels
skill_named() {
  awk '{sub(/\r$/,"")} NR==1{if($0!="---")exit 1;next} /^---$/{c=1;exit} $0=="name: business-carousels"{f=1} END{exit !(f&&c)}' "$1" 2>/dev/null
}
# is_this_skill DIR: DIR is a copy of the business-carousels skill
is_this_skill() {
  [ -f "$1/references/source-and-plan.md" ] && skill_named "$1/SKILL.md"
}
# linked PATH: PATH, a folder above it inside the home folder, or anything inside it is a link
linked() {
  p="$1"
  while [ "$p" != "$HOME" ] && [ "$p" != "/" ] && [ -n "$p" ]; do
    [ -L "$p" ] && return 0
    p="$(dirname "$p")"
  done
  [ -d "$1" ] && [ -n "$(find "$1" -type l 2>/dev/null | head -n 1)" ]
}
# above_linked PATH: PATH or a folder above it inside the home folder is a link
above_linked() {
  p="$1"
  while [ "$p" != "$HOME" ] && [ "$p" != "/" ] && [ -n "$p" ]; do
    [ -L "$p" ] && return 0
    p="$(dirname "$p")"
  done
  return 1
}
# edited DIR: a file in DIR that the incoming skill also has is different (names that are never copied aside)
edited() {
  ( cd "$1" && find . \( -name .git -o -name .env -o -name secrets -o -name memory -o -name .state -o -name agents.json \) -prune -o -type f -print ) | (
    while IFS= read -r p; do
      if [ -f "$SRC/$p" ] && ! cmp -s "$1/$p" "$SRC/$p"; then exit 0; fi
    done
    exit 1
  )
}
# clash DIR: prints the first path that is a folder in the incoming skill and a file in DIR, or the other way round
clash() {
  ( cd "$SRC" && find . -mindepth 1 \( -name .git -o -name .env -o -name secrets -o -name memory -o -name .state -o -name agents.json \) -prune -o -print ) | (
    while IFS= read -r p; do
      if [ -d "$SRC/$p" ]; then
        if [ -e "$1/$p" ] && [ ! -d "$1/$p" ]; then echo "${p#./}"; exit 0; fi
      elif [ -d "$1/$p" ]; then echo "${p#./}"; exit 0; fi
    done
    exit 1
  )
}
[ -d "$SRC" ] && is_this_skill "$SRC" || { echo "STOP: the kit folder is not there, or is not this kit: $KIT" >&2; exit 1; }
if above_linked "$KIT"; then echo "STOP: the kit folder $KIT is reached through a link. Run setup from the kit folder Loup delivered." >&2; exit 1; fi
if [ -n "$(find "$KIT" -type l 2>/dev/null | head -n 1)" ]; then echo "STOP: the kit folder $KIT holds a link to another folder. Not copying from it." >&2; exit 1; fi
if linked "$DEST"; then echo "STOP: $DEST, or a folder above it such as $SKILLS, or something inside it, is a link. Not writing through it." >&2; exit 1; fi
if [ "$SRC" -ef "$DEST" ]; then
  echo "The kit folder's skill is the installed skill already, so there is nothing to copy."
  exit 0
fi
if [ -e "$DEST" ]; then
  [ -d "$DEST" ] || { echo "STOP: $DEST is a file, not this skill. Left alone." >&2; exit 1; }
  if [ -n "$(ls -A "$DEST")" ] && ! is_this_skill "$DEST"; then echo "STOP: $DEST is not the business-carousels skill. Left alone." >&2; exit 1; fi
  C="$(clash "$DEST")"
  [ -z "$C" ] || { echo "STOP: $DEST/$C is a file where the skill has a folder, or a folder where the skill has a file. Left alone; nothing was copied." >&2; exit 1; }
  if edited "$DEST"; then
    if linked "$SAVED"; then echo "STOP: $SAVED, or a folder above it, is a link. Not writing through it." >&2; exit 1; fi
    mkdir -p "$HOME/.loup/installed" && cp -R "$DEST" "$SAVED" || { echo "STOP: could not save the earlier copy to $SAVED" >&2; exit 1; }
    echo "SAVED: the earlier copy, with its changes, to $SAVED"
  fi
fi
ARCHIVE="$(mktemp "${TMPDIR:-/tmp}/business-carousels.XXXXXX")" || { echo "STOP: the copy failed: no temporary file" >&2; exit 1; }
# Loup's copy is read-only and a copy keeps that, so the skill is made writable (links are never chmodded)
if mkdir -p "$DEST" &&
  find "$DEST" ! -type l ! -perm -u+w -exec chmod u+w {} + &&
  tar -cf "$ARCHIVE" -C "$SRC" --exclude=.git --exclude=.env --exclude=secrets --exclude=memory --exclude=.state --exclude=agents.json . &&
  tar -C "$DEST" -xf "$ARCHIVE" &&
  find "$DEST" ! -type l ! -perm -u+w -exec chmod u+w {} +; then
  rm -f "$ARCHIVE"
  echo "COPIED: the business-carousels skill to $DEST"
else
  rm -f "$ARCHIVE"
  echo "STOP: could not copy the skill to $DEST" >&2; exit 1
fi
```

Windows PowerShell (no backslash at the end of the kit folder path; robocopy reports success with exit codes 0 to 3, and 4 to 7 as long as no file and folder clash; `/IS /IT /IM` make it refresh every file even when its date and size look unchanged; `/A-:R` leaves the copy writable, because Loup's copy is read-only; `.git` and the attendee-owned names go in both `/XD` and `/XF`, because `/XD` matches only folders and `/XF` only files). In Codex, the second line is `$Skills = "$HOME\.agents\skills"`:

```powershell
$Kit = "<kit folder>"
$Skills = "$HOME\.claude\skills"
$Src = "$Kit\skills\business-carousels"
$Dest = "$Skills\business-carousels"
$Saved = "$HOME\.loup\installed\business-carousels.previous-" + (Get-Date -Format 'yyyyMMdd-HHmmss')
function Test-Linked($Path) {
  $p = $Path
  while ($p -and ($p.TrimEnd('\') -ne $HOME.TrimEnd('\'))) {
    $item = Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
    if ($item -and $item.LinkType) { return $true }
    $p = Split-Path -Parent $p
  }
  if (Test-Path -LiteralPath $Path -PathType Container) {
    if (@(Get-ChildItem -LiteralPath $Path -Recurse -Force -Attributes ReparsePoint -ErrorAction SilentlyContinue).Count -gt 0) { return $true }
  }
  return $false
}
function Test-SameFolder($A, $B) {
  if (-not (Test-Path -LiteralPath $A) -or -not (Test-Path -LiteralPath $B)) { return $false }
  return ((Resolve-Path -LiteralPath $A).ProviderPath.TrimEnd('\') -eq (Resolve-Path -LiteralPath $B).ProviderPath.TrimEnd('\'))
}
function Test-LinkedPath($Path) {
  $p = $Path
  while ($p -and ($p.TrimEnd('\') -ne $HOME.TrimEnd('\'))) {
    $item = Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
    if ($item -and $item.LinkType) { return $true }
    $p = Split-Path -Parent $p
  }
  return $false
}
function Test-SkillName($File, $Name) {
  if (-not (Test-Path -LiteralPath $File -PathType Leaf)) { return $false }
  $lines = @(Get-Content -LiteralPath $File)
  if ($lines.Count -lt 2 -or $lines[0] -ne '---') { return $false }
  $found = $false
  for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -eq '---') { return $found }
    if ($lines[$i] -eq "name: $Name") { $found = $true }
  }
  return $false
}
# Test-ThisSkill DIR: DIR is a copy of the business-carousels skill
function Test-ThisSkill($Dir) {
  return ((Test-Path -LiteralPath "$Dir\references\source-and-plan.md" -PathType Leaf) -and (Test-SkillName "$Dir\SKILL.md" 'business-carousels'))
}
# Test-Edited DIR: a file in DIR that the incoming skill also has is different (names that are never copied aside)
function Test-Edited($Dir) {
  $Base = (Resolve-Path -LiteralPath $Dir).ProviderPath.TrimEnd('\')
  foreach ($Item in @(Get-ChildItem -LiteralPath $Dir -Recurse -Force -File -ErrorAction Stop)) {
    $Rel = $Item.FullName.Substring($Base.Length + 1)
    if (@($Rel.Split('\') | Where-Object { $Protected -contains $_ }).Count -gt 0) { continue }
    $Match = Join-Path $Src $Rel
    if ((Test-Path -LiteralPath $Match -PathType Leaf) -and ((Get-FileHash -LiteralPath $Item.FullName).Hash -ne (Get-FileHash -LiteralPath $Match).Hash)) { return $true }
  }
  return $false
}
# Never copied: Git history and attendee-owned names
$Protected = @('.git', '.env', 'secrets', 'memory', '.state', 'agents.json')
# Get-Clash DIR: the first path that is a folder in the incoming skill and a file in DIR, or the other way round ($null if none)
function Get-Clash($Dir) {
  $Base = (Resolve-Path -LiteralPath $Src).ProviderPath.TrimEnd('\')
  $Queue = @($Base)
  while ($Queue.Count -gt 0) {
    $Next, $Queue = $Queue
    foreach ($Entry in @(Get-ChildItem -LiteralPath $Next -Force -ErrorAction Stop)) {
      if ($Protected -contains $Entry.Name) { continue }
      $There = Join-Path $Dir $Entry.FullName.Substring($Base.Length + 1)
      if (Test-Path -LiteralPath $There) {
        if ($Entry.PSIsContainer -ne (Test-Path -LiteralPath $There -PathType Container)) { return $Entry.FullName.Substring($Base.Length + 1) }
      }
      if ($Entry.PSIsContainer) { $Queue = @($Queue) + $Entry.FullName }
    }
    $Queue = @($Queue | Where-Object { $_ })
  }
  return $null
}
if (-not ((Test-Path -LiteralPath $Src -PathType Container) -and (Test-ThisSkill $Src))) { Write-Host "STOP: the kit folder is not there, or is not this kit: $Kit"; exit 1 }
if (Test-LinkedPath $Kit) { Write-Host "STOP: the kit folder $Kit is reached through a link. Run setup from the kit folder Loup delivered."; exit 1 }
if (@(Get-ChildItem -LiteralPath $Kit -Recurse -Force -Attributes ReparsePoint -ErrorAction SilentlyContinue).Count -gt 0) { Write-Host "STOP: the kit folder $Kit holds a link to another folder. Not copying from it."; exit 1 }
if (Test-Linked $Dest) { Write-Host "STOP: $Dest, or a folder above it such as $Skills, or something inside it, is a link. Not writing through it."; exit 1 }
if (Test-SameFolder $Src $Dest) { Write-Host "The kit folder's skill is the installed skill already, so there is nothing to copy."; exit 0 }
if (Test-Path -LiteralPath $Dest) {
  if (-not (Test-Path -LiteralPath $Dest -PathType Container)) { Write-Host "STOP: $Dest is a file, not this skill. Left alone."; exit 1 }
  if ((@(Get-ChildItem -LiteralPath $Dest -Force).Count -gt 0) -and -not (Test-ThisSkill $Dest)) { Write-Host "STOP: $Dest is not the business-carousels skill. Left alone."; exit 1 }
  try { $Clash = Get-Clash $Dest } catch { Write-Host "STOP: cannot read ${Src}: $($_.Exception.Message)"; exit 1 }
  if ($Clash) { Write-Host "STOP: $Dest\$Clash is a file where the skill has a folder, or a folder where the skill has a file. Left alone; nothing was copied."; exit 1 }
  try { $Edited = Test-Edited $Dest } catch { Write-Host "STOP: cannot read ${Dest}, so it was left alone: $($_.Exception.Message)"; exit 1 }
  if ($Edited) {
    if (Test-Linked $Saved) { Write-Host "STOP: $Saved, or a folder above it, is a link. Not writing through it."; exit 1 }
    try {
      New-Item -ItemType Directory -Force "$HOME\.loup\installed" -ErrorAction Stop | Out-Null
      Copy-Item -LiteralPath $Dest -Destination $Saved -Recurse -ErrorAction Stop
    } catch { Write-Host "STOP: could not save the earlier copy to ${Saved}: $($_.Exception.Message)"; exit 1 }
    Write-Host "SAVED: the earlier copy, with its changes, to $Saved"
  }
}
if (-not (Get-Command robocopy -ErrorAction SilentlyContinue)) { Write-Host "STOP: could not copy the skill: robocopy is not available"; exit 1 }
New-Item -ItemType Directory -Force $Skills | Out-Null
robocopy $Src $Dest /E /IS /IT /IM /A-:R /R:2 /W:2 /XD @Protected /XF @Protected /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8 -or ($LASTEXITCODE -band 4)) { Write-Host "STOP: could not copy the skill: robocopy exit code $LASTEXITCODE (8 or more is an error, 4 means a file and a folder clash)"; exit 1 }
$global:LASTEXITCODE = 0
Write-Host "COPIED: the business-carousels skill to $Dest"
```

- A `STOP:` line means the block stopped there. Show it to the attendee in plain English and fix the cause before going on; never skip it. For a folder that is not this skill, or a link, change nothing and ask the attendee what that folder is.
- A `SAVED:` line means the earlier copy had changes. Tell the attendee in one plain line where it is, that the new copy is now in use, and that they can delete the saved one once they have checked nothing of theirs is in it.

## 2. Prove it landed

Check that `<skill folder>/business-carousels` has `SKILL.md` (with `name: business-carousels` in its frontmatter), the ten pages in `references/` (`brand-and-identity.md`, `cta-and-revisions.md`, `example-prompts.md`, `examples.md`, `people.md`, `qa.md`, `slide-design.md`, `source-and-plan.md`, `style-options.md`, `tool-routes.md`) and the fifteen example images plus `index.json` in `assets/examples/`. If anything is missing, run step 1 again; do not go on until all of it is there.

Then check your own list of available skills. If `business-carousels` is not listed yet, tell the attendee to restart Claude, and that a new session will have it. That restart is the only pause here.

## 3. Tell them how to start

Tell the attendee in two plain sentences how to start a carousel: open a new session and say "Use Business Carousels" (in Claude Code they can also type `/business-carousels`; in Codex, `$business-carousels`), then share an idea, a reel's caption or transcript, a post, an article or their notes, plus who it is for and any brand files. The skill shows them a slide-by-slide plan to approve before any image is made.

## How the attendee knows it worked

Ask it to plan a carousel for a real customer question. They should get a slide-by-slide plan before any image is generated, where each slide has one clear point and every number keeps its units and context.

## If it stalls

- Say: "Check that Business Carousels has its SKILL.md, references and assets, then check which image tools you can actually use." Run step 2 again.
- If image generation is unavailable, ask for the complete image prompt for each slide instead.
- Running this setup again is safe: it refreshes the skill, keeps anything the attendee added, and saves an earlier copy that had changes before replacing it.

Using Claude in the browser or the desktop app, or ChatGPT? No setup is needed there: paste [PROMPT.md](PROMPT.md) into a chat instead, or see [QUICKSTART.md](QUICKSTART.md).
