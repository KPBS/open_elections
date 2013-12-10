from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = '<provider>'
    help = 'Generates CSV data from the specified provider(s); county, state, ap or combined'

    def handle(self, *args, **options):
        try:
            if args[0] == 'ap':
                pass
            elif args[0] == 'county':
                pass
            elif args[0] == 'state':
                pass
            elif args[0] == 'combined':
                from open_elections.content_parser import emit_combined_csv_results
                emit_combined_csv_results()
            self.stdout.write('Successfully ran function "emit_%s_csv_results()"' % args[0])
        except ImportError:
            raise CommandError('Function "emit_%s_csv_results()" does not exist' % args[0])
