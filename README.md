# VEIN – Hungarian Translation Toolkit

A self-contained kit to translate **VEIN** (Unreal Engine 5) into Hungarian and
build a ready-to-use `.pak`. It overwrites the game's **English (`en`)** locale
slot, so run the game in English to see the translation.

**Requirements:** Python 3 (from [python.org](https://www.python.org/) – tick
*"Add Python to PATH"* during install). Nothing else; only the standard library
is used. Windows only (uses Steam auto-detection).

---

## Files

| File | Purpose |
|---|---|
| **`translate.csv`** | ⭐ The translation memory. Columns: `ns, key, en, hu`. **This is the file to keep / hand over.** |
| `Game.locres` | The game's current **English** source (auto-extracted). Do not edit by hand. |
| `getlocres.bat` | Pull the current `Game.locres` from the game **and** refresh `translate.csv`. |
| `build.bat` | Build **`VEIN_HUN.pak`** from `translate.csv` + `Game.locres`. |
| `find.bat` | Search `translate.csv` for an English or Hungarian phrase. |
| `to_translate.csv` | Auto-generated: only the rows that still need work (new / changed). |
| `config.txt` | Optional game path (leave empty to auto-detect Steam). |
| `scripts\` | The Python code (nothing to touch here). |

---

## First time / everyday use

1. **Get the game text** – double-click **`getlocres.bat`**.
   It finds VEIN via Steam, extracts `Game.locres`, and creates/updates
   `translate.csv`. It prints how many rows still need translation.
2. **Translate** – open `translate.csv` in Excel / LibreOffice / a text editor
   and edit the **`hu`** column. Untranslated rows have `hu` = the English text.
   - Leave `ns`, `key`, `en` untouched.
   - Keep placeholders as-is: `{Value}`, `{OnOrOff}`, `${Dollars}`, rich-text tags.
   - Line breaks are written as the literal text `\r\n` – keep them that way.
   - Tip: `to_translate.csv` lists exactly the rows that need work.
   - To find a specific string: `find.bat "Turn On"`
3. **Build the pak** – double-click **`build.bat`** → produces `VEIN_HUN.pak`.

## Install the translation into the game

Copy **`VEIN_HUN.pak`** into:
```
...\steamapps\common\Vein\Vein\Content\Paks\
```
Start the game **in English**. If the translation does not show up, rename the
file to **`VEIN_HUN_P.pak`** (the `_P` suffix gives it top load priority).

---

## ⭐ When the game updates (new VEIN version) – no need to start over

1. Double-click **`getlocres.bat`** again.
   It re-extracts the new English text and rewrites `translate.csv`, **reusing
   every existing Hungarian translation**:
   - same key & English → kept;
   - a moved/renamed key with the same English → reused automatically;
   - a string whose English changed → old Hungarian kept but **flagged** for review;
   - a brand-new string → left English and **flagged**.
   Flagged rows are collected in **`to_translate.csv`**, and new rows are appended
   at the end of `translate.csv`. Strings removed from the game are dropped.
2. Translate only the handful of rows in `to_translate.csv` (edit `translate.csv`).
3. Double-click **`build.bat`** → new `VEIN_HUN.pak`.

So a game update usually means translating only a few dozen new/changed lines;
the thousands of existing translations carry over automatically.

---

## Notes / limitations

- `translate.csv` is saved as UTF-8 **with BOM** (so Excel shows accents), and
  line breaks are stored as literal `\r` `\n` `\t` so each entry stays on one row.
- The output pak is UE **v3**, uncompressed – UE happily loads older-version mod
  paks. Its internal path is
  `../../../Vein/Content/Localization/Game/en/Game.locres`.
- The extractor reads the shipped VEIN pak (v11, unencrypted index, uncompressed
  files). If a future update **compresses or encrypts** the locres, `getlocres.bat`
  will say so – then unpack `Game.locres` manually (e.g. FModel or repak), drop it
  in this folder, and run `build.bat`.
- Some in-game labels come from the **asset name**, not from the locres (e.g. a
  machine that shows "Sawmill"). Those cannot be changed by a localization pak –
  only by editing the actual game asset – so they are out of scope for this kit.
