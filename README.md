# Allure single html file builder

Tool to build allure generated folder into a single html file

## What it's doing?

After run by console command, or by call from python code, it:

1. Reads contents of allure-generated folder
2. Creates server.js file, which has all the data files inside and code to start fake XHR server
3. Patches index.html file, so it's using server.js and sinon-9.2.4.js (Taken from [here](https://sinonjs.org/)), and could be run in any browser without --allow-file-access-from-files parameter of chrome browser
4. Creates file complete.html with all files built-in in a single file

## Attention! Update!

According to this merged pull request https://github.com/allure-framework/allure2/pull/2072 Allure itself now has command line argument `--single-file` that make it produce report as a single html file. 
As for now it's not described in official allure docs, but anyway it should make this package (allure-combine) useless.
I'm encorage you to use Allure `--single-file` functionality, as it should work much better that my combiner!

## Requirements

* Python 3.6+
* You need to have your allure report folder generated (`allure generate './some/path/to/allure/generated/folder'`)

## Installation


### Install with pip

```shell
pip install allure-combine
```

or:

### Install manually

1. Clone repo

```bash
git clone git@github.com:MihanEntalpo/allure-single-html-file.git
cd allure-single-html-file
```

2. Install requirements (actually there are only BeautifulSoup)

```bash
pip install -r ./requirements.txt
python setup.py install
```

## Run as console script

If you have cloned repo, not installed module via pip, replace `allure-combine` with `python ./allure_combine/combine.py` in following commands:

1) Create complete.html file inside the allure folder itself

```bash
allure-combine ./some/path/to/allure/generated/folder
```

2) Create complete.html file inside specified folder:

```bash
allure-combine ./some/path/to/allure/generated/folder --dest /tmp
```

3) Ensure that specified dest folder exists (create if not)

```bash
allure-combine ./some/path/to/allure/generated/folder --dest /tmp/allure-2022-05-05_12-20-01/result --auto-create-folders
```

4) Remove sinon.js and server.js from allure folder after complete.html is generated:


```bash
allure-combine ./some/path/to/allure/generated/folder --remove-temp-files
```

5) If html/json files what should be utf-8 is has broken encoding, ignore errors:
```bash
allure-combine ./some/path/to/allure/generated/folder --ignore-utf8-errors
```

6) If the text content of generated HTML presents formatting issues, try this option:
```bash
allure-combine ./some/path/to/allure/generated/folder --disable-tags-escaping
```

## Import and use in python code

```shell
pip install allure-combine
```

```python
from allure_combine import combine_allure

# 1) Create complete.html in allure-generated folder
combine_allure("./some/path/to/allure/generated/folder")

# 2) Create complete.html in specified folder
combine_allure("./some/path/to/allure/generated/folder", dest_folder="/tmp")

# 3) Make sure that dest folder exists, create if not
combine_allure(
    "./some/path/to/allure/generated/folder",
    dest_folder="/tmp/allure-2022-05-05_12-20-01/result",
    auto_create_folders=True
)

# 4) Remove sinon.js and server.js from allure folder after complete.html is generated:
combine_allure(
    "./some/path/to/allure/generated/folder",
    remove_temp_files=True
)

# 5) If html/json files what should be utf-8 is has broken encoding, ignore errors:
combine_allure(
    "./some/path/to/allure/generated/folder",
    ignore_utf8_errors=True
)

# 6) If the text content of generated HTML presents formatting issues, try this option:
combine_allure(
    "./some/path/to/allure/generated/folder",
    disable_tags_escaping=True
)


```

## Integration tests

The repository contains Docker-based integration tests in `integration_tests/` that validate `allure-combine` CLI flows (including `--dest`, `--auto-create-folders`, `--remove-temp-files`, `--ignore-utf8-errors`, and `--disable-tags-escaping`).

Run full integration flow (requires Docker): build image, run tests, generate `complete.html` for each CLI variant, and validate every generated HTML in headless Chromium via Playwright.

```bash
./run_integration_tests.sh
```

Optional environment variables:

```bash
IMAGE_TAG=my-allure-itests:dev ./run_integration_tests.sh
ARTIFACTS_DIR=./tmp/allure-itests ./run_integration_tests.sh
RUN_PLAYWRIGHT_VALIDATION=0 ./run_integration_tests.sh
PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright:v1.56.1-noble ./run_integration_tests.sh
PLAYWRIGHT_VERSION=1.56.1 ./run_integration_tests.sh
```

Validate an existing HTML report directly with Playwright:

```bash
./validate_html_with_playwright.sh ./integration_tests/artifacts/complete.html
```

By default, generated reports are stored under `integration_tests/artifacts/` and variants under `integration_tests/artifacts/variants/`.

## TODO

* Functionality to open image or video in new browser tab doesn't work yet.
* Need functionality to return combined file as a string, not saving it to a file directly
* Functionality to not change source files at all, work in a read-only filesystem

## Ports to other languages:

* Javascript port: https://github.com/aruiz-caritsqa/allure-single-html-file-js
