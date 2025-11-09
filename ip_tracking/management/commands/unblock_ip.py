from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Remove IP addresses from the blocklist'
    
    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to unblock')
    
    def handle(self, *args, **options):
        ip_address = options['ip_address']
        
        try:
            deleted_count = BlockedIP.objects.filter(ip_address=ip_address).delete()[0]
            
            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully unblocked IP: {ip_address}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'IP {ip_address} was not found in blocklist')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error unblocking IP {ip_address}: {str(e)}')
            )