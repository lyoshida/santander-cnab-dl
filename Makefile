zip:
	zip bin/chromedriver.zip bin/chromedriver bin/headless-chromium
	rm bin/chromedriver
	rm bin/headless-chromium
unzip:
	unzip bin/chromedriver.zip -d .