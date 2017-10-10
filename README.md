## asciicast2vector

Convert asciicast ([asciinema](https://github.com/asciinema/asciinema) recordings) to vector graphics (SVG and TikZ).

![nano demo](https://raw.github.com/misc0110/asciicast2vector/master/screenshots/demo.png)

# Usage

Running asciicast2vector without arguments shows the following help:
```
Usage: asciicast2vector.py recording.json [options]

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

Without paramaters, asciicast2vector combines all frames, from the first to the last, and generates an SVG. 
To render only certain frames, the `-s` and `-e` parameters can be used. 
For example, to render frame 10 to 12, run `python asciicast2vector.py recording.json -s 10 -e 12 > output.svg`.

## SVG

The default output format is SVG. The resulting image can be directly used in browsers, or further modified using vector drawing programs (e.g., Inkscape).

## TikZ

asciicast2vector can also output the image as LaTeX TikZ drawings. Per default, the output is a standalone LaTeX document which can be compiled using `pdflatex`. 

To output the picture only (without the document structure), use the `-c` parameter: `python asciicast2vector.py recording.json -t tikz -c > output.tikz`.
Bear in mind that you require a definition for the colors `ansi0` to `ansi15` if you do not output the full document. 