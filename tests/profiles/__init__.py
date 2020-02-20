from django.apps import AppConfig


class TestProfileAppConfig(AppConfig):
    name = 'tests.profiles'
    label = 'tests_profiles'
    verbose_name = 'Test Profiles'


default_app_config = 'tests.profiles.TestProfileAppConfig'
