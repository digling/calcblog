## Create e-books in multiple formats

# Variables

BOOKNAME = calcblog

# Default targets

## all   : Generate all supported document types (updated files only)

all: html epub docx latex

## clean : Delete all generated files

clean: html_clean epub_clean docx_clean latex_clean

# `make help` displays all lines beginning with two hash signs

help : Makefile
	@sed -n 's/^##//p' $<

# Build targets

## html  : Generate an HTML file.

html: $(BOOKNAME).html

html_clean:
	rm -f $(BOOKNAME).html

$(BOOKNAME).html: $(BOOKNAME).md style.css
	pandoc $(BOOKNAME).md \
	-t html \
	-o $(BOOKNAME).html \
	--css="style.css" \
	--table-of-contents \
	--section-divs \
	--standalone

## epub  : Generate an EPUB file.

epub: $(BOOKNAME).epub

epub_clean:
	rm -f $(BOOKNAME).epub

$(BOOKNAME).epub: $(BOOKNAME).md images/cover.jpg style-epub.css
	pandoc $(BOOKNAME).md \
	-t epub \
	-o $(BOOKNAME).epub \
	--epub-cover-image="images/cover.jpg" \
	--css="style-epub.css" \
	--standalone

## latex : Generate a latex file.

latex: $(BOOKNAME).tex

latex_clean:
	rm -f $(BOOKNAME).tex

$(BOOKNAME).tex: $(BOOKNAME).md 
	pandoc $(BOOKNAME).md \
	-s \
	-o $(BOOKNAME)_firstpass.tex \
	-V documentclass=scrbook \
	-V indent \
	-V subparagraph \
	-V fontfamily="libertine" \
	-V fontfamilyoptions="oldstyle,proportional" \
	-V papersize=a4 \
	--top-level-division=part \
	--pdf-engine=lualatex \
	--table-of-contents

	sed -e 's/caption{{\\textbf{\(.*\)}/caption{\1/' calcblog_firstpass.tex > calcblog.tex
	rm calcblog_firstpass.tex

## docx  : Generate a Word file.

docx: $(BOOKNAME).docx

docx_clean:
	rm -f $(BOOKNAME).docx

$(BOOKNAME).docx: $(BOOKNAME).md style.docx
	pandoc $(BOOKNAME).md \
	-o $(BOOKNAME).docx \
	--reference-doc=style.docx \
	--table-of-contents

# Actions that do not correspond to files

.PHONY: help html docx epub html_clean docx_clean epub_clean latex latex_clean
