#!/usr/bin/envv python2

# python script showing battery details
import psutil
import traceback
import sys, os
sys.excepthook = traceback.format_exception
#try:
from xnotify import notify
#except:
    #print(traceback.format_exc())
    #pass
from make_colors import make_colors
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

def run(test = False):
    ntfy_servers = config.get_config('ntfy', 'servers')
    notify.ntfy_server = ntfy_servers
    nine = 0
    try:
        print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "]" + "-"*(cmdw.getWidth() - 38))
    except:
        print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "] ------- ")
    try:
        while 1:
            battery = get(False)
            #battery = 100
            # converting seconds to hh:mm:ss
            if test:
                test = " " + make_colors("[TEST]", 'lw', 'r')
                test1 = " [TEST]"
            else:
                test = ''
                test1 = ''
            print(
                make_colors("Battery stat", 'lg'), "      : " + "[{}]".format(set_color(battery.percent)) + " [" \
                + make_colors(str(convertTime(battery.secsleft)), 'lc') + "] [" \
                + set_color_plugged(battery.power_plugged) + "]" + test
            )
            if int(battery.percent) == 100 and  battery.power_plugged:
                #try:
                notify.send('Battery is FULL', 'Battery is FULL' + test1, 'battmon', 'FULL', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '100.png'))
                #except:
                print(make_colors("BATTERY FULL !", 'lw', 'r') + test)
                for i in [10, 11, 20, 30, 40, 50, 60, 70, 80, 90, 98]:
                    config.write_config('step', str(i), '0')
                time.sleep((config.get_config('sleep', 'fulltime', '2') or 2))
            elif int(battery.percent) == 99 and battery.power_plugged and not config.get_config('nine', 'done'): 
                #try:
                notify.send('Battery is 99', 'Battery is 99' + test1, 'battmon', 'FULL', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '90.png'))
                #except:
                print(make_colors("BATTERY is 99 !", 'lw', 'r') + test)
                time.sleep((config.get_config('sleep', 'willtime', '5') or 5))
                if not nine == (config.get_config('nine', 'times', '5') or 5):
                    nine += 1
                else:
                    config.write_config('nine', 'done', '1')
            elif int(battery.percent) <= 10 and not battery.power_plugged:
                config.write_config('nine', 'done', '0')
                #try:
                notify.send('Battery is LOW', 'Battery is LOW' + test1, 'battmon', 'LOW', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '10.png'))
                #except:
                print(make_colors("BATTERY LOW !", 'lw', 'r') + test)
                for i in [10, 11, 20, 30, 40, 50, 60, 70, 80, 90, 98]:
                    config.write_config('step', str(i), '1')                
                time.sleep((config.get_config('sleep', 'lesstime', '1') or 1))    
            else:
                time.sleep((config.get_config('sleep', 'idletime', '60') or 60))
            
            if int(battery.percent) in [11, 20, 30, 40, 50, 60, 70, 80, 90, 98]:
                percent = battery.percent
                if config.get_config('remind', 'ten'):
                    #nx = 0
                    if config.get_config('step', str(percent)):
                        for x in range(0, config.get_config('remind', 'times', '2') + 1):
                            if not x == config.get_config('remind', 'times', '2'):
                                #nx += 1
                                stat = "DC - Unplug"
                                if battery.power_plugged: stat = "AC - Plug"
                                message = "Battery stat" + " : " + "[{}]".format(percent) + "\n" + str(convertTime(battery.secsleft)) + "\n" + stat + test1
                                notify.send('Battery STATUS', message, 'battmon', 'STATUS', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '{}.png'.format(percent)))
                            else:
                                config.write_config('step', str(percent), '0')
                                
            try:
                print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " " + "-"*(cmdw.getWidth() - 30))
            except:
                print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " ------- ")
    except KeyboardInterrupt:
        print(make_colors("Terminated !" + test1, 'lw', 'r'))
        sys.exit()
    except:
        print(make_colors('ERROR' + test1, 'lw', 'r') + ' ' + traceback.format_exc())
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