from django.core.management.base import BaseCommand, CommandError
from open_elections.content_fetcher import ContentFetcher
from open_elections.content_parser import emit_combined_csv_results

class Command(BaseCommand):
    args = '<region>'
    help = 'Fetches and parses XML data from the specified region; county or state'

    def handle(self, *args, **options):

        content = ContentFetcher()
        try:
            if args[0] == 'state':
                from open_elections.content_parser import parse_state_xml
                state_xml_files = content.fetch_sos()
                parse_state_xml(state_xml_files)
                emit_combined_csv_results()
                
            elif args[0] == 'county':
                from open_elections.content_parser import parse_county_xml
                county_xml_file = content.fetch_xml_content(server="county")
                parse_county_xml(county_xml_file)
                emit_combined_csv_results()
                
            elif args[0] == 'ap':
                from open_elections.content_parser import parse_ap_xml
                ap_xml_file = content.fetch_xml_content(server="ap")
                parse_county_xml(ap_xml_file)
                emit_combined_csv_results()

            self.stdout.write('Successfully ran function "parse_%s_xml()"' % args[0])
        except ImportError:
            raise CommandError('Function "parse_%s_xml()" does not exist' % args[0])









