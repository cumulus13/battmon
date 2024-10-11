#!/usr/bin/envv python2

# python script showing battery details
import psutil
import signal
import traceback
import sys, os
sys.excepthook = traceback.format_exception
from xnotify import notify
from make_colors import make_colors
import time
try:
    import cmdw
except:
    pass
from datetime import datetime
import argparse
from pydebugger.debug import debug
import pyttsx3

# function returning time in hh:mm:ss
from configset import configset
config = configset()

def speak(level = None):
    if level:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Kecepatan bicara (kata per menit)
        engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        voices = engine.getProperty('voices')
        
        for voice in voices:
            if 'zira' in voice.name.lower():
                debug(voice_id = voice.id)
                engine.setProperty('voice', voice.id)
                break        
        
        text = f"Battery Level is {level}%"
        engine.say(text)
        engine.runAndWait()

def speakfree(text = None):
    if text:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Kecepatan bicara (kata per menit)
        engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        voices = engine.getProperty('voices')
        
        for voice in voices:
            debug(voice_gender = voice.name.lower())
            if 'zira' in voice.name.lower():
                debug(voice_id = voice.id)
                engine.setProperty('voice', voice.id)
                break        
        
        #text = f"Battery Level is {level}%"
        engine.say(text)
        engine.runAndWait()
    
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
    else:
        return make_colors(status, 'r', 'lw')

def set_color_plugged(status):
    if status:
        return make_colors("<===", 'lw', 'r')
    return make_colors("===>", 'b', 'lg')

def run(test = False):
    debug("run()")
    ntfy_servers = config.get_config('ntfy', 'servers')
    debug(ntfy_servers = ntfy_servers)
    notify.ntfy_server = ntfy_servers
    nine = 0
    try:
        print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "]" + "-"*(cmdw.getWidth() - 40))
    except:
        print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "] ------- ")
    try:
        last_status = None
        while 1:
            battery = get(False)
            debug(battery = battery)
            #battery = 100
            # converting seconds to hh:mm:ss
            if test:
                test = " " + make_colors("[TEST]", 'lw', 'r')
                test1 = " [TEST]"
            else:
                test = ''
                test1 = ''
            #print("battery.percent:", battery.percent)
            print(
                make_colors("Battery stat", 'lg'), "      : " + "[{}]".format(set_color(battery.percent)) + " [" \
                + make_colors(str(convertTime(battery.secsleft)), 'lc') + "] [" \
                + set_color_plugged(battery.power_plugged) + "] [" + make_colors(str(os.getpid()), 'b', 'y') + "] " + test
            )
            if not last_status or last_status != battery.power_plugged:
                last_status = battery.power_plugged
                status_str = 'plugged' if last_status else 'charging'
                notify.send('battmon', 'PLUG', f'Battery is {status_str}', f'Battery is {status_str}' + test1, ['PLUG', 'FULL', 'LOW', 'STATUS'], icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icon.png'), pushbullet = False)
                #except:
                print(make_colors(f"BATTERY is {status_str} !", 'lw', 'r') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "] " + test)
                speak(f"BATTERY is {status_str}!")
                                
            elif int(battery.percent) == 100 and battery.power_plugged:
                #try:
                notify.send('battmon', 'FULL', 'Battery is FULL', 'Battery is FULL' + test1, ['FULL', 'LOW', 'STATUS'], icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '100.png'), pushbullet = False)
                #except:
                print(make_colors("BATTERY FULL !", 'lw', 'r') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "] " + test)
                speak(100)
                
                for i in [10, 11, 20, 30, 40, 50, 60, 70, 80, 90, 98]:
                    config.write_config('step', str(i), '0')
                time.sleep((config.get_config('sleep', 'fulltime', '2') or 2))
            
            elif (int(battery.percent) == 99 or int(battery.percent) > 99) and battery.power_plugged and not config.get_config('nine', 'done'): 
                #try:
                #notify.send('Battery is 99', 'Battery is 99' + test1, 'battmon', 'FULL', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '90.png'), pushbullet = False)
                notify.send('battmon', 'FULL', 'Battery is 99', 'Battery is 99' + test1, ['FULL', 'LOW', 'STATUS'], icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '90.png'), pushbullet = False)
                #except:
                print(make_colors("BATTERY is 99 !", 'lw', 'r') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "] " + test)
                speak(battery.percent)
                time.sleep((config.get_config('sleep', 'willtime', '5') or 5))
                if not nine == (config.get_config('nine', 'times', '5') or 5):
                    nine += 1
                else:
                    config.write_config('nine', 'done', '1')
            elif int(battery.percent) <= 32 and not battery.power_plugged:
                config.write_config('nine', 'done', '0')
                #try:
                nl = 0
                if not nl > config.get_config('len10', 'times', 10):
                    #notify.send('Battery is LOW', 'Battery is LOW' + test1, 'battmon', 'LOW', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '10.png'), pushbullet = False)
                    notify.send('battmon', 'LOW', 'Battery is LOW', 'Battery is LOW' + test1, ['FULL', 'LOW', 'STATUS'], icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '10.png'), pushbullet = False)
                else:
                    nl += 1
                #except:
                print(make_colors("BATTERY LOW !", 'lw', 'r') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "] " + test)
                speak(battery.percent)
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
                                speakfree(f"Battery status is {stat} on level {percent}%")
                                #notify.send('Battery STATUS', message, 'battmon', 'STATUS', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '{}.png'.format(percent)), pushbullet = False)
                                notify.send('battmon', 'STATUS', 'Battery STATUS', message + test1, ['FULL', 'LOW', 'STATUS'], icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '{}.png'.format(percent)), pushbullet = False)
                            else:
                                config.write_config('step', str(percent), '0')
                                
            try:
                print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " " + "[" + make_colors(str(os.getpid()), 'b', 'y') + "] " + "-"*(cmdw.getWidth() - 40))
            except:
                print(make_colors(datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S:%f'), 'lb') + " [" + make_colors(str(os.getpid()), 'b', 'y') + "] " + " ------- ")
    except KeyboardInterrupt:
        print(make_colors("Terminated !" + test1, 'lw', 'r'))
        speakfree("Battmon Terminated !")
        os.kill(os.getpid(), signal.SIGTERM)
    except:
        print(make_colors('ERROR' + test1, 'lw', 'r') + ' ' + traceback.format_exc())
        speakfree("Battmon ERROR !")
        sys.exit()
        
def test():
    #notify.send('Battery is FULL', 'Battery is FULL', 'battmon', 'FULL', icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '100.png'), pushbullet = False)
    notify.send('battmon', 'FULL', 'Battery is FULL', 'Battery is FULL', ['FULL', 'LOW', 'STATUS'], icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), '100.png'), pushbullet = False)
        
def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--monitor', action = 'store_true', help = "Realtime monitor")
    parser.add_argument('-t', '--test', action = 'store_true', help = 'Test Notification')

    if len(sys.argv) == 1:
        parser.print_help()
        print("\n")
        get()
    else:
        args = parser.parse_args()
        debug(args = args)
        if args.monitor:
            debug(args = "monitor")
            run()
        elif args.test:
            os.environ.update({'DEBUG': '1',})
            test()
            os.environ.update({'DEBUG': '',})
        else:
            run()

if __name__ == '__main__':
    usage()
    #test()