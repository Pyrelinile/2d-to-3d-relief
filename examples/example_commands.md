# Example commands

```bash
relief relief --input portrait.jpg --output out/portrait.stl --width-mm 140 --mesh-res 384 --export-heightmap out/heightmap.png
relief plan --input portrait.jpg --output-dir out --strategy tdblend --filaments examples/sample_filaments.yaml --gcode-style m600 --slicer prusaslicer
relief pipeline --input portrait.jpg --output-dir out --config examples/config_example.yaml
relief inspect --input portrait.jpg --filaments examples/sample_filaments.yaml --palette examples/sample_palette.json
```
