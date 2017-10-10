## asciinema2vector

Convert [asciinema](https://github.com/asciinema/asciinema) recordings to vector graphics (SVG and TikZ).

![nano demo](https://raw.github.com/misc0110/asciinema2terminal/master/screenshots/demo.svg)

# Usage

Running asciinema2vector without arguments shows the following help:
```
Usage: asciinema2vector.py recording.json [options]

Converter for asciinema recording to vector graphic

Options:
  -h, --help            show this help message and exit
  -s START, --start=START
                        Start frame (default: first)
  -e END, --end=END     End frame (default: last)
  -o OUT, --out=OUT     Filename to write vector graphic to (default: stdout)
  -t TYPE, --type=TYPE  Vector graphic type: svg or tikz (default: svg)
  -b, --background      No background
  -i, --invert          Invert black and white
  -c, --content         Do not add document structure (tikz only)
  -q, --query           Show information about the JSON file and exit
```

