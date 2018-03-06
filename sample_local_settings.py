LOCAL_SETTINGS = {
    'SYSTEM_USER_NAME': 'ubuntu',
    'REPO_ROOT_PATH': '/home/ubuntu/Desktop',
    'PROJECT_FOLDER_NAME': 'test',
    'CUSTOM_MODEL_DEF': {
        'api_version': '1.0.1',
        'app_name': 'chats',
        'model_name': 'UserMessage',
        'str_property_name': 'channel_name',
        'with_user': False,
        'def': {
            'channel_name': {
                '__type__': 'str',
                '__null__': True,
                '__help_text__': 'Chat message channel name',
                '__extra__': ['min_length=4'],
                'max_length': '256',
            },
            'message': {
                '__type__': 'txt',
                '__help_text__': 'Chat message text',
                'default': '\'\'',
            },
            'user': {
                '__type__': 'ref',
                '__help_text__': 'Chat message text owner user',
                '__ref_model__': 'users.User',
            },
            'email': {
                '__type__': 'CustomEmailField',
                '__help_text__': 'Email address of the user',
            },
            'message_type': {
                '__type__': 'choice',
                '__choices__': 'Private,Protected,Open for everyone',
                '__help_text__': 'Type of the message sent',
            },
        }
    },
}
