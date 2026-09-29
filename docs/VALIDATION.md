# Validation / 検証記録

Date: 2026-09-29. **Geo3D開発者 Alex Moncks氏のopenMSXでまず確認した版**です。

## Environment

- [alexmoncks/openMSX](https://github.com/alexmoncks/openMSX), commit `de29fb854885a38251c03e24596ad4ff95770ef2` (local source checkout clean; no semantic changes).
- Executable SHA256: `ec39fbb8ec658e2358f0d824267eb9e5f2c8927e6a393c226428e58d560ae2f2`.
- Machine `Panasonic_FS-A1ST_V9968`, extension `geo3d`, ASCII16 cartridge mapping.
- Windows, SDLGL-PP renderer, NTSC machine timing, TurboR high-speed CPU mode.
- Source/spec reference: [Geo3D revision c9381505](https://github.com/alexmoncks/V9968_Cartridge/tree/c938150507f9763ac41720104135096776d9f2af/geo3d).

These are pinned evaluation versions, not a claim about the newest upstream revision.

## Release verification

1. Rebuilt all three public-source ROMs. Each is 1,048,576 bytes and matches the previously reviewed ROM SHA256.
2. Checked model limits, face vertex indices, texture-coordinate ranges and every frame's bank/HUD references using `tools/verify.py`.
3. Started all three ROMs in the above emulator and captured one full cycle. Selected frames at three points match the reviewed local versions pixel-for-pixel. Capture logs are in `validation/` next to this document.
4. Decoded complete MP4 files and every GIF frame; checked GIFs below 15,000,000 bytes and consistent duration. No audio or video speed-up.

| Demo | Captured cycle (emulated time) | Render updates/s (average) | Result |
|---|---:|---:|---|
| vector-rush | 25.637 s | 19.97 | PASS |
| skybound | 25.627 s | 19.98 | PASS |
| orbital (v0.1.1) | 18.425 s | 27.79 | PASS |

The video stream itself is approximately 59.92 fps, including repeated display frames. The table counts completed render updates, not unique encoded video frames. It is **not an FPGA benchmark**.

## What remains unverified

- Physical TurboR + V9968 + Geo3D hardware, synthesis timing and physical cartridge performance.
- blueMSX Plus, standard openMSX, other V9968-only emulators, external 88h VDP configurations, other CPU/machine types.
- Compatibility with newer upstream register/RTL changes.

The checked Geo3D emulator computes geometry without charging emulated CPU/FPGA time for that math; VDP command execution and CPU streaming are separate. Successful playback therefore establishes display/software behavior in this environment, not real hardware throughput or full hardware compatibility. The videos are demonstrations, not proof of a playable game's complete workload.

Checksums: each `validation/*-original-build.json` records the expected ROM hash; release `SHA256SUMS.txt` covers downloads. Source/build dependencies can affect reproducibility and must not be silently substituted when comparing hashes.

## v0.1.1 ORBITAL update

All 1536 pose records keep the same Moon hemisphere facing Earth (maximum fixed-point facing error below 0.2 degrees). Earth poses and lunar positions match v0.1.0 exactly. A small background UFO is present during 240 records. ORBITAL was recaptured for a full loop and the MP4/GIF revalidated; the other two demos remain byte-identical. The earlier pixel-for-pixel comparison above describes v0.1.0, before this intentional ORBITAL change.
