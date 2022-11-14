#!/usr/bin/envv python2

# python script showing battery details
import psutil
try:
    from xnotify import notify
except:
    pass
from make_colors import make_colors
import sys, os
import traceback
import time
try:
    import cmdw
except:
    pass
from datetime import datetime
import argparse

# function returning time in hh:mm:ss
from configset import configset
config = configset()

def convertTime(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

def get(print_status = True):
     # returns a tuple
    battery = psutil.sensors_battery()
    
    if print_status:
        print(make_colors("Battery percentage", 'y'), ": " + make_colors(str(battery.percent), 'b', 'y'))
        print(make_colors("Power plugged in", 'lc'), "  : " + make_colors(str(battery.power_plugged), 'b', 'lc'))
    return battery

def set_color(status, low = 10, height = 100):
    if int(status) <= 10:
        return make_colors(status, 'lw', 'r')
    elif int(status) > 11 and int(status) < 30:
        return make_colors(status, 'lw', 'm')
    elif int(status) > 30 and int(status) < 60:
        return make_colors(status, 'lw', 'bl')
    elif int(status) > 60 and int(status) < 90:
        return make_colors(status, 'b', 'lg')
    elif int(status) > 90 and int(status) < 100:
        return make_colors(status, 'b', 'lc')
    elif int(status) == 100:
        return make_colors(status, 'b', 'y')

def set_color_plugged(status):
    if status:
        return make_colors("<===", 'lw', 'r')
    return make_colors("===>", 'b', 'lg')

def run():
    nine = 0
    try:
        print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " " + "-"*(cmdw.getWidth() - 30))
    except:
        print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " ------- ")
    try:
        while 1:
            battery = get(False)
            #battery = 100
            # converting seconds to hh:mm:ss
            print(
                make_colors("Battery stat", 'lg'), "      : " + "[{}]".format(set_color(battery.percent)) + " [" \
                + make_colors(str(convertTime(battery.secsleft)), 'lc') + "] [" \
                + set_color_plugged(battery.power_plugged) + "]"
            )
            if int(battery.percent) == 100:
                #try:
                notify.send('Battery is FULL', 'Battery is FULL', 'battmon', 'FULL', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '100.png'))
                #except:
                print(make_colors("BATTERY FULL !", 'lw', 'r'))
                time.sleep((config.get_config('sleep', 'fulltime', '1') or 1))
            elif int(battery.percent) == 99 and battery.power_plugged and not config.get_config('nine', 'done'): 
                #try:
                notify.send('Battery is 99', 'Battery is 99', 'battmon', 'FULL', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '90.png'))
                #except:
                print(make_colors("BATTERY is 99 !", 'lw', 'r'))
                time.sleep((config.get_config('sleep', 'willtime', '5') or 5))
                if not nine == (config.get_config('nine', 'times', '5') or 5):
                    nine += 1
                else:
                    config.write_config('nine', 'done', '1')
            elif int(battery.percent) <= 10 and not battery.power_plugged:
                config.write_config('nine', 'done', '0')
                #try:
                notify.send('Battery is LOW', 'Battery is LOW', 'battmon', 'LOW', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '10.png'))
                #except:
                print(make_colors("BATTERY LOW !", 'lw', 'r'))
                time.sleep((config.get_config('sleep', 'lesstime', '5') or 5))    
            else:
                time.sleep((config.get_config('sleep', 'idletime', '60') or 60))
            
            if int(battery.percent) in [11, 20, 30, 40, 50, 60, 70, 80, 90, 99]:
                if config.get_config('remind', 'ten'):
                    stat = "DC - Unplug"
                    if battery.power_plugged:
                        stat = "AC - Plug"
                    message = "Battery stat" + " : " + "[{}]".format(battery.percent) + "\n" + str(convertTime(battery.secsleft)) + "\n" + stat
                    notify.send('Battery STATUS', message, 'battmon', 'STATUS', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '{}.png'.format(battery.percent)))
            try:
                print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " " + "-"*(cmdw.getWidth() - 30))
            except:
                print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " ------- ")
    except KeyboardInterrupt:
        print(make_colors("Terminated !", 'lw', 'r'))
        sys.exit()
    except:
        print(make_colors('ERROR', 'lw', 'r') + ' ' + traceback.format_exc())
        sys.exit()

def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--monitor', action = 'store_true', help = "Realtime monitor") 

    if len(sys.argv) == 1:
        parser.print_help()
        print("\n")
        get()
    else:
        args = parser.parse_args()
        run()

if __name__ == '__main__':
    usage()