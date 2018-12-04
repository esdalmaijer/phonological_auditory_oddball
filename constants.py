# This is the constants file for a phonological auditory oddball task that
# is part of the Resilience in Education and Development (RED) study. The
# task was designed to be run in the background, so that a video could be
# displayed in the foreground.

import os


# GENERAL SETTINGS
# Delay after the researcher indicates the experiment can start, in seconds.
DELAY = 20.0
# You can define a particular random seed to equalise the order between
# participants, or set the seed to None to not do so.
RANDOMSEED = 19

# SOUND SETTINGS
# Define the names of the sounds that should be presented in the experiment.
SOUNDS = ["boak", "boap", "boat"]
# Define the type of stimulus that each sound is.
# The S (standard) sound is a non-word reference word (e.g. "boak").
# The Dw is a known word deviant (e.g. "boat")
# The Dp is a pseudo-word deviant (e.g. "boap")
SOUNDTYPES = { \
    "S":    SOUNDS[0], \
    "Dw":   SOUNDS[2], \
    "Dp":   SOUNDS[1], \
    }
# Define how many standard sounds will occur between each deviant. This should
# be a list of integers that define all potential number of occurences. They
# will be (uniformly) randomly sampled from.
STANDARD_PADDING = [2, 3, 4, 5]
# Define the number of habituation sounds that will be played at the start of
# the experiment. These will all be the standard sound.
HABITUATION_TRIALS = 10
# Define how often each deviant will be presented.
DEVIANT_TRIALS = { \
    "Dw":   150, \
    "Dp":   150, \
    }
# Define the inter-sound interval, as a (minimal, maximal) ISI pair. ISIs will
# be sampled from a uniform distribution between the minimum and the maximum.
# Note that the ISI is the difference between the onsets of sounds.
# EDWIN NOTE: The original task had offset-onset intervals of 800 ms. Taking
# into account the length of each sound (400 ms), the ISI should be 1200 ms.
ISI = (1200, 1200)

# MEG SETTINGS
MEGDUMMY = False
TRIGGERCODES = { \
    "S":    101, \
    "Dw":   102, \
    "Dp":   103, \
    "kill":  19, \
    }

# DISPLAY SETTINGS
# Display back-end, either "pygame" or "psychopy".
DISPTYPE = "psychopy"
# Display resolution in pixels.
DISPSIZE = (600,300)
# Fullscreen should be turned off, as we'll be running other things in the
# background. (Or via a DVD player, but fullscreen presentation is unnecessary
# either way.)
FULLSCREEN = False

# FILES AND FOLDERS
# Auto-detect the directory that this file is in.
DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the data directory.
DATADIR = os.path.join(DIR, "data")
# Construct the resource directory.
RESDIR = os.path.join(DIR, "resources")
# Check if the resource directory exists.
if not os.path.isdir(RESDIR):
    raise Exception("ERROR: Could not find resources directory at '%s'"  % \
        (RESDIR))
# Construct the paths to sound files.
SOUNDFILES = {}
for soundname in SOUNDS:
    SOUNDFILES[soundname] = os.path.join(RESDIR, soundname + ".wav")
    # Check if the sound file exists in its expected location.
    if not os.path.isfile(SOUNDFILES[soundname]):
        raise Exception("ERROR: Could not find sound file '%s' at '%s'" % \
            (soundname, SOUNDFILES[soundname]))
# Create a new data directory if one doesn't exist yet.
if not os.path.isdir(DATADIR):
    os.mkdir(DATADIR)
# Ask for a new name for the log file.
LOGFILENAME = raw_input("Please enter a file name: ")
# Construct the path to the log file (a file extension will be added
# automatically).
LOGFILE = os.path.join(DATADIR, LOGFILENAME)
