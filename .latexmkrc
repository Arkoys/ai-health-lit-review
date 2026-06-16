#!/usr/bin/env perl

# LaTeXmk configuration file
# Documentation: https://ctan.math.washington.edu/tex-archive/support/latexmk/latexmk.pdf

###################
# Path Settings
###################
# Add paths for sections and other directories
ensure_path('TEXINPUTS', './sections//');  # For section files
ensure_path('TEXINPUTS', './figures//');   # For figure files
ensure_path('TEXINPUTS', './style//');     # For style files
ensure_path('BIBINPUTS', './bib//');       # For bibliography files

###################
# Engine Settings
###################
$pdf_mode = 1;        # Use pdflatex by default
$pdflatex = 'pdflatex %O -shell-escape -synctex=1 -interaction=nonstopmode -file-line-error %S';

# Enable recursive scanning for included files
$recursive_dir_scan = 1;

###################
# Clean Settings
###################
$clean_ext = 'acn acr alg aux bbl bcf fdb_latexmk fls ' .   
             'ent glo gls glg ist lof lot nav out snm ' .       
             'run.xml synctex.gz synctex(busy) thm toc vrb xdv ' .
             'gz hd loa xdy _minted-%R/* _minted-%R';

# Don't delete PDF files during cleanup
$clean_full_ext = '';

###################
# Build Settings
###################
$max_repeat = 5;

# Force directory creation if needed
system('mkdir -p sections figures style bib');
