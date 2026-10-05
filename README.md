# LDraw Corrector

A Python tool for applying part-specific corrections to LDraw model files.

LDraw Corrector reads `.ldr` and `.mpd` files, normalizes `.dat` part references, and applies configured rotations and position offsets to matching Type 1 part lines. The original model is left unchanged. The corrected model is saved beside it with `_corrected` added to the filename.

> This project is under development. Correction coverage is limited to the parts listed in [`corrections.json`](corrections.json). Review the output model before using it.

## Features

- Opens `.ldr` and `.mpd` files using a file selection dialog.
- Removes non-digit characters from `.dat` part names before looking up corrections. The normalized name is written to the output file.
- Supports 90°, 180°, and 270° rotations around the X, Y, and Z local axes.
- Supports per-part position offsets.
- Leaves non-`.dat` references, such as submodel names, unchanged.
- Writes a separate corrected file and preserves the original.

## Requirements

- Python 3
- Tkinter

No additional Python packages are required.

## Run

Keep `correct.py` and `corrections.json` together in the same folder.

Open a terminal in that folder and run:

**macOS**

```bash
python3 correct.py
```

**Windows**

```bash
py correct.py
```

Choose an `.ldr` or `.mpd` file in the dialog. The output will be created in the same folder as the input. For example:

```text
model.ldr
model_corrected.ldr
```

## Correction data

Corrections are stored in `corrections.json`, keyed by the normalized `.dat` filename. A correction can specify a rotation, an offset, or both:

```json
{
  "12345.dat": {
    "rotation": "Y180",
    "offset": [0, -8, 0]
  }
}
```

Rotation can also be a list. Rotations in a list are applied in the order written:

```json
{
  "12345.dat": {
    "rotation": ["X180", "Y90"],
    "offset": null
  }
}
```

Supported rotation names are `X90`, `X180`, `X270`, `Y90`, `Y180`, `Y270`, `Z90`, `Z180`, and `Z270`.

## Feedback and bug reports

Please open an [Issue](https://github.com/3205afol-prog/LDraw-Corrector/issues) to report a problem or suggest an improvement. Include:

- Your operating system and Python version
- The steps you took
- What you expected and what happened
- A short error message or screenshot, if available

Only attach an LDraw model if you are comfortable making it public. Please remove private or unnecessary model details before sharing.

## License

No license has been specified yet.
