# santander-cnab-dl
Downloads CNAB retorno for a given Santander account.

The repo includes the chromium and chromedriver binaries in zip format under `/bin`

You can run `make unzip` to extract the files (Binaries are in .gitignore)

## Installation

Install Serverless
`npm install -g serverless`

Set up AWS credentials
You can find the credentials on Lastpass
`serverless config credentials`

Create a credential called `lambda`

```
[lambda]
aws_access_key_id = ***
aws_secret_access_key = ***
```

Dependencies must be installed in the project directory

`pip install module-name -t /path/to/project-dir`


## Deploy

There are 2 stages: `dev` and `prod`

Use the `dev` stage to test:
`serverless deploy --stage dev --aws-profile lambda`

Use the `prod` stage on production
`serverless deploy --stage prod --aws-profile lambda`

## Usage example

Post request:
```
{
    "agencia": "4040", # Only digits
    "conta": "338301", # Only digits
    "user": "USER",
    "senha": "PasSWorD",
    "layout": "240 - Cobrança/240/4M7L ",
    "cnab_date": "2018-10-22", # format YYYY-MM-DD
    "api_key": [api_key]  # Check last pass
}
```

The layout key can be found on Transferência de arquivos → Retorno → Consultar → Produto → Layout, after selecting "Cobrança"

## Lambda set up 

### environment variables

```
API_KEY=[api_key]
PATH=/var/task/bin:/var/task
BUCKET=[bucket_name] # example 'storage.access55.com'
ACCESS_KEY=[aws_access_key]
SECRET_KEY=[aws_secret_key]
```

### configuration

* Set the lambda maximum execution time to at least 5 minutes. If the scraper reaches the time limit, the execution will be canceled.
* Memory requirement is around 300mb. It should be set to 512mb 

## Logs

Execution logs can be found under CloudWatch -> Logs

## Notes
This repo includes the chromedriver and headless-chromium.
Due to binary sizes, we need to use a git extension to version large files
`Large files detected. You may want to try Git Large File Storage - https://git-lfs.github.com.`

## Refs

https://github.com/adieuadieu/serverless-chrome/releases
https://robertorocha.info/setting-up-a-selenium-web-scraper-on-aws-lambda-with-python/
https://github.com/ManivannanMurugavel/selenium-python-aws-lambda (This template was used to make this work)


By default, chromium headless does not allow file downloads. We need to use this `hack`
https://stackoverflow.com/questions/45631715/downloading-with-chrome-headless-and-selenium?rq=1
https://stackoverflow.com/questions/45631715/downloading-with-chrome-headless-and-selenium/51725319#51725319

