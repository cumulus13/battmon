#!/usr/bin/envv python2

# python script showing battery details
import psutil
from xnotify import notify
from make_colors import make_colors
import sys
import traceback
import time
import cmdw
from datetime import datetime

# function returning time in hh:mm:ss
def convertTime(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

def run():
    print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " " + "-"*(cmdw.getWidth() - 30))
    try:
        while 1:
            # returns a tuple
            battery = psutil.sensors_battery()
            
            print(make_colors("Battery percentage", 'y'), ": " + make_colors(str(battery.percent), 'b', 'y'))
            print(make_colors("Power plugged in", 'lc'), "  : " + make_colors(str(battery.power_plugged), 'b', 'lc'))
            
            # converting seconds to hh:mm:ss
            print(make_colors("Battery left", 'lg'), "      : " + make_colors(str(convertTime(battery.secsleft)), 'b', 'lg'))
            if str(battery.percent) == '100':
                notify('Battery Monitor', 'battmon', 'FULL', 'Battery is FULL')
                time.sleep(5)
            elif int(battery.percent) <= 10:
                notify('Battery Monitor', 'battmon', 'LOW', 'Battery is LOW')
                time.sleep(1)
            else:
                time.sleep(60)
            print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " " + "-"*(cmdw.getWidth() - 30))
    except KeyboardInterrupt:
        print(make_colors("Terminated !", 'lw', 'r'))
        sys.exit()
    except:
        print(make_colors('ERROR', 'lw', 'r') + ' ' + traceback.format_exc())
        sys.exit()
        
if __name__ == '__main__':
    run()