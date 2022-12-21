# Solar Analyzer
### WEB app for solar power installations.    

Online version: https://energyanalyzer-3mzkf7yicq-no.a.run.app/  
running on google could with CI/CD from github repository. 

This app will load xls files from your energy company, analyze them and, based on your history, calculate which solar power installation makes more sense.  

It will show analysis between a WITH batteries and WITHOUT batteries installation and the SELL EXCESS to company option.   

This version only works with xls from "comercializadora regulada".  
Send me other companies csv or xls files and I will update it.

The web is built with streamlit and python, but there is a bug with streamlit
and auto refresh randomly the page, so you may have to upload again some files if this happens to you. Sorry about that.
I have a ticket open with streamlit trying to solve this. 
