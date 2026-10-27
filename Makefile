# make          figures, deck, and the five speaker-notes PDFs
# make deck     deck only
# make clean    remove LaTeX build files
NOTES := $(basename $(notdir $(wildcard notes/notes_*.tex)))

all: deck $(addprefix notes/,$(addsuffix .pdf,$(NOTES)))

figs:
	python3 scripts/make_figs.py

deck: figs
	lualatex -interaction=nonstopmode -halt-on-error deck.tex >/dev/null
	lualatex -interaction=nonstopmode -halt-on-error deck.tex >/dev/null

notes/%.pdf: notes/%.tex notes/speakernotes.sty deck.pdf
	cd notes && lualatex -interaction=nonstopmode -halt-on-error $*.tex >/dev/null
	cd notes && lualatex -interaction=nonstopmode -halt-on-error $*.tex >/dev/null

clean:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb notes/*.aux notes/*.log notes/*.out

.PHONY: all figs deck clean
