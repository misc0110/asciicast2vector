#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import json
import sys
from optparse import OptionParser

options = OptionParser(usage='%prog recording.json [options]', description='Converter for asciicast (asciinema recording) to vector graphic')
options.add_option('-s', '--start', type='int', default=-1, help='Start frame (default: first)')
options.add_option('-e', '--end', type='int', default=-1, help='End frame (default: last)')
options.add_option('-o', '--out', type='str', default='-', help='Filename to write vector graphic to (default: stdout)')
options.add_option('-t', '--type', type='str', default="svg", help='Vector graphic type: svg or tikz (default: svg)')
options.add_option('-b', '--background', action='store_true', default=False, help='No background')
options.add_option('-i', '--invert', action='store_true', default=False, help='Invert black and white')
options.add_option('-c', '--content', action='store_true', default=False, help='Do not add document structure (tikz only)')
options.add_option('-q', '--query', action='store_true', default=False, help='Show information about the JSON file and exit')
options.add_option('-v', '--version', action='store_true', default=False, help='Show version info and exit')


class ANSIParser:

    def __init__(self, filename, start_line = -1, max_line = -1):
        self.debug_output = False

        self.filename = filename

        with open(filename) as j:
            self.meta = json.load(j)
            
        cont = ""
        for line_nr,line in enumerate(self.meta["stdout"]):
            if start_line != -1 and line_nr < start_line: continue
            if max_line != -1 and line_nr > max_line: break
            cont += line[1]

        self.lines = [ cont ]
                    
        self.width = self.meta["width"] + 1
        self.height = self.meta["height"] + 1
        self.fgcolor = 7
        self.bgcolor = 0
        self.bold = False
        self.inverse = False
        self.charset = 0
        self.charset_enabled = False
        self.max_row = 0
        self.max_col = 0
        self.no_background = False
        self.invert_blackwhite = False
        
        self.saved_row = 0
        self.saved_col = 0
        
        self.clear = {"char": ' ', "fgcolor": 7, "bgcolor": 0, "bold": False, "inverse": False, "charset": 0}
        
        self.g1 = ["~", "◆", "▒", "␉", "␌", "␍", "␊", "°", "±", "␤", "␋", "┘", "┐", "┌", "└", "┼", "⎺", "⎻", "─", "⎼", "⎽", "├", "┤", "┴", "┬", "│", "≤", "≥", "π", "≠", "£", "·"]
        
        self.colors = [
            [1,1,1],
            [222,56,43],
            [57,181,74],
            [255,199,6],
            [0,111,184],
            [118,38,113],
            [44,181,233],
            [204,204,204],
            [128,128,128],
            [255,0,0],
            [0,255,0],
            [255,255,0],
            [0,0,255],
            [255,0,255],
            [0,255,255],
            [255,255,255]
        ]
        
        self.parse()
        
        
    def debug(self, string):
        if self.debug_output:
            print(string, file=sys.stderr)
        
        
    def appendChar(self, c):
        self.row = min(max(0, self.row), self.height - 1)
        self.col = min(max(0, self.col), self.width - 1)
        if self.charset == 1:
            idx = ord(c) - 0x5f
            if idx >= 0 and idx < len(self.g1): c = self.g1[idx] #.decode("utf8")
        self.screen[self.row][self.col] = {"char": c, "fgcolor": self.fgcolor, "bgcolor": self.bgcolor, "bold": self.bold, "inverse": self.inverse, "charset": self.charset}
        self.col += 1
        if self.col >= self.width:
            self.col = 0
            #self.row += 1
            #if self.row >= self.height:
            #    self.row = 0
        if self.row > self.max_row: self.max_row = self.row
        if self.col > self.max_col: self.max_col = self.col
                    
        
    def parseANSI(self, line):
        self.row = min(max(0, self.row), self.height - 1)
        self.col = min(max(0, self.col), self.width - 1)
        
        eoc = 0
        while eoc < len(line) and not line[eoc].isalpha() and line[eoc] != '\x1b': eoc += 1
        if eoc >= len(line): eoc = len(line) - 1
        
        #print(line)
    
        code = line[eoc]
        special = False
        if len(line) > 1 and line[1] == '?':
            special = True
            
        while eoc > 0 and not line[eoc].isalpha(): eoc -= 1
        num = (line[1:eoc] if not special else line[2:eoc])
        if len(num) > 0:
            #print("Num: %s" % num)
            if ";" in num:
                num = [int(x) if len(x) > 0 else 1 for x in num.split(";")]
            elif len(num) > 0:
                num = int(num)
        
        #print(line[0] + " / "  + code)
        
        eoc += 1
        if line[0] == '[':
            if code == 'A':
                if num == '': num = 1
                self.row -= num
                if self.row < 0: self.row = 0
            elif code == 'B':
                if num == '': num = 1
                self.row += num
                if self.row >= self.height: self.row = self.height - 1
            elif code == 'C':
                if num == '': num = 1
                self.col += num
                if self.col >= self.width: self.col = self.width - 1
            elif code == 'D':
                if num == '': num = 1
                self.col -= num
                if self.col < 0: self.col = 0
                        
            
            elif code == 'm':
                if not isinstance(num, list): num = [ num ]
                for n in num:
                    if n == '' or n == 0:
                        self.fgcolor = 7
                        self.bgcolor = 0
                        self.bold = False
                        self.inverse = False
                    elif n == 1:
                        self.bold = True
                    elif n == 7:
                        self.inverse = True
                    elif n == 22:
                        self.bold = False
                        self.inverse = False
                    elif n == 24:
                        pass
                    elif n == 27:
                        self.inverse = False
                    elif n >= 30 and n <= 37:
                        self.fgcolor = n - 30
                    elif n >= 40 and n <= 47:
                        self.bgcolor = n - 40
                    elif n == 49:
                        self.bgcolor = 0
                    elif n == 39:
                        self.fgcolor = 7
                    elif n >= 90 and n <= 97:
                        self.fgcolor = n - 90
                        self.bold = True
                    elif n >= 100 and n <= 107:
                        self.bgcolor = n - 100
                        self.bold = True
                    else:
                        self.debug("Unhandled: ^]m: %s" % str(num))
                    
            elif code == 'J':
                if num == '' or num == 0:
                    x = self.col
                    y = self.row
                    while y < self.height:
                        while x < self.width:
                            self.screen[y][x] = self.clear
                            x += 1
                        x = 0
                        y += 1
                elif num == 1:
                    x = self.col
                    y = self.row
                    while y >= 0:
                        while x >= 0:
                            self.screen[y][x] = self.clear
                            x -= 1
                        x = self.width - 1
                        y -= 1
                elif num == 2 or num == 3:
                    x = 0
                    y = 0
                    while y < self.height:
                        while x < self.width:
                            self.screen[y][x] = self.clear
                            x += 1
                        x = 0
                        y += 1
                    self.col = 0
                    self.row = 0                
                else:
                    self.debug("Unhandled: ^]J: %s" % str(num))
                        
            elif code == 'H' or code == 'f':
                if isinstance(num, list): 
                    self.row = num[0]
                    self.col = num[1]
                elif num == '':
                    self.col = 0
                    self.row = 0
                else:
                    self.col = 0
                    self.row = num
                
                
            elif code == 'd':
                self.row = num
                self.col = 1
                            
            elif code == 'G':
                if num == '':
                    self.col = 0
                else:
                    self.col = num
                        
            elif code == 'K':
                clear = dict(self.clear)
                clear["bgcolor"] = self.bgcolor
                if num == '' or num == 0:
                    for x in range(self.col, self.width): self.screen[self.row][x] = dict(clear)
                elif num == 1:
                    for x in range(self.col): self.screen[self.row][x] = dict(clear)
                elif num == 2:
                    for x in range(0, self.width): self.screen[self.row][x] = dict(clear)
                else:
                    self.debug("Unhandled: ^]K: %s" % str(num))
            
            elif code == 's':
                self.saved_col = self.col
                self.saved_row = self.row
                
            elif code == 'u':
                self.col = self.saved_col
                self.row = self.saved_row
            
            else:
                self.debug("Unhandled: ^]%s (special: %s, num: %s)" % (code, "yes" if special else "no", str(num)))
                    
            if self.row > self.max_row: self.max_row = self.row
            if self.col > self.max_col: self.max_col = self.col
        
            return eoc
                    
        elif line[0] == '=' or line[0] == '>' or line[0] == '*' or line[0] == '+' or line[0] == ',' or line[0] == '-' or line[0] == '.' or line[0] == '/':
            return 1
        
        elif line[0] == ')':
            self.charset_enabled = True
            return 2
        
        elif line[0] == '(':
            return 2
        
        elif line[0] == ']':
            while line[eoc] != '\x07': eoc += 1
            return eoc + 1
        else:
            self.debug("Unhandled: %s" % line[0])
            return eoc
        
        
    def parse(self):
        self.screen = [[self.clear for x in range(self.width)] for y in range(self.height)]
        
        self.row = 0
        self.col = 0

        for line in self.lines:
            ci = 0
            while ci < len(line):
                c = line[ci]
                if c != '\x1b':
                    if c == '\x0e' and self.charset_enabled:
                        self.charset = 1
                    elif c == '\x0f' and self.charset_enabled:
                        self.charset = 0
                    elif c == '\b':
                        if self.col > 0: self.col -= 1
                    elif c == '\r':
                        self.col = 0
                    elif c == '\n':
                        self.row += 1
                    else: 
                        self.appendChar(c)
                else:
                    ci += self.parseANSI(line[ci+1:])
                ci += 1
                if self.row > self.max_row: self.max_row = self.row
                if self.col > self.max_col: self.max_col = self.col
        
            
    def show_info(self):
        print("Frames: %d" % len(self.meta["stdout"]))
        print("Terminal (columns x rows): %d x %d" % (self.width, self.height))
        print("")
        print("asciicast version: %d" % (self.meta["version"]))
        print("Environment: %s" % str(self.meta["env"]))
        print("Duration: %.2fs" % self.meta["duration"])
    

    def dump(self):
        for line in self.screen:
            pline = ""
            for data in line: 
                pline += data["char"]
            if len(pline.strip()) > 0: print(pline)
            
            
    def sanitizeLatexChar(self, c):
        if c == '%':
            return "\%"
        if c == '~':
            return "\\textasciitilde"
        if c == '^':
            return "$\hat{}$"
        if c == "#":
            return "\\#"
        if c == '_':
            return "\\_"
        if c == '\\':
            return "\\textbackslash"
        if c == '$':
            return "\\$"
        if c == '{':
            return "\\{"
        if c == '}':
            return "\\}"
        # wtf below here
        if c == '\r' or c == '\n':
            return ''
        if c == '\b':
            return ''
        return c
    
            
    def toTikz(self, header = False, footer = False, invert_blackwhite = False, background = True):
        pline = ""
        
        if header: pline += self.tikzHeader()
        
        pline += "\\resizebox{\hsize}{!}{\\begin{tikzpicture}[yscale=-1]\\ttfamily\n"
        if background: pline += "\\draw[fill=%s,draw=none] (-1em,-1em) rectangle +(%.1fem,%dem);\n" % ("ansi7" if invert_blackwhite else "ansi0", (self.max_col + 4) / 2.0, self.max_row + 2)
        for row,line in enumerate(self.screen):
            for col,data in enumerate(line): 
                if data["char"] == ' ' and ((data["inverse"] == False and data["bgcolor"] == 0) or (data["inverse"] and data["fgcolor"] == 0)):
                    continue
                
                fg = data["fgcolor" if not data["inverse"] else "bgcolor"]
                bg = data["bgcolor" if not data["inverse"] else "fgcolor"]
                
                if invert_blackwhite:
                    if fg == 0: fg = 7
                    elif fg == 7: fg = 0
                    if bg == 0: bg = 7
                    elif bg == 7: bg = 0
                
                bgcol = "ansi%d" % bg
                
                if not background and ((not invert_blackwhite and bg == 0) or (invert_blackwhite and bg == 7)): bgcol = "none"
                
                if data["bold"] and not (invert_blackwhite and fg == 7 and not background): fg += 8
                
                pline += "\\draw[fill=%s,draw=none] (%.1fem,%dem) rectangle +(0.5em,1em) node[pos=.5, anchor=base, yshift=-0.5ex] {\\textcolor{ansi%d}{%s}};\n" % (bgcol, col / 2.0, row, fg, self.sanitizeLatexChar(data["char"]))
            
        pline += "\\end{tikzpicture}}"
        
        if footer: pline += self.tikzFooter()
        
        return pline
    
    def tikzColors(self):
        line = ""
        for i,c in enumerate(self.colors):
            line += "\\definecolor{ansi%d}{RGB}{%d,%d,%d}\n" % (i, c[0], c[1], c[2])
        return line
    
    def tikzHeader(self):
        line = "\\documentclass{article}\n"
        line += "\\usepackage[utf8]{inputenc}\n"
        line += "\\usepackage{tikz}\n"
        line += "\\usepackage{color}\n"
        line += "\\usepackage{amssymb}\n"
        line += "\\usepackage{pmboxdraw}\n"
        line += self.tikzColors()
        line += "\\begin{document}\n"
        return line
    
    def tikzFooter(self):
        return "\\end{document}\n"
    
    
    def toSVG(self, invert_blackwhite = False, background = True):
        header = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n<svg version=\"1.1\" preserveAspectRatio=\"xMinYMin meet\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" x=\"0em\" y=\"0em\" width=\"%.1fem\" height=\"%dem\" viewBox=\"0 0 %.1f %d\" font-family=\"monospace\" >\n"
        footer = "</svg>"
        
        char = "<rect x=\"%.1f\" y=\"%.1f\" width=\"1\" height=\"1\" style=\"fill:rgb(%d,%d,%d);stroke-width:0;\" /><text transform=\"translate(%.1f, %.2f)\" alignment-baseline=\"baseline\" style=\"font-size:1;fill:rgb(%d,%d,%d);\">%s</text>\n"
        char_nobg = "<text transform=\"translate(%.1f, %.2f)\" alignment-baseline=\"baseline\" style=\"font-size:1;fill:rgb(%d,%d,%d);\">%s</text>\n"

        pline = header % ((self.max_col + 4) / 2.0, self.max_row + 2, (self.max_col + 4) / 2.0, self.max_row + 2, )
        
        bcol = self.colors[0] if not invert_blackwhite else self.colors[7]
        if background: pline += "<rect width=\"%.1f\" height=\"%d\" x=\"0\" y=\"0\" style=\"fill:rgb(%d,%d,%d);stroke-width:0;\" />" % ((self.max_col + 4) / 2.0, self.max_row + 2, bcol[0], bcol[1], bcol[2])
        
        for row,line in enumerate(self.screen):
            for col,data in enumerate(line): 
                if data["char"] == ' ' and ((data["inverse"] == False and data["bgcolor"] == 0) or (data["inverse"] and data["fgcolor"] == 0)):
                    continue
                
                fg = data["fgcolor" if not data["inverse"] else "bgcolor"]
                bg = data["bgcolor" if not data["inverse"] else "fgcolor"]
                
                if invert_blackwhite:
                    if fg == 0: fg = 7
                    elif fg == 7: fg = 0
                    if bg == 0: bg = 7
                    elif bg == 7: bg = 0
                
                bgcol = self.colors[bg]
                
                if not background and ((not invert_blackwhite and bg == 0) or (invert_blackwhite and bg == 7)): bgcol = None
                
                if data["bold"] and not (invert_blackwhite and fg == 7 and not background): fg += 8
                
                if bgcol is None:
                    pline += char_nobg % (col / 2.0 - 0.1 + 1, row + .5 + 1, self.colors[fg][0], self.colors[fg][1], self.colors[fg][2], data["char"])
                else:
                    pline += char % (col / 2.0 + 1, row + 0.7, bgcol[0], bgcol[1], bgcol[2], col / 2.0 - 0.1 + 1, row + .5 + 1, self.colors[fg][0], self.colors[fg][1], self.colors[fg][2], data["char"])
                
        pline += footer
        return pline


def main():
    opts, args = options.parse_args()
    if opts.version:
        print("asciicast2vector 1.0")
        return

    if len(args) < 1:
        options.print_help()
        return
    
    try:
        p = ANSIParser(args[0], opts.start, opts.end)
    except:
        print("Could not parse '%s'" % args[0])
        return
    
    #p.dump()
    if opts.query:
        p.show_info()
        return
    
    if opts.type == "svg":
        img = p.toSVG(invert_blackwhite = opts.invert, background = not opts.background)
    elif opts.type == "tikz":
        img = p.toTikz(header = not opts.content, footer = not opts.content, invert_blackwhite = opts.invert, background = not opts.background)
    else:
        print("Unknown output format: %s" % opts.type)
        return
    if opts.out == "-":
        print(img)
    else:
        try:
            with open(opts.out, "w") as out:
                out.write(img)
        except:
            print("Could not save file '%s'" % opts.out)
            return


if __name__ == '__main__':
    main()

