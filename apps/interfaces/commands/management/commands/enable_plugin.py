from data.plugins import pool
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Enable a plugin"

    def add_arguments(self, parser):
        parser.add_argument("identifier", type=str)

    def handle(self, *args, **options):
        identifier = options["identifier"]
        plugin = pool.plugin_pool.get_plugin(identifier=identifier)
        if not plugin:
            raise CommandError('Plugin "%s" does not exist' % identifier)

        pool.plugin_pool.enable(plugin_=plugin)
        self.stdout.write(self.style.SUCCESS('Enabled "%s"' % plugin.name))
