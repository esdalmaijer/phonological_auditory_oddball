import copy
import random

import numpy

from constants import *
from pygaze.display import Display
from pygaze.screen import Screen
from pygaze.sound import Sound
from pygaze.mouse import Mouse
from pygaze.keyboard import Keyboard
from pygaze.logfile import Logfile
import pygaze.libtime as timer

# Load the real MEGTriggerBox, or define a dummy class.
if not MEGDUMMY:
    from scansync.meg import MEGTriggerBox
else:
    class MEGTriggerBox:
        def __init__(self):
            self._logpath = LOGFILE + "_MEGDUMMY"
            self._log = Logfile(filename=self._logpath)
            self._log.write(["time", "value"])
        def set_trigger_state(self, value, return_to_zero_ms=10):
            self._log.write([timer.get_time(), value])
            timer.pause(return_to_zero_ms)
            self._log.write([timer.get_time(), 0])


# # # # #
# INITIALISE

# Initialise a Display to present messages for the researcher on.
disp = Display()

# Make sure that the mouse can be seen when hovering over.
mouse = Mouse()
mouse.set_visible(True)

# Create a Screen for ad-hoc presentation. (We don't need pre-created screens,
# as we are unconcerned with visual timing in this particular experiment.)
scr = Screen()
scr.draw_text(text="Loading, please wait...", fontsize=32)
disp.fill(scr)
disp.show()

# Create a keyboard instance to allow the researcher to provide input.
keyboard = Keyboard(keylist=None, timeout=None)

# Create all sound stimuli.
sound = {}
for soundname in SOUNDS:
    sound[soundname] = Sound(soundfile=SOUNDFILES[soundname])

# Create a new logfile.
log = Logfile()
# Write a header to the logfile.
log.write(["soundnr", "onset", "type", "name", "trigger"])

# Create a MEGTriggerBox instance to send triggers to the MEG.
meg = MEGTriggerBox()

# Pre-create a pause screen.
pause = Screen()
pause.draw_text(text="Experiment PAUSED\n\n- Space to continue\n- Esc to kill prematurely.", \
    fontsize=32)


# # # # #
# RANDOMISATION

# Set the random seed.
if RANDOMSEED is not None:
    random.seed(RANDOMSEED)
    numpy.random.seed(RANDOMSEED)

# Construct a sequence of all trials.
deviant_order = []
for deviant_type in DEVIANT_TRIALS.keys():
    deviant_order.extend(DEVIANT_TRIALS[deviant_type] * [deviant_type])
# Randomise the order.
random.shuffle(deviant_order)

# Create a list of all trials.
trials = []
# Add the habituation trials.
for i in range(HABITUATION_TRIALS):
    trials.append({ \
        "stimtype": "S", \
        "stimname": SOUNDTYPES["S"],
        })
# Add the oddball trials, separated by a predefined number of standard trials.
for i, deviant_type in enumerate(deviant_order):
    # Add the debiant.
    trials.append({ \
        "stimtype": deviant_type, \
        "stimname": SOUNDTYPES[deviant_type],
        })
    # Add the in-between trials.
    for j in range(numpy.random.choice(STANDARD_PADDING, p=PADDING_PROB)):
        trials.append({ \
            "stimtype": "S", \
            "stimname": SOUNDTYPES["S"],
            })


# # # # #
# WAIT TO START

# Show the waiting message on the display.
scr.clear()
scr.draw_text(text="Press a key to start the %.2f second countdown!" % (DELAY), \
    fontsize=32)
disp.fill(scr)
disp.show()

# Wait for a keypress.
key, t0 = keyboard.get_key(keylist=None, timeout=None, flush=True)
t1 = copy.deepcopy(t0)

# Present a visual countdown.
delay_ms = DELAY * 1000.0
while t1 - t0 < delay_ms:
    scr.clear()
    scr.draw_text(text="T - %.2f seconds" % ((delay_ms - (t1-t0))/1000.0), \
        fontsize=32)
    disp.fill(scr)
    t1 = disp.show()


# # # # #
# RUN EXPERIMENT

# Present running message.        
scr.clear()
scr.draw_text(text="Running experiment...\n\n- Space to pause\n- Esc to kill prematurely.", \
    fontsize=32)
disp.fill(scr)
disp.show()

# Loop through all trials.
for i, trial in enumerate(trials):
    # Play the sound.
    sound[trial["stimname"]].play()
    # Get a timestamp. Note that this is not automatically synced to the sound
    # onset, which is determined by latencies in the system (specifically
    # those caused by the sound card). This needs to be calibrated on each
    # system this experiment runs on!
    t = timer.get_time()
    # Send a trigger to the MEG.
    meg.set_trigger_state(TRIGGERCODES[trial["stimtype"]], \
        return_to_zero_ms=10)
    # Log this trial.
    log.write([i, t, trial["stimtype"], trial["stimname"], \
        TRIGGERCODES[trial["stimtype"]]])
    # Wait for the ISI by using it as a timeout to the keyboard, so that the
    # experimenter can kill the experiment at will.
    isi = random.randint(ISI[0], ISI[1]) - (timer.get_time()-t)
    key, presstime = keyboard.get_key(keylist=["escape", "space"], \
        timeout=isi)
    # If the experimenter pressed the Escape or Q keys, kill the experiment.
    if key is not None:
        # Check if the experimenter pressed Space to pause the experiment.
        if key == "space":
            # Start the break.
            disp.fill(pause)
            disp.show()
            meg.set_trigger_state(TRIGGERCODES["pause"], \
                return_to_zero_ms=10)
            # Wait for a Space press.
            key, presstime = keyboard.get_key(keylist=["escape", "space"], \
                timeout=None, flush=True)
            # Re-present the experiment screen.
            disp.fill(scr)
            disp.show()
            meg.set_trigger_state(TRIGGERCODES["unpause"], \
                return_to_zero_ms=10)
        # Check if the experimenter pressed Escape during the trial or during
        # the pause.
        if key in ["escape", "q"]:
            # Break off the trial loop.
            meg.set_trigger_state(TRIGGERCODES["kill"], \
                return_to_zero_ms=10)
            log.write(["NaN", presstime, "EXPKILL", "EXPKILL", \
                TRIGGERCODES["kill"]])
            break


# # # # #
# CLOSE

# Close the log file.
log.close()

# Show an ending message on the display.
scr.clear()
scr.draw_text(text="The experiment has ended! Press any key to close.", \
    fontsize=32)
disp.fill(scr)
disp.show()
# Wait for a keypress.
key, presstime = keyboard.get_key(keylist=None, timeout=None, flush=True)

# Close the display.
disp.close()
