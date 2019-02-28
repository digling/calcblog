# calcblog
Repository for code and data for generating presentable PDFs from CALC's blog

## How to use

Please note that PDF generation is currently failing because I need to
write code to download images locally (no other way of using `xelatex`, as
the `.latex` files will also need some minor postprocessing).

```
python3 process.py
pandoc -o calc2018.odt output.md

pandoc -s -o calc2018.latex output.md
xelatex calc2018.latex
```
