#!/usr/bin/python2.7
#perilloro - slightly modified version of pomodoro method

import sys
import time
from os import linesep
import subprocess as sp

HELP_MSG = linesep.join(("perilloro - slightly modified version of pomodoro method",
                        "concepts:",
                        "\tpomodoro: time applied to activity",
                        "\tbreak: time applied between pomodores",
                        "\tsession: set of pomodores",
                        "\trest: time applied between sessions" + linesep,
                        "avaliable options (all time values are in minutes):"))

PROG_KEY = "[perilloro] "

def min_to_sec(minutes):
    return minutes * 60.0

def sec_to_min(seconds):
    return seconds / 60.0

def format_time(seconds):
    hours = int(seconds) / 3600
    minutes = (int(seconds)%3600) / 60
    seconds = seconds % 60 
    return hours, minutes, seconds

def notify(path_to_notifier, message):
    if not path_to_notifier:
        return

    try:
        proc = sp.Popen(path_to_notifier.split() + [message], stdout=sp.PIPE, stderr=sp.PIPE)
        return proc.communicate()
    except:
        message("warning: could not use system notifier")
        return None

#input: initial time, increment in seconds
def time_gen(initial_period, incr=0.0):
    i=0
    while True:
        yield initial_period + i*incr
        i += 1

#returns total times in minutes
def total_times(pomodoro_gen, break_gen, rest_gen, iterations, sessions):
    pomodoro_total_time = sessions * sum(pomodoro_gen.next() for i in xrange(iterations))
    break_total_time = sessions * sum(break_gen.next() for i in xrange(iterations-1))
    rest_total_time = sum(rest_gen.next() for i in xrange(sessions-1))

    return pomodoro_total_time, break_total_time, rest_total_time

def message(msg, endl=True):
    sys.stdout.write(PROG_KEY + msg + (linesep if endl else ""))

def tic_toc(sleep_time, msg=""):
    for i in xrange(int(sleep_time)):
        sys.stdout.write(msg + "remaining time: %dh%dm%ds" % format_time(sleep_time-i))
        sys.stdout.flush()
        time.sleep(1.0)

def main():
    import oarg_exp as oarg

    #command line args
    pomodoro_start_time = oarg.Oarg("-p --pomodoro", 25.0, "initial pomodoro time")
    pomodoro_increment = oarg.Oarg("--pi", 0.0, "increment of pomodoros times for each session") 
    break_start_time = oarg.Oarg("-b --break", 5.0, "initial break time among sessions")
    break_increment = oarg.Oarg("--bi", 5.0, "increment of breaks times") 
    rest_start_time = oarg.Oarg("-r --rest", 20.0, "initial rest time")
    rest_increment = oarg.Oarg("--ri", 0.0, "increment of rests times for each session") 
    iterations = oarg.Oarg("-i --iterations", 2, "number of pomodoros for each session")
    sessions = oarg.Oarg("-s --sessions", 1, "number of sessions")  
    notifier = oarg.Oarg("-n --notifier", "", "path to system notifier to send messages" + 
                                              "about sessions")
    hlp = oarg.Oarg("-h --help", False, "this help message")  
    
    #parsing command line args
    oarg.parse()

    #help messages
    if hlp.val:
        oarg.describeArgs(HELP_MSG, def_val=True)
        exit()

    #times generators
    pomodoro_gen = time_gen(min_to_sec(pomodoro_start_time.val), 
                            min_to_sec(pomodoro_increment.val))
    break_gen = time_gen(min_to_sec(break_start_time.val), 
                         min_to_sec(break_increment.val))
    rest_gen = time_gen(min_to_sec(rest_start_time.val), 
                        min_to_sec(rest_increment.val))

    #times 
    pomodoros_time, breaks_time, rests_time = total_times(pomodoro_gen, break_gen, rest_gen,
                                                          iterations.val, sessions.val)

    message("will run %d sessions of %d iterations each" % (sessions.val, iterations.val))
    print
    for k, t in zip(("pomodoros", "break", "rest"), 
                         (pomodoros_time, breaks_time, rests_time)):
        message(k + " total time: %dh%dm%ds" % format_time(t))
    message("total time: %dh%dm%ds" % format_time(pomodoros_time + breaks_time + rests_time))
    print

    session_efic = pomodoros_time / (pomodoros_time + breaks_time)
    total_efic = pomodoros_time / (pomodoros_time + rests_time + breaks_time)

    message("efficiency per session: %.2f" % session_efic)
    message("total efficiency: %.2f" % total_efic)
    print

    message("starting sessions in ", endl=False)
    for n in xrange(3):
        sys.stdout.write(str(3 - n) + ", ") 
        sys.stdout.flush()
        time.sleep(1.0)
    print "go!" + linesep

    for i in xrange(sessions.val):
        pg = pomodoro_gen
        bg = break_gen

        message("on session #%d" % (i+1))
        for it in xrange(iterations.val):
            pomodoro = pg.next()
            notify(notifier.val, "pomodoro started - duration: %dh%dm%ds" % \
                                 format_time(pomodoro))
            tic_toc(pomodoro, msg="\r" + len(PROG_KEY)*" " + 
                                  "pomodoro #%d out of %d - " % (it+1, iterations.val))
            print

            break_time = bg.next()
            notify(notifier.val, "break time - duration: %dh%dm%ds" % \
                                 format_time(break_time))
            tic_toc(break_time, msg="\r" + len(PROG_KEY)*" " + "break time! - ")
            print 

        rest_time = rest_gen.next()
        print
        message("time to rest for next session")
        notify(notifier.val, "rest time - duration: %dh%dm%ds" % \
                             format_time(rest_time))
        tic_toc(rest_time, msg="\r" + len(PROG_KEY)*" ")
        print linesep 
    
    message("fini")
        
if __name__ == "__main__":
    main()
