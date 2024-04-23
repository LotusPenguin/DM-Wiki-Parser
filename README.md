# DM-Wiki-Parser
bs4-based Python3.10 scrapper and parser for MSE-DM - a [Magic Set Editor](https://github.com/twanvl/MagicSetEditor2) fork for the game [Duel Masters](https://duelmasters.fandom.com/wiki/Duel_Masters_Wiki)

Image upscaling and processing powered by [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN/)

The script-embedded version of the upscaler currently works well only with CUDA GPUs. Intel IrisXe support might be added at a later date, but as of now it requires many code changes to [the outsourced model](https://github.com/xinntao/Real-ESRGAN/).

Roadmap:
- [x] Basic set parsing capabilities - 16.03.2024
- [x] [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN/) integration for image upscaling - 23.04.2024
- [ ] Basic CLI Interface
- [ ] First alpha release as ncnn package
- [ ] Hash-based image indexing/data structures to reduce redundant processing
- [ ] GUI
- [ ] Splitting code into GUI-functionality modules
- [ ] Image selection interface
