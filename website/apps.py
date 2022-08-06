from django.apps import AppConfig
from threading import Timer
import time
from time import sleep
# import django
# django.setup()
import django
from bson import ObjectId

# some variable declarations
# world_mapping = {
#     'osm_id': 'osm_id',
# }


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def timeout(self):
        from .models import room as model_room
        rooms = model_room.objects(status='opening')
        for r in rooms:
            print('---------------------------')
            now = round(time.time() * 1000)
            print(now)
            millisec = r.end.timestamp() * 1000
            print(millisec)

            if int(millisec) <= now:
                model_room.objects(id=ObjectId(r.id)).update(status='closed')
                print('phong '+ str(r.id) + ' da dong!')
            else:
                print("thoi gian dang chay...")

    def ready(self):
        self.timer_thread = Timer(0.2, self.timeout)
        self.timer_thread.start()
        sleep(0.2)








    # def ready(self):
    #     # start daemon thread that polls device's health
    #     thread = Thread(name='device_health_checker', target=self.device_health_check)
    #     thread.daemon = True
    #     thread.start()