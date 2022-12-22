from django.core.management.base import BaseCommand, CommandError

from data.plugins import pool


class Command(BaseCommand):
    help = "Disable a plugin"

    def add_arguments(self, parser):
        parser.add_argument("identifier", type=str)

    def handle(self, *args, **options):
        identifier = options["identifier"]
        plugin = pool.plugin_pool.get_plugin(identifier=identifier)
        if not plugin:
            raise CommandError('Plugin "%s" does not exist' % identifier)

        pool.plugin_pool.disable(plugin_=plugin)
        self.stdout.write(self.style.SUCCESS('Disabled "%s"' % plugin.name))
