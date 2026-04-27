# Third-Party Notices

updio includes several open-source components. This file provides notice and licensing information for these third-party materials.

## Bundled Runtime Components

### FFmpeg / FFprobe
- **Source**: [https://ffmpeg.org/](https://ffmpeg.org/)
- **Build Source**: [https://github.com/GyanD/codexffmpeg](https://github.com/GyanD/codexffmpeg)
- **License**: LGPL v2.1 (or GPL depending on build). See `third-party-licenses/ffmpeg/LICENSE`.
- **Note**: Used for video frame extraction and final assembly.

### Real-ESRGAN
- **Source**: [https://github.com/xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- **NCNN Executable**: [https://github.com/nihui/realesrgan-ncnn-vulkan](https://github.com/nihui/realesrgan-ncnn-vulkan)
- **License**: BSD 3-Clause (Real-ESRGAN) / MIT (ncnn-vulkan wrapper).
- **Note**: Provides AI upscaling models and execution engine.

### Real-CUGAN
- **Source**: [https://github.com/nihui/realcugan-ncnn-vulkan](https://github.com/nihui/realcugan-ncnn-vulkan)
- **License**: MIT.
- **Note**: Provides specialized anime/video upscaling models.

## Libraries and Frameworks

- **Next.js / React**: MIT License
- **Tauri**: MIT or Apache-2.0
- **Lucide React**: ISC License
- **i18next**: MIT License
- **Tailwind CSS**: MIT License

## Licensing and Compliance

Release packages include a `third-party-licenses/` directory containing the full license text for these components where required. If you have questions regarding the use of these components, please refer to the respective upstream project documentation.
