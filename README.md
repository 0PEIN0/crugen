# Django CRUD Generator

### Overview
Generates django models, managers, services, serializers and api views all from a simple json definition. The idea is to generate these items just by providing a simple generator configuration and definitions, so that repetitive tasks are minimized.

### Project run prerequisites
1. This project is only tested in Ubuntu 16.04 so far. Any additional tests on other operating systems are welcomed.
2. Uses `python3` to run the generator script.

### New Django app creation with models
1. Clone the repository.
2. Run `source ~/.bash_aliases` command from terminal. Or `bash_refresh` if you are using  [`bash-helpers`](https://github.com/0PEIN0/bash-helpers) project.
3. Copy the contents from `sample_local_settings.py` file and place it in `local_settings.py` file. This `local_settings.py` file is added in gitignore, so you'll need to create this file on the cloned repository folder.
4. Update the app/model/field definition in `local_settings.py` file.
5. Run this script with at least 1 model definition in local settings file. You can run it by this command: `python3 <WHERE_REPO_WAS_CLONED>/crugen/crud_generator.py`. Here `WHERE_REPO_WAS_CLONED` means the directory path where this current repository was cloned. Or if you are using [`bash-helpers`](https://github.com/0PEIN0/bash-helpers) project, then you can just run `bash_refresh` command first then run `crugen_run` command.
6. Run `./manage.py makemigrations` and `./manage.py migrate` command in django project directory while virtual environment being active.
7. Run `./manage.py api_spec` to generate api specs.
8. Add new folder in postman collection for the newly created model CRUD.
9. Export postman collection to repository.

### Sample local settings file generator config description

1. `SYSTEM_USER_NAME` denotes the OS username, probably the one other than `root` user. This value is only used in `REPO_ROOT_PATH` location string. So if you leave it blank and override `REPO_ROOT_PATH` property value, its also file as well.
2. `REPO_ROOT_PATH` contains the disk path where repository parent path is located. For those who are using [`bash-helpers`](https://github.com/0PEIN0/bash-helpers) project, the repositories are cloned in `/home/<SYSTEM_USER_NAME>/Gitrepos` path. So that becomes the value for this field and is the default value. For others, it will be the parent directory of the location where repository was cloned.
3. `PROJECT_FOLDER_NAME` is the actual repository name. When a repository is cloned a new folder is created with the repository name inside which actual contents reside. This is that repository name.
4. `CUSTOM_MODEL_DEF` holds the dictionary for app, model definition and configs. Also this is the place to define all model properties and their own definitions.
5. `api_version` is api version which is placed in django api view method docstring. This version usage is useful to identify new api or method addition/changes for api consumers. And is recommended to let the api consumers know about changes in api implementation.
6. `app_name` is the django app name. If there is no django app is present with this name, a new django app will be created and added to django project `settings.py` file and `urls.py` file. Bear in mind that this new django app creation will be done with a customized folder structure. Use snake casing for naming convention for this property.
7. `model_name` is actual model name that we are trying to create. Use camel casing for naming convention for this property.
8. `str_property_name` is the unicode or rather `__str__` method field for the model we are generating.
9. `with_user` denotes whether or not we are trying to create api views and services with a `user` foreign key field or not. Different api view and service template is used to generate the codes based `with_user` being true or false.
10. `predefined_model_imports` contains all the additional imports that we might need for model class. If there is no such import is required, then this list will be empty. Otherwise imports lines can be added as multiple strings in list. One import line for 1 string.
11. `def` contains all the model field definition and config. Each model field has its own definition and config.
12. `__type__` is the type of model field. Can be one of these values: `str`, `txt`, `bool`, `float`, `int`, `choice`, `ref`, `many_ref`, `date`, `date_time`.

> `str` denotes 'CharField'

> `txt` denotes 'TextField'

> `bool` denotes 'BooleanField'

> `float` denotes 'DecimalField'

> `int` denotes 'IntegerField'

> `choice` denotes 'IntegerField'

> `ref` denotes 'ForeignKey'

> `many_ref` denotes 'ManyToManyField'

> `date` denotes 'DateField'

> `date_time` denotes 'DateTimeField'

There is a internal mapper that replaces these config names like `str` with proper model field types. If no map entry is found for provided type, then that name is treated as custom name and directly placed as model field type. For example usage of custom model field types, you can look into `sample_local_settings.py` file `CustomEmailField` usage.

13. `__null__` denotes whether the model field is nullable or not. If its true then both `null` and `blank` property of model will be set to true. Default `__null__` value is `False`.
14. `__help_text__` is a string that places provided help text string in the model field. Field `verbose_name` value is auto generated from field name.
15. `__extra__` is a list of additional model field properties. In the `sample_local_settings.py` file, you'll notice that `min_length=4` is added for `channel_name` model field in `__extra__` config. What this will do is to just place this `min_length=4` string in model field definition when generating the model class code. This list can hold any number of additional model field definitions. Default `__extra__` value is empty list.
16. `__ref_model__` points to the foreign key model field or many to many model field reference. Place the reference model here with app name in a string. This `__ref_model__` config is only applicable when `__type__` is `ref` or `many_ref`.
