# ARC5

Arc5 mapping / parsing project


### Interviews

Convert everything doc to pdf

```find . -iname '*.docx' -type f -exec bash -c 'lowriter --convert-to pdf:writer_pdf_Export "$0"' {} \;```


Merge into one single pdf

```ls -v *.pdf | bash -c 'IFS=$'"'"'\n'"'"' read -d "" -ra x;pdfunite "${x[@]}" output.pdf'```
