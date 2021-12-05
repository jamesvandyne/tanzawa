from django.core.management.commands import migrate
from django.db import migrations


class Command(migrate.Command):
    def handle(self, *args, **kwargs):
        # Set the flag.
        migrations.MIGRATION_OPERATION_IN_PROGRESS = True

        # Execute the normal behaviour.
        super(Command, self).handle(*args, **kwargs)
        migrations.MIGRATION_OPERATION_IN_PROGRESS = False
