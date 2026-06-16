\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{lightreport}[2025/02/05 Light Report Class]

% Declare class options
\DeclareOption{british}{%
  \PassOptionsToPackage{british}{babel}%
}
\DeclareOption{english}{%
  \PassOptionsToPackage{english}{babel}%
}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}

% Set english (with American spell check) as default
\ExecuteOptions{english}

\ProcessOptions\relax

\LoadClass[10pt,a4paper]{article}

%% ============================================================================
%% Package Loading
%% ============================================================================

% Basic packages
\RequirePackage[
  a4paper,
  top=3cm,
  bottom=3cm,
  left=2.5cm,
  right=2.5cm,
  headheight=2cm,
  headsep=1cm,
  footskip=1.5cm,
%   showframe
]{geometry}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{etex}
\RequirePackage[activate={true,nocompatibility}]{microtype}
\RequirePackage{linegoal}
\RequirePackage{ragged2e}
\RequirePackage{graphicx}
\RequirePackage{fancyhdr}
\RequirePackage{array}
\RequirePackage{xparse}
\RequirePackage{setspace}
\RequirePackage{titlesec}
\RequirePackage{fix-cm}
\RequirePackage{babel}  % Remove the [english] option here
\addto\captionsenglish{%
  \def\ackname{Acknowledgments}%  American spelling
}
\addto\captionsbritish{%
  \def\ackname{Acknowledgements}% British spelling
}
\RequirePackage[en-GB]{datetime2}
\DTMlangsetup[en-GB]{showdayofmonth=false}


% Math and formatting packages
% \RequirePackage{amsfonts}
\RequirePackage{upgreek}
\providecommand{\dd}{\mathop{}\!\mathrm{d}}
\providecommand{\ee}{\mathrm{e}}
\providecommand{\ii}{\mathrm{i}}
\providecommand{\jj}{\mathrm{j}}

\RequirePackage{amsmath}
\RequirePackage{bm}

\RequirePackage{siunitx}
\DeclareSIUnit\mmHg{mmHg}
\RequirePackage{nicefrac}
\RequirePackage[super,negative]{nth}

% Hyperref and URL handling (must be loaded before biblatex)
\RequirePackage[
    colorlinks,
    linkcolor=black,
    citecolor=black,
    anchorcolor=black,
    urlcolor=black,
    unicode=true
]{hyperref}
\RequirePackage{xurl}
\RequirePackage{orcidlink}


%% ============================================================================
%% Basic Configuration
%% ============================================================================

% Load configuration file
\InputIfFileExists{metadata.cfg}{}{%
    \ClassWarning{lightreport}{metadata.cfg not found.}%
}

\ProcessOptions\relax

% Font settings
% \renewcommand{\rmdefault}{ptm}
% \renewcommand{\sfdefault}{phv}
\RequirePackage{newtx}
\RequirePackage[normalem]{ulem}

% Page settings
\widowpenalty=10000
\clubpenalty=10000
\flushbottom
\sloppy

\newcommand{\shorttoday}{\ifcase\month\or Jan\or Feb\or Mar\or Apr\or May\or Jun\or Jul\or Aug\or Sep\or Oct\or Nov\or Dec\fi\space\number\year}

%% ============================================================================
%% Length Definitions
%% ============================================================================

