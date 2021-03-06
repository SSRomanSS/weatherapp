"""
App commands
"""
from weatherapp.core.abstract import Command


class Providers(Command):
    """
    List of providers
    """
    name = 'providers'

    def run(self):
        """
        Run command
        """
        providers = self.app.provider_manager
        for name in providers:
            print('{} - "{}"'.format(name, providers.get(name).title))
