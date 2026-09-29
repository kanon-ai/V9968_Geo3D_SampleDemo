# Third-party notices

## Geo3D — Alex Moncks

The Geo3D protocol, reference implementation and demonstration programs informed the ROM-side setup and command streaming used here. Retain the upstream MIT notice for any portions adapted from those examples. [Full MIT notice](LICENSES/Geo3D-MIT.txt).

- Copyright (c) 2026 Alex Moncks.
- [Geo3D README license section](https://github.com/alexmoncks/V9968_Cartridge/blob/c938150507f9763ac41720104135096776d9f2af/geo3d/README.md#license)
- [Textured reference example](https://github.com/alexmoncks/V9968_Cartridge/blob/c938150507f9763ac41720104135096776d9f2af/geo3d/z80/geo3d_tex_demo.asm)

## V9968 — HRA!

V9968 design and documentation are credited to HRA!. [Upstream MIT notice](LICENSES/V9968-MIT.txt) is preserved for reference and attribution. This repository does not include the FPGA implementation or a bitstream.

- Copyright (c) 2026 HRA!.
- [Upstream](https://github.com/hra1129/V9968_Cartridge)

## External tools (not redistributed)

- openMSX: GPL-2.0 (as identified in the Geo3D fork README); some Geo3D additions have MIT SPDX headers. Use the upstream source and its per-file notices. Neither the executable, machine definitions, libraries nor system ROMs are bundled here.
- SDCC assembler/linker: external tools; see their upstream distribution notices. No compiler or runtime library is included in these hand-written Z80 ROMs.
- NumPy, Pillow, OpenCV and ffmpeg: installed separately and remain under their respective licenses. No package wheels or executable binaries are included.
- Bahnschrift: used locally to render video captions. The font file is not distributed. `CAPTION_FONT` can select a different locally licensed font.

## Original demo assets

Geometry and the compact HUD font are authored in the demo source. SKYBOUND and ORBITAL texture originals were made using a built-in AI image generation tool without reference images; prompts are included. These assets are offered under the repository MIT terms to the extent the contributors hold rights. No exclusive copyright or absence of all possible third-party claims is asserted for AI outputs.

Names of hardware, tools and their authors are used for identification and attribution, not as an endorsement claim.
