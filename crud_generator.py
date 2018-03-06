import os
import re


class DjangoCrudGenerator(object):
    CONFIG = {
        'SYSTEM_USER_NAME': 'ubuntu',
        'REPO_ROOT_PATH': '/home/{user_name}/Desktop',
        'FIELD_TYPE_MAP': {
            'str': 'CharField',
            'txt': 'TextField',
            'bool': 'BooleanField',
            'float': 'DecimalField',
            'int': 'IntegerField',
            'choice': 'IntegerField',
            'ref': 'ForeignKey',
            'many_ref': 'ManyToManyField',
            'date': 'DateField',
            'date_time': 'DateTimeField',
        },
        'EXCLUDED_ADMIN_PANEL_SEARCH_FIELDS': ['ManyToManyField', 'ForeignKey', 'DateField', 'DateTimeField'],
        'ADMIN_PANEL_LIST_DISPLAY_FIELD_LIMIT': 3,
    }

    def __init__(self,
                 local_settings):
        self.CONFIG['CUSTOM_MODEL_DEF'] = local_settings['CUSTOM_MODEL_DEF']
        self.CONFIG['PROJECT_FOLDER_NAME'] = local_settings['PROJECT_FOLDER_NAME']
        if self.CONFIG['PROJECT_FOLDER_NAME'] is None or self.CONFIG['PROJECT_FOLDER_NAME'] == '':
            raise Exception('Project name can not be null or empty.')
        project_name = self.CONFIG['PROJECT_FOLDER_NAME']
        self.CONFIG['CUSTOM_MODEL_DEF']['project_name'] = project_name
        for key, value in local_settings.items():
            self.CONFIG[key] = value
        self.CONFIG['REPO_ROOT_PATH'] = self.CONFIG['REPO_ROOT_PATH'].format(
            user_name=self.CONFIG['SYSTEM_USER_NAME'])
        self.PROJECT_NAME = project_name
        self.PROJECT_PATH = '{prefix}/{project_name}'.format(
            prefix=self.CONFIG['REPO_ROOT_PATH'],
            project_name=self.PROJECT_NAME)
        if self.CONFIG['CUSTOM_MODEL_DEF'].get('is_second_depth', None) is None:
            self.CONFIG['CUSTOM_MODEL_DEF']['is_second_depth'] = False
        if self.CONFIG['CUSTOM_MODEL_DEF']['is_second_depth'] is True:
            self.PROJECT_PATH = '{prefix}/{project_name}'.format(
                prefix=self.PROJECT_PATH,
                project_name=self.PROJECT_NAME)
        for key, value in local_settings.items():
            self.CONFIG[key] = value

    def _write_on_file_force(self,
                             dir_path,
                             file_content):
        file_obj = open(dir_path, 'w')
        file_obj.write(file_content)
        file_obj.close()

    def _read_file(self,
                   dir_path):
        try:
            file_obj = open(dir_path, 'r')
            file_content = file_obj.read()
            file_obj.close()
        except Exception as ex:
            raise Exception('FATAL ERROR: error occured during reading a file. File path: {dir_path}'.format(
                dir_path=dir_path))
        return file_content

    def _read_file_lines(self,
                         dir_path):
        file_obj = open(dir_path, 'r')
        file_content = file_obj.readlines()
        file_obj.close()
        return file_content

    def _check_and_create_dir(self,
                              dir_path):
        if os.path.isdir(dir_path) is False:
            os.makedirs(dir_path)

    def _check_and_create_file(self,
                               file_path):
        if os.path.exists(file_path) is False:
            os.mknod(file_path)

    def _create_module_init(self,
                            dir_path):
        file_path = '{dir_path}/__init__.py'.format(dir_path=dir_path)
        self._check_and_create_file(file_path=file_path)

    def _create_urls_file(self,
                          dir_path):
        file_path = '{dir_path}/urls.py'.format(dir_path=dir_path)
        self._check_and_create_file(file_path=file_path)

    def _create_apps_file(self,
                          dir_path,
                          single_model_def):
        file_path = '{dir_path}/apps.py'.format(dir_path=dir_path)
        self._check_and_create_file(file_path=file_path)
        app_name_camel_case = self._camel_case_word_split(
            source_string=self._convert_from_snake_to_camel(source_string=single_model_def['app_name']))
        app_name_camel_case = ' '.join(app_name_camel_case)
        context = {
            'app_name': single_model_def['app_name'],
            'app_name_camel_case': app_name_camel_case,
        }
        self._write_template_file(template_file_name='django_apps_file_template.j2',
                                  context=context,
                                  destination_file_path=file_path)

    def _perform_module_operations(self,
                                   dir_path):
        self._check_and_create_dir(dir_path=dir_path)
        self._create_module_init(dir_path=dir_path)

    def _camel_case_word_split(self,
                               source_string):
        matches = re.finditer(
            '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', source_string)
        return [m.group(0) for m in matches]

    def _convert_from_camel_to_snake(self,
                                     source_string):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', source_string)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _convert_from_snake_to_camel(self,
                                     source_string):
        components = source_string.split('_')
        return components[0].title() + ''.join(x.title() for x in components[1:])

    def _set_missing_definition_properties(self,
                                           model_def):
        model_def['model_file_name'] = self._convert_from_camel_to_snake(
            source_string=model_def['model_name'])
        custom_file_configs = {
            'model_file_path': '{prefix}/{app_name}/models/{file_name}.py',
            'admin_panel_class_file_path': '{prefix}/{app_name}/admin/{file_name}.py',
            'service_file_path': '{prefix}/{app_name}/services/{file_name}.py',
            'create_update_serializer_file_path': '{prefix}/{app_name}/rest_api/serializers/{file_name}_create_update.py',
            'output_serializer_file_path': '{prefix}/{app_name}/rest_api/serializers/{file_name}_output.py',
            'create_list_views_file_path': '{prefix}/{app_name}/rest_api/views/{file_name}_create_list.py',
            'fetch_update_delete_views_file_path': '{prefix}/{app_name}/rest_api/views/{file_name}_fetch_update_delete.py',
            'serializer_init_file_path': '{prefix}/{app_name}/rest_api/serializers/__init__.py',
            'admin_init_file_path': '{prefix}/{app_name}/admin/__init__.py',
            'service_init_file_path': '{prefix}/{app_name}/services/__init__.py',
            'model_init_file_path': '{prefix}/{app_name}/models/__init__.py',
            'constants_init_file_path': '{prefix}/{app_name}/constants/__init__.py',
            'views_init_file_path': '{prefix}/{app_name}/rest_api/views/__init__.py',
            'app_urls_file_path': '{prefix}/{app_name}/rest_api/urls.py',
            'project_settings_file_path': '{prefix}/{project_name}/settings.py',
            'project_urls_file_path': '{prefix}/{project_name}/urls.py',
            'project_messages_file_path': '{prefix}/rest/messages.py',
            'model_field_constant_file_path': '{prefix}/{app_name}/constants/',
        }
        for key, value in custom_file_configs.items():
            model_def[key] = value.format(
                prefix=self.PROJECT_PATH,
                app_name=model_def['app_name'],
                project_name=model_def['project_name'],
                file_name=model_def['model_file_name'])
        name_word_list = self._camel_case_word_split(
            source_string=model_def['model_name'])
        model_def['model_name_spaces'] = ' '.join(name_word_list)
        model_def['model_name_spaces_lower_case'] = name_word_list[0] + ' ' + \
            ' '.join(name_word_list[1:]).lower()
        if model_def.get('str_property_name', None) is None:
            model_def['str_property_name'] = 'id'
        if model_def.get('with_user', None) is None:
            model_def['with_user'] = False
        model_field_name_list = []
        for key, value in model_def['def'].items():
            model_field_name_list.append(key)
            try:
                value['__type__'] = self.CONFIG['FIELD_TYPE_MAP'][value['__type__']]
                value['__type_val__'] = 'models.' + value['__type__']
            except Exception as ex:
                value['__type_val__'] = value['__type__']
            if value.get('__extra__', None) is None:
                value['__extra__'] = []
            if value.get('__null__', None) is None:
                value['__null__'] = False
            value['__verbose_name__'] = ' '.join(self._camel_case_word_split(source_string=self._convert_from_snake_to_camel(
                source_string=key)))
        if model_def['str_property_name'] not in model_field_name_list:
            raise Exception(
                '`str_property_name` field name is not present in model field definition. Please correct this value in the definition.')
        return model_def

    def _to_space_seperated_words(self,
                                  source_string):
        destination_string = ''
        return destination_string

    def _process_template(self,
                          template_content,
                          context):
        file_content = template_content
        for key, value in context.items():
            new_key = '{{' + key + '}}'
            while new_key in file_content:
                file_content = file_content.replace(new_key, value)
        return file_content

    def _process_template_file(self,
                               template_file_name,
                               context):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = os.path.join(dir_path, 'templates', template_file_name)
        file_content = self._read_file(dir_path=dir_path)
        file_content = self._process_template(template_content=file_content,
                                              context=context)
        return file_content

    def _process_template_file_only_first_line(self,
                                               template_file_name,
                                               context):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = os.path.join(dir_path, 'templates', template_file_name)
        file_content = self._read_file_lines(dir_path=dir_path)
        file_content = file_content[0].replace('\n', '')
        file_content = self._process_template(template_content=file_content,
                                              context=context)
        return file_content

    def _write_template_file(self,
                             template_file_name,
                             context,
                             destination_file_path):
        file_content = self._process_template_file(template_file_name=template_file_name,
                                                   context=context)
        self._write_on_file_force(dir_path=destination_file_path,
                                  file_content=file_content)

    def _check_and_write_export_template_file(self,
                                              template_file_name,
                                              context,
                                              destination_file_path):
        file_content = self._process_template_file_only_first_line(template_file_name=template_file_name,
                                                                   context=context)
        init_file_lines = self._read_file_lines(dir_path=destination_file_path)
        found = False
        for line in init_file_lines:
            if file_content in line:
                found = True
                break
        if found is False:
            init_file_lines.append(file_content + '\n')
            init_file_content = ''.join(init_file_lines)
            self._write_on_file_force(dir_path=destination_file_path,
                                      file_content=init_file_content)
        return file_content

    def _check_and_write_admin_export_template_file(self,
                                                    template_file_name,
                                                    context,
                                                    destination_file_path):
        file_content = self._process_template_file(template_file_name=template_file_name,
                                                   context=context)
        file_content = file_content.split('\n')
        init_file_lines = self._read_file_lines(dir_path=destination_file_path)
        write_on_file = False
        for item in file_content:
            if item == '':
                continue
            found = False
            for line in init_file_lines:
                if item in line:
                    found = True
                    write_on_file = True
                    break
            if found is False:
                init_file_lines.append(item + '\n')
        if write_on_file is True:
            init_file_content = ''.join(init_file_lines)
            self._write_on_file_force(dir_path=destination_file_path,
                                      file_content=init_file_content)

    def _generate_constant_class(self,
                                 field_name,
                                 choices,
                                 single_model_def):
        res = []
        cn = 0
        choice_static_field_list = ''
        choice_list = ''
        for item in choices:
            item_upper = item.upper().replace(' ', '_')
            res.append(item_upper)
            context = {
                'choice_name_upper': item_upper,
                'choice_value': str(cn),
            }
            file_content = self._process_template_file(template_file_name='constant_class_single_static_field_template.j2',
                                                       context=context)
            choice_static_field_list += file_content
            context = {
                'choice_name_upper': item_upper,
                'choice_name_spaces': item,
            }
            file_content = self._process_template_file(template_file_name='constant_class_single_choice_field_template.j2',
                                                       context=context)
            choice_list += file_content
            cn += 1
        context = {
            'field_name_camel': self._convert_from_snake_to_camel(source_string=field_name),
            'choice_static_field_list': choice_static_field_list,
            'choice_list': choice_list,
        }
        self._write_template_file(template_file_name='constant_class_template.j2',
                                  context=context,
                                  destination_file_path='{prefix}{model_field_name}.py'.format(prefix=single_model_def['model_field_constant_file_path'], model_field_name=field_name))
        context = {
            'model_file_name': field_name,
            'class_name_suffix_part_underscored': '',
            'model_name': self._convert_from_snake_to_camel(source_string=field_name),
            'class_name_suffix_part': '',
        }
        file_content = self._check_and_write_export_template_file(template_file_name='export_file_class_name_template.j2',
                                                                  context=context,
                                                                  destination_file_path=single_model_def['constants_init_file_path'])
        single_model_def['model_additional_imports'] += file_content.replace(
            '.', '{app_name}.constants.'.format(app_name=single_model_def['app_name']))
        return res

    def _compute_model_body(self,
                            single_model_def):
        model_body = ''
        single_model_def['model_additional_imports'] = ''
        for key, value in single_model_def['def'].items():
            other_properties = []
            context_list = []
            if value['__null__'] is True:
                context_list.append({
                    'property': 'null',
                    'value': 'True',
                })
                context_list.append({
                    'property': 'blank',
                    'value': 'True',
                })
            if value.get('__ref_model__', None) is not None:
                context_list.append({
                    'property': 'to',
                    'value': '\'' + value['__ref_model__'] + '\'',
                })
            if value.get('__choices__', None) is not None:
                choices = value['__choices__'].split(',')
                choices = self._generate_constant_class(field_name=key,
                                                        choices=choices,
                                                        single_model_def=single_model_def)
                context_list.append({
                    'property': 'choices',
                    'value': '{field_name_camel}.choices'.format(field_name_camel=self._convert_from_snake_to_camel(source_string=key)),
                })
                context_list.append({
                    'property': 'default',
                    'value': '{field_name_camel}.{default}'.format(field_name_camel=self._convert_from_snake_to_camel(source_string=key),
                                                                   default=choices[0]),
                })
            for property_name, property_value in value.items():
                if '__' not in property_name:
                    context_list.append({
                        'property': property_name,
                        'value': property_value,
                    })
            for item in value['__extra__']:
                property_name = item.split('=')[0]
                property_value = item.split('=')[1]
                context_list.append({
                    'property': property_name,
                    'value': property_value,
                })
            for context in context_list:
                file_content = self._process_template_file_only_first_line(template_file_name='model_property_template.j2',
                                                                           context=context)
                other_properties.append(file_content)
            if len(other_properties) > 0:
                other_properties = '\n' + '\n'.join(other_properties)
            else:
                other_properties = '\n'.join(other_properties)
            context = {
                'model_field_name': key,
                'model_field_type': value['__type_val__'],
                'verbose_name': value['__verbose_name__'],
                'help_text': value['__help_text__'],
                'other_properties': other_properties,
            }
            file_content = self._process_template_file(template_file_name='model_field_template.j2',
                                                       context=context)
            model_body = model_body + file_content
        return model_body

    def _prepare_model_file_content(self,
                                    single_model_def):
        single_model_def['model_body'] = self._compute_model_body(
            single_model_def=single_model_def)
        additional_imports = single_model_def['model_additional_imports']
        context = {
            'app_name': single_model_def['app_name'],
            'model_name': single_model_def['model_name'],
            'model_body': single_model_def['model_body'],
            'model_file_name': single_model_def['model_file_name'],
            'model_name_spaces': single_model_def['model_name_spaces'],
            'model_name_spaces_lower_case': single_model_def['model_name_spaces_lower_case'],
            'str_property_name': single_model_def['str_property_name'],
            'additional_imports': additional_imports,
        }
        self._write_template_file(template_file_name='model_template.j2',
                                  context=context,
                                  destination_file_path=single_model_def['model_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'class_name_suffix_part_underscored': '',
            'model_name': single_model_def['model_name'],
            'class_name_suffix_part': '',
        }
        self._check_and_write_export_template_file(template_file_name='export_file_class_name_template.j2',
                                                   context=context,
                                                   destination_file_path=single_model_def['model_init_file_path'])
        print('INFO: checked/updated model class for the model.')

    def _prepare_service_class_file_content(self,
                                            single_model_def):
        context = {
            'app_name': single_model_def['app_name'],
            'model_name': single_model_def['model_name'],
            'model_file_name': single_model_def['model_file_name'],
        }
        template_file_name = 'service_class_template_file.j2'
        if single_model_def['with_user'] is True:
            template_file_name = 'service_class_with_user_template_file.j2'
        self._write_template_file(template_file_name=template_file_name,
                                  context=context,
                                  destination_file_path=single_model_def['service_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'class_name_suffix_part_underscored': '',
            'model_name': single_model_def['model_name'],
            'class_name_suffix_part': 'Service',
        }
        self._check_and_write_export_template_file(template_file_name='export_file_class_name_template.j2',
                                                   context=context,
                                                   destination_file_path=single_model_def['service_init_file_path'])
        print('INFO: checked/updated service class for the model.')

    def _prepare_serializer_class_files_content(self,
                                                single_model_def):
        custom_fields = ''
        fields = []
        cn = 0
        for key, value in single_model_def['def'].items():
            plural_identifier = ''
            if value['__type__'] == 'ManyToManyField':
                key = key + '_uuids'
                plural_identifier = 's'
            elif value['__type__'] == 'ForeignKey':
                key = key + '_uuid'
            if '_uuid' in key:
                context = {
                    'field_name': key,
                    'model_name_spaces': single_model_def['model_name_spaces'],
                    'plural_identifier': plural_identifier,
                }
                custom_fields = custom_fields + self._process_template_file(template_file_name='serializer_payload_custom_field_template.j2',
                                                                            context=context)
            context = {
                'field_name': key,
            }
            file_content = self._process_template_file_only_first_line(template_file_name='serializer_field_template.j2',
                                                                       context=context)
            if cn > 0:
                file_content = '\n' + file_content
            else:
                file_content = file_content.strip()
            fields.append(file_content)
            cn += 1
        fields = ''.join(fields)
        context = {
            'fields': fields,
            'model_name': single_model_def['model_name'],
            'custom_fields': custom_fields,
        }
        self._write_template_file(template_file_name='create_update_serializer_class_template.j2',
                                  context=context,
                                  destination_file_path=single_model_def['create_update_serializer_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'class_name_suffix_part_underscored': '_create_update',
            'model_name': single_model_def['model_name'],
            'class_name_suffix_part': 'CreateUpdateSerializer',
        }
        self._check_and_write_export_template_file(template_file_name='export_file_class_name_template.j2',
                                                   context=context,
                                                   destination_file_path=single_model_def['serializer_init_file_path'])
        fields = []
        field_declaration_list = []
        field_method_declaration_list = []
        custom_fields = ''
        cn = 0
        for key, value in single_model_def['def'].items():
            if value['__type__'] in['ForeignKey', 'ManyToManyField', ]:
                context = {
                    'foreign_key_field': key,
                }
                field_declaration_list.append(self._process_template_file_only_first_line(template_file_name='output_serializer_class_field_template.j2',
                                                                                          context=context))
                is_many = ''
                if value['__type__'] == 'ManyToManyField':
                    is_many = ', many=True'
                context = {
                    'foreign_key_field': key,
                    'foreign_key_model': value['__ref_model__'].split('.')[1],
                    'is_many': is_many
                }
                field_method_declaration_list.append(self._process_template_file(template_file_name='output_serializer_class_field_method_template.j2',
                                                                                 context=context))
            context = {
                'field_name': key,
            }
            file_content = self._process_template_file_only_first_line(template_file_name='serializer_field_template.j2',
                                                                       context=context)
            if cn > 0:
                file_content = '\n' + file_content
            else:
                file_content = file_content.strip()
            fields.append(file_content)
            cn += 1
        fields.append('\n                  \'date_created\',')
        fields = ''.join(fields)
        field_declaration_list = '\n' + '\n'.join(field_declaration_list)
        field_method_declaration_list = '\n'.join(
            field_method_declaration_list)
        context = {
            'fields': fields,
            'field_declaration_list': field_declaration_list,
            'field_method_declaration_list': field_method_declaration_list,
            'model_name': single_model_def['model_name'],
        }
        self._write_template_file(template_file_name='output_serializer_class_template.j2',
                                  context=context,
                                  destination_file_path=single_model_def['output_serializer_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'class_name_suffix_part_underscored': '_output',
            'model_name': single_model_def['model_name'],
            'class_name_suffix_part': 'OutputSerializer',
        }
        self._check_and_write_export_template_file(template_file_name='export_file_class_name_template.j2',
                                                   context=context,
                                                   destination_file_path=single_model_def['serializer_init_file_path'])
        print('INFO: checked/updated serializer classes for the model.')

    def _prepare_view_class_files_content(self,
                                          single_model_def):
        foreign_key_fields = ''
        for model_field, model_def in single_model_def['def'].items():
            template_file_name = ''
            if model_def['__type__'] == 'ForeignKey':
                template_file_name = 'create_update_view_foreign_key_template.j2'
            elif model_def['__type__'] == 'ManyToManyField':
                template_file_name = 'create_update_view_many_to_many_key_template.j2'
            else:
                continue
            model_name = model_def['__ref_model__'].split('.')[1]
            model_file_name = self._convert_from_camel_to_snake(
                source_string=model_name)
            context = {
                'model_file_name': model_file_name,
                'model_name': model_name,
            }
            file_content = self._process_template_file(template_file_name=template_file_name,
                                                       context=context)
            foreign_key_fields += '\n' + file_content[:-1]
        template_file_name = 'create_list_view_class_template.j2'
        if single_model_def['with_user'] is True:
            template_file_name = 'create_list_with_user_view_class_template.j2'
        context = {
            'app_name': single_model_def['app_name'],
            'model_name': single_model_def['model_name'],
            'api_version': single_model_def['api_version'],
            'model_name_spaces_lower_case': single_model_def['model_name_spaces_lower_case'],
            'foreign_key_fields': foreign_key_fields,
            'model_file_name': single_model_def['model_file_name'],
        }
        self._write_template_file(template_file_name=template_file_name,
                                  context=context,
                                  destination_file_path=single_model_def['create_list_views_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'class_name_suffix_part_underscored': '_create_list',
            'model_name': single_model_def['model_name'],
            'class_name_suffix_part': 'CreateListAPIView',
        }
        self._check_and_write_export_template_file(template_file_name='export_file_class_name_template.j2',
                                                   context=context,
                                                   destination_file_path=single_model_def['views_init_file_path'])
        template_file_name = 'fetch_update_delete_view_class_template.j2'
        if single_model_def['with_user'] is True:
            template_file_name = 'fetch_update_delete_with_user_view_class_template.j2'
        context = {
            'app_name': single_model_def['app_name'],
            'model_name': single_model_def['model_name'],
            'api_version': single_model_def['api_version'],
            'model_name_spaces_lower_case': single_model_def['model_name_spaces_lower_case'],
            'foreign_key_fields': foreign_key_fields,
            'model_file_name': single_model_def['model_file_name'],
        }
        self._write_template_file(template_file_name=template_file_name,
                                  context=context,
                                  destination_file_path=single_model_def['fetch_update_delete_views_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'class_name_suffix_part_underscored': '_fetch_update_delete',
            'model_name': single_model_def['model_name'],
            'class_name_suffix_part': 'FetchUpdateDeleteAPIView',
        }
        self._check_and_write_export_template_file(template_file_name='export_file_class_name_template.j2',
                                                   context=context,
                                                   destination_file_path=single_model_def['views_init_file_path'])
        print('INFO: checked/updated view classes for the model.')
        self._update_app_urls_file(single_model_def=single_model_def)

    def _prepare_admin_panel_class_file_content(self,
                                                single_model_def):
        single_model_def['admin_panel_class_body'] = ''
        cn = 0
        list_display = []
        search_fields = []
        for key, value in single_model_def['def'].items():
            if value['__type__'] not in self.CONFIG['EXCLUDED_ADMIN_PANEL_SEARCH_FIELDS']:
                context = {
                    'field_name': key,
                }
                file_content = self._process_template_file_only_first_line(template_file_name='admin_panel_class_field_template.j2',
                                                                           context=context)
                search_fields.append('\n ' + file_content)
                cn += 1
                if cn <= self.CONFIG['ADMIN_PANEL_LIST_DISPLAY_FIELD_LIMIT']:
                    list_display.append('\n' + file_content)
        list_display = ''.join(list_display)
        search_fields = ''.join(search_fields)
        context = {
            'app_name': single_model_def['app_name'],
            'list_display': list_display,
            'search_fields': search_fields,
        }
        self._write_template_file(template_file_name='admin_panel_class_template.j2',
                                  context=context,
                                  destination_file_path=single_model_def['admin_panel_class_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'class_name_suffix_part_underscored': '',
            'model_name': single_model_def['model_name'],
            'class_name_suffix_part': 'Admin',
            'app_name': single_model_def['model_name'],
        }
        self._check_and_write_admin_export_template_file(template_file_name='export_admin_file_class_template.j2',
                                                         context=context,
                                                         destination_file_path=single_model_def['admin_init_file_path'])
        print('INFO: checked/updated admin panel class for the model.')

    def _update_project_settings_file(self,
                                      single_model_def):
        file_content = self._read_file(
            dir_path=single_model_def['project_settings_file_path'])
        if 'PROJECT_APPS = [' not in file_content:
            print(
                'FATAL: Could not add new app name in settings.py file INSTALLED_APPS list.')
        else:
            app_name = '\'' + single_model_def['app_name'] + '\','
            if app_name not in file_content:
                replace_str = '\n    ' + single_model_def['app_name']
                file_content = re.sub(
                    r'(PROJECT_APPS = \[)', r'\1{replace_str}'.format(replace_str=replace_str), file_content)
                self._write_on_file_force(dir_path=single_model_def['project_settings_file_path'],
                                          file_content=file_content)
                print(
                    'INFO: added new django app name in project `settings.py` file INSTALLED_APPS list.')
            else:
                print(
                    'INFO: django app name is already added in project `settings.py` file INSTALLED_APPS list.')

    def _update_new_app_urls_file(self,
                                  single_model_def):
        file_content = self._read_file(
            dir_path=single_model_def['app_urls_file_path'])
        if 'urlpatterns = [' in file_content:
            print('INFO: skipping new app urls.py file creation as that already exists.')
        else:
            context = {}
            self._write_template_file(template_file_name='app_urls_template.j2',
                                      context=context,
                                      destination_file_path=single_model_def['app_urls_file_path'])
            print(
                'INFO: added new app urls.py file content.')

    def _update_project_urls_file(self,
                                  single_model_def):
        urls_file_content = self._read_file(
            dir_path=single_model_def['project_urls_file_path'])
        context = {
            'app_name': single_model_def['app_name'],
        }
        file_content = self._process_template_file(template_file_name='project_url_new_app_entry_template.j2',
                                                   context=context)
        pattern_string = 'url(r\'^api/{app_name}/\','.format(
            app_name=single_model_def['app_name'])
        if pattern_string not in urls_file_content:
            replace_str = file_content + ']'
            urls_file_content = re.sub(
                r'(\])', r'\t{replace_str}'.format(replace_str=replace_str), urls_file_content)
            self._write_on_file_force(dir_path=single_model_def['project_urls_file_path'],
                                      file_content=urls_file_content)
            print('INFO: added new django app url in project `urls.py` file.')
        else:
            print('INFO: django app url is already added in project `urls.py` file.')

    def _update_app_urls_file(self,
                              single_model_def):
        # TODO: generate urls where with_user is set to True
        urls_file_content = self._read_file(
            dir_path=single_model_def['app_urls_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'model_name': single_model_def['model_name'],
            'model_file_name_hyphen': single_model_def['model_file_name'].replace('_', '-'),
        }
        file_content = self._process_template_file(template_file_name='app_urls_new_entry_template.j2',
                                                   context=context)
        pattern_string = 'url(r\'^{model_file_name}/$\','.format(
            model_file_name=single_model_def['model_file_name'].replace('_', '-'))
        if pattern_string not in urls_file_content:
            replace_str = file_content + ']'
            urls_file_content = re.sub(
                r'(\])', r'\t{replace_str}'.format(replace_str=replace_str), urls_file_content)
            self._write_on_file_force(dir_path=single_model_def['app_urls_file_path'],
                                      file_content=urls_file_content)
            print('INFO: added new model CRUD urls in django app `urls.py` file.')
        else:
            print('INFO: model CRUD urls already exists in django app `urls.py` file.')

    def _update_project_messages_file(self,
                                      single_model_def):
        messages_file_content = self._read_file(
            dir_path=single_model_def['project_messages_file_path'])
        context = {
            'model_file_name': single_model_def['model_file_name'],
            'model_name_spaces_lower_case': single_model_def['model_name_spaces_lower_case'],
        }
        file_content = self._process_template_file(template_file_name='service_initial_error_message_template.j2',
                                                   context=context)
        pattern_string = '\'sr_{model_file_name}_1\': '.format(
            model_file_name=single_model_def['model_file_name'])
        if pattern_string not in messages_file_content and single_model_def['with_user'] is False:
            replace_str = '\n' + file_content[:-1]
            messages_file_content = re.sub(
                r'(SERVICE_ERROR_MESSAGE_MAP = {)', r'\1{replace_str}'.format(replace_str=replace_str), messages_file_content)
            self._write_on_file_force(dir_path=single_model_def['project_messages_file_path'],
                                      file_content=messages_file_content)
            print('INFO: added error message from service to `messages.py` file.')
        else:
            print(
                'INFO: error message from service is already added to `messages.py` file.')

    def create_new_app(self,
                       single_model_def):
        dir_path = '{prefix}/{app_name}'.format(prefix=self.PROJECT_PATH,
                                                app_name=single_model_def['app_name'])
        self._perform_module_operations(dir_path=dir_path)
        self._create_apps_file(dir_path=dir_path,
                               single_model_def=single_model_def)
        parent_path = dir_path
        for sub_folder_name in ['admin',
                                'constants',
                                'migrations',
                                'models',
                                'rest_api',
                                'services', ]:
            dir_path = '{prefix}/{sub_folder_name}'.format(prefix=parent_path,
                                                           sub_folder_name=sub_folder_name)
            self._perform_module_operations(dir_path=dir_path)
            if sub_folder_name == 'rest_api':
                for second_sub_folder_name in ['serializers',
                                               'views', ]:
                    child_dir_path = '{prefix}/{sub_folder_name}'.format(prefix=dir_path,
                                                                         sub_folder_name=second_sub_folder_name)
                    self._perform_module_operations(dir_path=child_dir_path)
                self._create_urls_file(dir_path=dir_path)
                self._update_new_app_urls_file(
                    single_model_def=single_model_def)
        self._update_project_settings_file(single_model_def=single_model_def)
        self._update_project_urls_file(single_model_def=single_model_def)
        self._update_project_messages_file(single_model_def=single_model_def)
        print('INFO: checked for app existance and created if did not exist.')

    def add_new_model(self,
                      model_def):
        model_def = self._set_missing_definition_properties(
            model_def=model_def)
        self.create_new_app(single_model_def=model_def)
        self._check_and_create_file(file_path=model_def['model_file_path'])
        self._prepare_model_file_content(single_model_def=model_def)
        self._prepare_service_class_file_content(single_model_def=model_def)
        self._prepare_admin_panel_class_file_content(
            single_model_def=model_def)
        self._prepare_serializer_class_files_content(
            single_model_def=model_def)
        self._prepare_view_class_files_content(single_model_def=model_def)
        print('INFO: operation completed.')


LOCAL_SETTINGS = {}

try:
    from local_settings import LOCAL_SETTINGS
except Exception as ex:
    pass

django_crud_generator = DjangoCrudGenerator(local_settings=LOCAL_SETTINGS)
django_crud_generator.add_new_model(
    model_def=LOCAL_SETTINGS['CUSTOM_MODEL_DEF'])
