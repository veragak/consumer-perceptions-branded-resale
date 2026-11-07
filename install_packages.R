# Install the R packages used in code/ (R >= 4.2).
pkgs <- c("dplyr", "tidyr", "readr", "stringr", "zoo", "ggplot2",
          "lfe", "lmtest", "sandwich", "did", "remotes")
install.packages(setdiff(pkgs, rownames(installed.packages())))
# synthdid is not on CRAN:
if (!requireNamespace("synthdid", quietly = TRUE))
  remotes::install_github("synth-inference/synthdid")
