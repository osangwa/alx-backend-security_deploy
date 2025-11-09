from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Add IP addresses to the blocklist'
    
    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to block')
        parser.add_argument('--reason', type=str, default='', help='Reason for blocking')
    
    def handle(self, *args, **options):
        ip_address = options['ip_address']
        reason = options['reason']
        
        try:
            blocked_ip, created = BlockedIP.objects.get_or_create(
                ip_address=ip_address,
                defaults={'reason': reason}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully blocked IP: {ip_address}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'IP {ip_address} is already blocked')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error blocking IP {ip_address}: {str(e)}')
            )