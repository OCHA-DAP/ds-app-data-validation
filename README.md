# ds-app-data-validation

This repo holds a Dash application for basic visualization and validation of outputs from the Data Science Team data pipelines.

## Usage

Running the app locally:

1. Install the dependencies with `pip install -r requirements.txt`
2. Create a local .env file with the variables:

```
DSCI_AZ_BLOB_PROD_SAS=<provided-on-request>
DSCI_AZ_BLOB_DEV_SAS=<provided-on-request>

DSCI_AZ_DB_PROD_PW=<provided-on-request>
DSCI_AZ_DB_PROD_UID=<provided-on-request>

DSCI_AZ_DB_PROD_PW=<provided-on-request>
DSCI_AZ_DB_PROD_UID=<provided-on-request>

DSCI_AZ_DB_DEV_HOST=<provided-on-request>
DSCI_AZ_DB_PROD_HOST=<provided-on-request>

STAGE='prod' # or 'dev'
```

3. Run the app with python app.py for debugging, or gunicorn -w 4 -b 127.0.0.1:8000 app:server for production.

## Development

All code is formatted according to black and flake8 guidelines. The repo is set-up to use pre-commit. Before you start developing in this repository, you will need to run

```
pre-commit install
```

You can run all hooks against all your files using

```
pre-commit run --all-files
```

It is also strongly recommended to use jupytext to convert all Jupyter notebooks (.ipynb) to Markdown files (.md) before committing them into version control. This will make for cleaner diffs (and thus easier code reviews) and will ensure that cell outputs aren't committed to the repo (which might be problematic if working with sensitive data).
