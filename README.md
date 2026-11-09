# TFC Anvil Helper

**English** | [Русский](README.ru.md)

A helper for the anvil minigame in
[TerraFirmaCraft](https://www.curseforge.com/minecraft/mc-mods/terrafirmacraft),
a Minecraft mod.

The original program was made for the video
[TerraFirmaCraft - Anvil Helper](https://www.youtube.com/watch?v=rVMdPzjS_7s).

## Features

- **Path** tab — calculates the sequence of actions from the last three hits
  and the end coordinate.
- **End** tab — calculates the end coordinate from the hits already made, so
  you do not have to write it down manually.
- **Language selector** in the top-right corner: English (default) or Russian.

Action values: Light Hit −3, Medium Hit −6, Heavy Hit −9, Draw −15,
Punch +2, Bend +7, Upset +13, Shrink +16.

## Resource pack

The [TFC Anvil Helper](https://www.curseforge.com/minecraft/texture-packs/tfc-anvil-helper)
resource pack shows a red line at the end coordinate, which makes the anvil
easier to use.

![red line helper](assets/red_line_helper.png)

## Requirements

- Python 3.9+
- Tkinter (`tk` on Arch Linux, `python3-tk` on Debian/Ubuntu)
- Pillow (`pip install pillow`)

## Running

```bash
python3 tfctk.py
```

If Tkinter is installed in a non-standard location (for example, unpacked
locally without root), use `run.sh`, which sets the required library paths:

```bash
./run.sh
```

The interface starts in English. Pick `Русский` in the language selector to
switch to Russian. You can also set the initial language with an environment
variable:

```bash
TFC_LANG=ru ./run.sh
```

## License

GPL-3.0, see [LICENSE](LICENSE). Original author: dzhemvrot, interface
enhancements: Taeko-ar.