% Title page dimensions
\newlength{\institutionlogowidth}\setlength{\institutionlogowidth}{5cm}
\newlength{\lablogowidth}\setlength{\lablogowidth}{12cm}
\newlength{\lablogoheadwidth}\setlength{\lablogoheadwidth}{6cm}
\newcommand{\setInstitutionLogoWidth}[1]{\setlength{\institutionlogowidth}{#1}}
\newcommand{\setLabLogoWidth}[1]{\setlength{\lablogowidth}{#1}}
\newcommand{\setLabLogoHeadWidth}[1]{\setlength{\lablogoheadwidth}{#1}}

% Title page spacing
\newlength{\titleabovespace}\setlength{\titleabovespace}{0.2cm}
\newlength{\titlebelowspace}\setlength{\titlebelowspace}{0.2cm}
\newlength{\authorabovespace}\setlength{\authorabovespace}{0.4cm}
\newlength{\authorbelowspace}\setlength{\authorbelowspace}{1cm}
\newlength{\dateabovespace}\setlength{\dateabovespace}{0.2cm}
\newlength{\datebelowspace}\setlength{\datebelowspace}{0.4cm}

% Caption spacing
\newlength{\@abovecaptionskip}\setlength{\@abovecaptionskip}{7\p@}
\newlength{\@belowcaptionskip}\setlength{\@belowcaptionskip}{\z@}
\setlength{\abovecaptionskip}{\@abovecaptionskip}
\setlength{\belowcaptionskip}{\@belowcaptionskip}

% Paragraph and list spacing
\setlength{\parindent}{\z@}
\setlength{\parskip}{5.5\p@}
\setlength{\footnotesep}{6.65\p@}
\setlength{\skip\footins}{9\p@ \@plus 4\p@ \@minus 2\p@}

%% ============================================================================
%% Font Size Definitions
%% ============================================================================

\renewcommand{\normalsize}{%
    \@setfontsize\normalsize\@xpt\@xipt
    \abovedisplayskip      7\p@ \@plus 2\p@ \@minus 5\p@
    \abovedisplayshortskip \z@ \@plus 3\p@
    \belowdisplayskip      \abovedisplayskip
    \belowdisplayshortskip 4\p@ \@plus 3\p@ \@minus 3\p@
}
\normalsize

\renewcommand{\small}{%
    \@setfontsize\small\@ixpt\@xpt
    \abovedisplayskip      6\p@ \@plus 1.5\p@ \@minus 4\p@
    \abovedisplayshortskip \z@ \@plus 2\p@
    \belowdisplayskip      \abovedisplayskip
    \belowdisplayshortskip 3\p@ \@plus 2\p@ \@minus 2\p@
}

% Other font sizes
\renewcommand{\footnotesize}{\@setfontsize\footnotesize\@ixpt\@xpt}
\renewcommand{\scriptsize}{\@setfontsize\scriptsize\@viipt\@viiipt}
\renewcommand{\tiny}{\@setfontsize\tiny\@vipt\@viipt}
\renewcommand{\large}{\@setfontsize\large\@xiipt{14}}
\renewcommand{\Large}{\@setfontsize\Large\@xivpt{16}}
\renewcommand{\LARGE}{\@setfontsize\LARGE\@xviipt{20}}
\renewcommand{\huge}{\@setfontsize\huge\@xxpt{23}}
\renewcommand{\Huge}{\@setfontsize\Huge\@xxvpt{28}}

%% ============================================================================
%% Section Formatting
%% ============================================================================

\titleformat{\section}
    {\large\bfseries\raggedright}{\thesection}{1em}{}[]
\titlespacing{\section}
    {0pt}{2.0ex plus 0.5ex minus 0.2ex}{1.5ex plus 0.3ex minus 0.2ex}

\titleformat{\subsection}
    {\normalsize\bfseries\raggedright}{\thesubsection}{1em}{}[]
\titlespacing{\subsection}
    {0pt}{1.8ex plus 0.5ex minus 0.2ex}{0.8ex plus 0.2ex}

\titleformat{\subsubsection}
    {\normalsize\itshape\raggedright}{\thesubsubsection}{1em}{}[]
\titlespacing{\subsubsection}
    {0pt}{1.5ex plus 0.5ex minus 0.2ex}{0.5ex plus 0.2ex}

\titleformat{\paragraph}[runin]
    {\normalsize\bfseries}{\theparagraph}{1em}{}[]
\titlespacing{\paragraph}
    {0pt}{1.5ex plus 0.5ex minus 0.2ex}{1em}

\titleformat{\subparagraph}[runin]
    {\normalsize\bfseries\itshape}{\thesubparagraph}{1em}{}[]
\titlespacing{\subparagraph}
    {2em}{1.5ex plus 0.5ex minus 0.2ex}{1em}

%% ============================================================================
%% Title Page Components
%% ============================================================================

% Logo definitions
\def\@titlelogoinst{}
\def\@titlelogolab{}
\newcommand{\titlelogoinst}[1]{\def\@titlelogoinst{#1}}
\newcommand{\titlelogolab}[1]{\def\@titlelogolab{#1}}

% Title bar commands
\newcommand{\@toptitlebar}{%
    \vskip 0.25in
    \vskip -\parskip
}

\newcommand{\@bottomtitlebar}{%
    \vskip 0.29in
    \vskip -\parskip
    \vskip 0.09in
}

% Author separator commands
\newcommand{\AuthorSepNormal}{\quad}
\newcommand{\AuthorSepWide}{\qquad}

% Initialize author storage
\def\@students{}
\def\@studentnames{}
\def\@supervisors{}
\def\@supervisornames{}

%% ============================================================================
%% Author Commands
%% ============================================================================

% Initialize author storage and counters
\newcount\@studentcount\@studentcount=0
\newcount\@supervisorcount\@supervisorcount=0

\NewDocumentCommand{\addstudent}{m m m m o}{%
    % Add to display block
    \g@addto@macro\@students{%
        \ifx\@students\@empty\else\And\fi
        #1\,\IfValueT{#5}{\orcidlink{#5}}\\
        \textit{Student}\\
        #3\\#4\\
        \href{mailto:#2}{\texttt{#2}}%
    }%
    % Increment counter
    \advance\@studentcount by 1
    % Store name in array-like macro
    \expandafter\def\csname @student@\the\@studentcount\endcsname{#1}%
    % Build name list
    \def\@studentnames{}%
    \count255=1
    \loop\ifnum\count255<\@studentcount
        \ifnum\count255=1
            \edef\@studentnames{\csname @student@\the\count255\endcsname}%
        \else
            \edef\@studentnames{\@studentnames, \csname @student@\the\count255\endcsname}%
        \fi
        \advance\count255 by 1
    \repeat
    \ifnum\@studentcount>1
        \ifnum\@studentcount>2
            \edef\@studentnames{\@studentnames,}% Add comma for lists of 3+ items
        \fi
        \edef\@studentnames{\@studentnames\space and \csname @student@\the\@studentcount\endcsname}%
    \else
        \edef\@studentnames{\csname @student@\the\@studentcount\endcsname}%
    \fi
}

\NewDocumentCommand{\addsupervisor}{m m m m o}{%
    % Add to display block
    \g@addto@macro\@supervisors{%
        \ifx\@supervisors\@empty\else\And\fi
        #1\,\IfValueT{#5}{\orcidlink{#5}}\\
        \textit{Supervision}\\
        #3\\#4\\
        \href{mailto:#2}{\texttt{#2}}%
    }%
    % Increment counter
    \advance\@supervisorcount by 1
    % Store name in array-like macro
    \expandafter\def\csname @supervisor@\the\@supervisorcount\endcsname{#1}%
    % Build name list
    \def\@supervisornames{}%
    \count255=1
    \loop\ifnum\count255<\@supervisorcount
        \ifnum\count255=1
            \edef\@supervisornames{\csname @supervisor@\the\count255\endcsname}%
        \else
            \edef\@supervisornames{\@supervisornames, \csname @supervisor@\the\count255\endcsname}%
        \fi
        \advance\count255 by 1
    \repeat
    \ifnum\@supervisorcount>1
        \ifnum\@supervisorcount>2
            \edef\@supervisornames{\@supervisornames,}% Add comma for lists of 3+ items
        \fi
        \edef\@supervisornames{\@supervisornames\space and \csname @supervisor@\the\@supervisorcount\endcsname}%
    \else
        \edef\@supervisornames{\csname @supervisor@\the\@supervisorcount\endcsname}%
    \fi
}

%% ============================================================================
%% Title Making Commands
%% ============================================================================

\renewcommand{\@maketitle}{%
    \vbox{%
        \hsize\textwidth
        \linewidth\hsize
        
        % Institution logo
        \if\@titlelogoinst\empty\else
            \begin{center}
                \includegraphics[width=\institutionlogowidth]{\@titlelogoinst}
                \vspace*{1cm}
            \end{center}
        \fi
        
        % Title section
        \vspace*{\titleabovespace}
        \@toptitlebar
        \begin{center}
            {\huge\bfseries\sffamily\scshape\@title\par}
        \end{center}
        \@bottomtitlebar
        \vspace*{\titlebelowspace}
        
        % Report type
        \begin{center}
            {\large\itshape\reportType\par}
        \end{center}
        \vspace*{\authorabovespace}
        
        % Author block
        \begin{center}
            \def\And{%
                \end{tabular}\AuthorSepNormal
                \begin{tabular}[t]{@{}c@{}}%
                \bfseries\rule{\z@}{24pt}\ignorespaces
            }%
            \def\AND{%
                \end{tabular}\AuthorSepWide
                \begin{tabular}[t]{@{}c@{}}%
                \bfseries\rule{\z@}{24pt}\ignorespaces
            }%
            \begin{tabular}[t]{@{}c@{}}%
                \bfseries\rule{\z@}{24pt}\@author
            \end{tabular}%
        \end{center}
        
        % Date and lab logo
        \vspace*{\authorbelowspace}
        \begin{center}
            \reportDate
        \end{center}
        \vspace*{\datebelowspace}
        
        \if\@titlelogolab\empty\else
            \begin{center}
                \vfill
                \includegraphics[width=\lablogowidth]{\@titlelogolab}
                \vfill
            \end{center}
        \fi
    }%
}

% Citation definition with both students and supervisors
\def\reportCitation{%
    \textbf{\@studentnames}; 
    \ifnum\@supervisorcount=1
        \textbf{\@supervisornames}\ (Supervisor)%
    \else
        \textbf{\@supervisornames}\ (Supervisors)%
    \fi.\ 
    \textit{\reportTitle}.\ \reportDateShort.\ 
    \reportType.\ \reportLab\ (\reportLabAbbrev), \reportInstitution.%
}

\renewcommand{\maketitle}{%
    \par
    \begingroup
        \renewcommand{\thefootnote}{\fnsymbol{footnote}}
        \renewcommand{\@makefnmark}{\hbox to \z@{$^{\@thefnmark}$\hss}}
        \long\def\@makefntext##1{%
            \parindent1em\noindent
            \hbox to 1.8em{\hss $\m@th ^{\@thefnmark}$}##1%
        }
        \thispagestyle{empty}
        \@maketitle
        \@thanks
    \endgroup
    \let\maketitle\relax
    \let\thanks\relax
}

\newcommand{\makereporttitle}{%
    \titlelogoinst{\reportLogoInstitution}%
    \titlelogolab{\reportLogoLab}%
    \title{\reportTitle
        \thanks{\textit{\underline{Citation}}: \reportCitation}%
    }%
    \author{%
        \@students
        \ifx\@students\@empty\else
            \ifx\@supervisors\@empty\else\And\fi
        \fi
        \@supervisors
    }%
    \maketitle
}

%% ============================================================================
%% Abstract and Graphical Abstract
%% ============================================================================

% Abstract environment
\renewenvironment{abstract}{%
    \begin{center}
        \addcontentsline{toc}{section}{Abstract}
        {\Large \bfseries \scshape Abstract}
    \end{center}
    \begin{quote}
        \setstretch{1.5}
}{%
    \end{quote}
}

% Keywords command
\def\keywordname{{\bfseries \itshape Keywords}}
\def\keywords#1{\par\addvspace\medskipamount{\rightskip=0pt plus1cm
    \def\and{\ifhmode\unskip\nobreak\fi\ $\cdot$
    }\noindent\keywordname\enspace\ignorespaces#1\par}}


% Graphical Abstract command and options
\RequirePackage{graphicx}
\RequirePackage{keyval}
\RequirePackage[font=small,labelfont=bf]{caption}

\define@key{graphabs}{landscape}[true]{\@landscapetrue}
\define@key{graphabs}{width}{\def\@graphabswidth{#1}}
\define@key{graphabs}{caption}{\def\@graphabscaption{#1}}

\newif\if@graphicalabstract\@graphicalabstractfalse
\newif\if@landscape\@landscapefalse
\def\@graphabswidth{0.8\textwidth}
\def\@graphabscaption{}

\newcommand{\graphicalabstract}[2][]{%
    \@graphicalabstracttrue
    \setkeys{graphabs}{#1}%
    \def\@graphicalabstractimage{#2}%
    \begin{samepage}
        \begin{center}
            \addcontentsline{toc}{section}{Graphical Abstract}
            {\Large \bfseries \scshape Graphical Abstract}
            \vspace{1em}
            
            \if@landscape
                \includegraphics[width=\@graphabswidth,angle=270]{\@graphicalabstractimage}
            \else
                \includegraphics[width=\@graphabswidth]{\@graphicalabstractimage}
            \fi
            
            \if\@graphabscaption\empty\else
                \captionsetup{type=figure}
                \captionsetup{style=base}
                \captionbox*{\@graphabscaption}[\textwidth]{}
            \fi
        \end{center}
    \end{samepage}
}

%% ============================================================================
%% Special Logo Commands
%% ============================================================================

\RequirePackage{hologo}

% Laboratory acronym (\LiGHT)
\DeclareRobustCommand{\LiGHT}{%
  \texorpdfstring{%
    L\kern-0.20em%
    \raisebox{0.50ex}{\scalebox{0.85}{i}}%
    G\kern-0.10em%
    \raisebox{-0.36ex}{\scalebox{0.98}{H}}%
    \kern-0.12em%
    T%
  }{LiGHT}%
}

% Template name (\LiGHTempLaTeX)
\DeclareRobustCommand{\LiGHTempLaTeX}{%
  \texorpdfstring{%
    \LiGHT%
    \kern-0.18em%
    \raisebox{-0.22ex}{\scalebox{0.82}{E}}%
    \kern-0.06em%
    M%
    \kern-0.10em%
    \raisebox{-0.22ex}{\scalebox{0.82}{P}}%
    \kern-0.06em%
    \LaTeX%
  }{LiGHTempLaTeX}%
}

% \LiGHTeX
\DeclareRobustCommand{\LiGHTeX}{%
  \texorpdfstring{%
    L\kern-0.20em%
    \raisebox{0.50ex}{\scalebox{0.85}{i}}%
    G\kern-0.10em%
    \raisebox{-0.36ex}{\scalebox{0.98}{H}}%
    \kern-0.12em%
    \TeX%
  }{LiGHTeX}%
}

\RequirePackage[export]{adjustbox}

% LiGHT logo with optional grayscale version (use \LiGHTLogo* for grayscale)
\DeclareRobustCommand{\LiGHTLogo}{%
  \texorpdfstring{%
    \@ifstar{\includegraphics[height=1.05em,valign=c]{light_logo_gray.pdf}}%
            {\includegraphics[height=1.05em,valign=c]{light_logo.pdf}}%
  }{LiGHT}%
}

% EPFL logo with optional grayscale version (use \EPFLLogo* for grayscale)
\DeclareRobustCommand{\EPFLLogo}{%
  \texorpdfstring{%
    \@ifstar{\includegraphics[height=0.65em,valign=c]{epfl_logo_gray.pdf}}%
            {\includegraphics[height=0.65em,valign=c]{epfl_logo.pdf}}%
  }{EPFL}%
}



%% ============================================================================
%% List and Paragraph Formatting
%% ============================================================================

\RequirePackage{enumerate}
\RequirePackage[inline]{enumitem}

\setlist{
    topsep=0.3ex,         % space before first item and after last item
    partopsep=0pt,        % extra space if list starts new page
    itemsep=0.2ex,        % space between items
    parsep=\parskip,      % space between paragraphs within items
    listparindent=\parindent, % paragraph indent within items
}

\setlist[enumerate]{
    topsep=0.3ex,
    itemsep=0.2ex,
    leftmargin=4em,       % increased left margin (was 2em)
    labelwidth=1.5em,     % width reserved for label
    labelsep=0.5em,       % space between label and item text
    itemindent=0em,       % item indentation
    align=left           % align label left
}

\setlist[itemize]{
    topsep=0.3ex,
    itemsep=0.2ex,
    leftmargin=4em,       % increased left margin (was 2em)
    labelwidth=1em,       % width reserved for bullet
    labelsep=1em,         % space between bullet and item text
    itemindent=0em,       % item indentation
    align=left           % align label left
}

% For nested lists, add progressive indentation
\setlist[enumerate,2]{leftmargin=3em}  % second level
\setlist[enumerate,3]{leftmargin=3em}  % third level
\setlist[itemize,2]{leftmargin=3em}    % second level
\setlist[itemize,3]{leftmargin=3em}    % third level

%% ============================================================================
%% Page Style
%% ============================================================================

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyheadoffset{0pt}
\cfoot{\thepage}

\AtBeginDocument{%
    \rhead{\reportShortTitle}%
    \lhead{\begin{picture}(0,0)
        \put(0,-10){\includegraphics[width=\lablogoheadwidth]{\reportLogoLab}}
    \end{picture}}%

    \hypersetup{
        pdftitle={\reportTitle},
        pdfauthor={\@studentnames},
        pdfsubject={\reportType},
    }
}


%% ============================================================================
%% Style Options
%% ============================================================================
\RequirePackage{kvoptions}

% First, process class options before setting up kvoptions
\DeclareOption*{\PassOptionsToPackage{\CurrentOption}{lightreport}}
\ProcessOptions\relax

% Setup the family name for the options
\SetupKeyvalOptions{
  family=lightreport,
  prefix=lightreport@
}

% Define the options
\DeclareStringOption[epfl]{style}[epfl]
\DeclareStringOption[msc-semester-project]{reporttype}[msc-semester-project]
\DeclareStringOption[light]{lab}[light]

% Process key-val options
\ProcessKeyvalOptions{lightreport}

% Handle report type
\ifdefstring{\lightreport@reporttype}{msc-semester-project}{%
    \renewcommand{\reportType}{MSc Semester Project Report}
}{%
    \ifdefstring{\lightreport@reporttype}{msc-thesis}{%
        \renewcommand{\reportType}{Master's Thesis}
    }{%
        \ifdefstring{\lightreport@reporttype}{bsc-semester-project}{%
            \renewcommand{\reportType}{BSc Semester Project Report}
        }{%
            \ifdefstring{\lightreport@reporttype}{bsc-thesis}{%
                \renewcommand{\reportType}{Bachelor's Thesis}
            }{%
                % If an invalid type is specified
                \PackageWarning{lightreport}{Unknown reporttype '\lightreport@reporttype' specified. Using MSc Semester Project Report as fallback.}
                \renewcommand{\reportType}{MSc Semester Project Report}
            }%
        }%
    }%
}

% Style selection
\ifdefstring{\lightreport@style}{epfl}{%
    \renewcommand{\reportInstitution}{EPFL}
    \renewcommand{\reportLogoInstitution}{epfl_logo.pdf}
    \setInstitutionLogoWidth{5cm}
}{%
    \ifdefstring{\lightreport@style}{harvard}{%
        \renewcommand{\reportInstitution}{EPFL}
        \renewcommand{\reportLogoInstitution}{epfl_logo.pdf}
        \setInstitutionLogoWidth{5cm}
    }{%
        % If an invalid style is specified, fallback to epfl and warn the user
        \PackageWarning{lightreport}{Unknown style '\lightreport@style' specified. Using EPFL style as fallback.}
        \renewcommand{\reportInstitution}{EPFL}
        \renewcommand{\reportLogoInstitution}{epfl_logo.pdf}
        \setInstitutionLogoWidth{5cm}
    }%
}

% Lab selection
\ifdefstring{\lightreport@lab}{light}{%
    \renewcommand{\reportLab}{Laboratory for Intelligent Global Health and Humanitarian Response Technologies}
    \renewcommand{\reportLabAbbrev}{LiGHT}
    \renewcommand{\reportLogoLab}{light_wordmark.pdf}
}{%
    \ifdefstring{\lightreport@lab}{mlo}{%
        \renewcommand{\reportLab}{Machine Learning and Optimization Laboratory}
        \renewcommand{\reportLabAbbrev}{MLO}
        \renewcommand{\reportLogoLab}{logo-mlo.png}
        % reset this length lablogoheadwidth
        \setLabLogoWidth{10cm}
        \setLabLogoHeadWidth{4cm}
    }{%
        % If an invalid lab is specified, fallback to LiGHT and warn the user
        \PackageWarning{lightreport}{Unknown lab '\lightreport@lab' specified. Using LiGHT as fallback.}
        \renewcommand{\reportLab}{Laboratory for Intelligent Global Health and Humanitarian Response Technologies}
        \renewcommand{\reportLabAbbrev}{LiGHT}
        \renewcommand{\reportLogoLab}{light_wordmark.pdf}
    }%
}
%% ============================================================================
%% Info Boxes
%% ============================================================================

% For info blocks
\RequirePackage[many]{tcolorbox}
\RequirePackage[fixed]{fontawesome5}

% Define colors for different block types
\definecolor{note-bg}{RGB}{242, 247, 255}
\definecolor{note-border}{RGB}{0, 101, 255}
\definecolor{tip-bg}{RGB}{240, 247, 242}
\definecolor{tip-border}{RGB}{26, 127, 55}
\definecolor{important-bg}{RGB}{245, 242, 255}
\definecolor{important-border}{RGB}{121, 74, 255}
\definecolor{warning-bg}{RGB}{255, 248, 230}
\definecolor{warning-border}{RGB}{154, 103, 0}
\definecolor{caution-bg}{RGB}{255, 242, 244}
\definecolor{caution-border}{RGB}{207, 34, 46}

% Create the basic info block environment
\newenvironment{infoblock}[2]{%
    \begin{tcolorbox}[
        breakable,
        enhanced,
        colback=#1,
        colframe=#2,
        arc=4mm,                % Rounded corners radius
        outer arc=4mm,          % Matching outer radius
        boxrule=1pt,
        left=10pt,              % Slightly increased padding
        right=10pt,
        top=6pt,
        bottom=6pt,
        % boxsep=0pt,
        fontupper=\sffamily,
        frame style={rounded corners=4mm}  % Ensure frame corners match
    ]%
}{%
    \end{tcolorbox}%
}

% Define specific info block types
\NewDocumentEnvironment{infonote}{+b}{%
    \begin{infoblock}{note-bg}{note-border}%
        {\sffamily\bfseries\faInfo\enskip{}NOTE}\par\medskip
        #1%
    \end{infoblock}%
}{}

\NewDocumentEnvironment{infotip}{+b}{%
    \begin{infoblock}{tip-bg}{tip-border}%
        {\sffamily\bfseries\faLightbulb\enskip{}TIP}\par\medskip
        #1%
    \end{infoblock}%
}{}

\NewDocumentEnvironment{infoimportant}{+b}{%
    \begin{infoblock}{important-bg}{important-border}%
        {\sffamily\bfseries\faExclamation\enskip{}IMPORTANT}\par\medskip
        #1%
    \end{infoblock}%
}{}

\NewDocumentEnvironment{infowarning}{+b}{%
    \begin{infoblock}{warning-bg}{warning-border}%
        {\sffamily\bfseries\faExclamationTriangle\enskip{}WARNING}\par\medskip
        #1%
    \end{infoblock}%
}{}

\NewDocumentEnvironment{infocaution}{+b}{%
    \begin{infoblock}{caution-bg}{caution-border}%
        {\sffamily\bfseries\faExclamationCircle\enskip{}CAUTION}\par\medskip
        #1%
    \end{infoblock}%
}{}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Latin abbreviations and phrases
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{xspace}     % For intelligent spacing after commands
\makeatletter              % For starred commands

% General Latin phrase formatting
\newcommand{\latin}[1]{\textit{#1}}
\newcommand{\latinabbr}[1]{{#1}}


% Common abbreviations (never italicized)
\newcommand{\ie}{\latinabbr{i.e.}\xspace}%          % id est (that is)
\newcommand{\eg}{\latinabbr{e.g.}\xspace}%          % exempli gratia (for example)
\newcommand{\cf}{\latinabbr{cf.}\xspace}%           % confer (compare)
\newcommand{\etal}{\latinabbr{et~al.}\xspace}%      % et alii (and others)
\newcommand{\vs}{\latinabbr{vs.}\xspace}%           % versus (against)
\newcommand{\etc}{\latinabbr{etc.}\xspace}%         % et cetera (and so forth)
\newcommand{\viz}{\latinabbr{viz.}\xspace}%         % videlicet (namely)
\newcommand{\nb}{\latinabbr{n.b.}\xspace}%          % nota bene (note well)
\newcommand{\ibidem}{\latinabbr{ibid.}\xspace}%     % ibidem (in the same place)
\newcommand{\ca}{\latinabbr{ca.}\xspace}%           % circa (approximately)
\newcommand{\qv}{\latinabbr{q.v.}\xspace}%          % quod vide (which see)

% Technical Latin phrases (context-dependent italics)
\newcommand{\invitro}{\@ifstar{\latin{In vitro}\xspace}{\latin{in vitro}\xspace}}
\newcommand{\invivo}{\@ifstar{\latin{In vivo}\xspace}{\latin{in vivo}\xspace}}
\newcommand{\insilico}{\@ifstar{\latin{In silico}\xspace}{\latin{in silico}\xspace}}
\newcommand{\insitu}{\@ifstar{\latin{In situ}\xspace}{\latin{in situ}\xspace}}

% Common Latin phrases (always italicized)
\newcommand{\adhoc}{\@ifstar{\latin{Ad hoc}\xspace}{\latin{ad hoc}\xspace}}
\newcommand{\apriori}{\@ifstar{\latin{A priori}\xspace}{\latin{a priori}\xspace}}
\newcommand{\aposteriori}{\@ifstar{\latin{A posteriori}\xspace}{\latin{a posteriori}\xspace}}
\newcommand{\defacto}{\@ifstar{\latin{De facto}\xspace}{\latin{de facto}\xspace}}
\newcommand{\dejure}{\@ifstar{\latin{De jure}\xspace}{\latin{de jure}\xspace}}
\newcommand{\exante}{\@ifstar{\latin{Ex ante}\xspace}{\latin{ex ante}\xspace}}
\newcommand{\expost}{\@ifstar{\latin{Ex post}\xspace}{\latin{ex post}\xspace}}
\newcommand{\perse}{\@ifstar{\latin{Per se}\xspace}{\latin{per se}\xspace}}
\newcommand{\viceversa}{\@ifstar{\latin{Vice versa}\xspace}{\latin{vice versa}\xspace}}
\newcommand{\denovo}{\@ifstar{\latin{De novo}\xspace}{\latin{de novo}\xspace}}
\newcommand{\sic}{\latin{sic}\xspace}

\makeatother

% Usage examples:
% Normal: This experiment was conducted \invitro, showing that \etc
% Capitalized: \invitro* showed that...
% The analysis was performed \denovo using standard protocols \cf Smith \etal
% Technical usage: The \invitro[adj] experiment... % (future enhancement for adjectival use)

%% ============================================================================
%% Additional Environments and Commands
%% ============================================================================

% Cross-referencing
\RequirePackage[nameinlink,noabbrev]{cleveref}
\crefname{algocf}{algorithm}{algorithms}
\Crefname{algocf}{Algorithm}{Algorithms}

% Table-related packages
\RequirePackage{booktabs}      % Professional tables
\RequirePackage{makecell}      % Multi-line table cells
\RequirePackage{multirow}      % Multiple row cells
\RequirePackage{longtable}     % Multi-page tables
\RequirePackage{threeparttable}     % Tables with notes
\RequirePackage{threeparttablex}    % Notes for longtables
\AtBeginEnvironment{tablenotes}{\small}

% \setlength{\LTpre}{\bigskipamount}
% \setlength{\LTpost}{\bigskipamount}
% \setlength{\LTcapwidth}{\textwidth}

% Additional controls for page breaking
% \setlength{\textfloatsep}{20pt plus 2pt minus 4pt}
% \setlength{\intextsep}{20pt plus 2pt minus 4pt}
% \setlength{\floatsep}{20pt plus 2pt minus 4pt}

\RequirePackage{dcolumn}
\newcolumntype{d}[1]{D{.}{.}{#1}}

% Figure and subfigure support
\RequirePackage{subcaption}

% Algorithm typesetting
\RequirePackage[ruled,vlined,algosection]{algorithm2e}


% Code and verbatim environments
\RequirePackage{fvextra}
\RequirePackage{csquotes}
\RequirePackage[section,newfloat=true]{minted}
\RequirePackage{endnotes}

% Minted code settings
\setminted{%
    linenos,
    fontsize=\small,
    breaklines,
    mathescape,
    samepage,
    frame=single,
    autogobble,
    style=algol_nu,
    breakafter=d,           % Added: better line breaks
    tabsize=4,             % Added: consistent tab size
    numbersep=5pt,         % Added: space after line numbers
    xleftmargin=15pt       % Added: consistent left margin
}

% Verbatim settings
\fvset{%
    linenos,
    fontsize=\small,
    breaklines,
    mathescape,
    samepage,
    frame=single,
    breakafter=d,          % Added: better line breaks
    tabsize=4,             % Added: consistent tab size
    numbersep=5pt          % Added: space after line numbers
}

% Counter management for figures, tables, and equations
\RequirePackage{chngcntr}
\counterwithin{figure}{section}
\counterwithin{table}{section}
\counterwithin{equation}{section}
% \counterwithin{algocf}{section}

\providecommand\pkg[1]{\href{https://ctan.org/pkg/#1}{\textsf{#1}}}
\providecommand{\BibLaTeX}{\textsc{Bib}\LaTeX}

\endinput
