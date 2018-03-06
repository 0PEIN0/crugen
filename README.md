# Django CRUD Generator

### New Django app creation with models
1. Clone the repository.
2. Copy the contents from `sample_local_settings.py` file and place it in `local_settings.py` file. This `local_settings.py` file is added in gitignore, so you'll need to create this file on the cloned repository folder.
3. Update the app/model/field definition in `local_settings.py` file.
4. Run this script with at least 1 model definition in local settings file. You can run it by this command: `python3 <WHERE_REPO_WAS_CLONED>/crugen/crud_generator.py`. Here `WHERE_REPO_WAS_CLONED` means the directory path where this current repository was cloned. Or if you are using [bash-helpers](https://github.com/0PEIN0/bash-helpers), then you can just run `bash_refresh` command first then run `crugen_run` command.
