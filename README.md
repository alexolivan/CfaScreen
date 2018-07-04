CristalFontz python micro-framework.

![screenshot1](/screenshots/cfa635-1.jpg "screenshot1") ![screenshot2](/screenshots/cfa635-2.jpg "screenshot2")
![screenshot3](/screenshots/cfa635-3.jpg "screenshot3") ![screenshot5](/screenshots/cfa635-5.jpg "screenshot5")
![screenshot6](/screenshots/cfa635-6.jpg "screenshot6") ![screenshot7](/screenshots/cfa635-7.jpg "screenshot7")


A tiny python kind of framework, resulting of my work on trying to control
ALSA Sound Card audio setup using the CFA635 LCD... as a kind of LCD-keypress
based ALSAmixer.

To ease auto-generation of screens upon parsing ALSA mixer controls, I created
a wrapper class, CfaScreen.py, provideing necessary methods, being the core
library comunicating with the CFA635 LCD 'lcdproc'
https://github.com/jinglemansweep/lcdproc.

The concept I used is somehow similar to those Game Frameworks such as LibGDX,
where an endless loop calls methods you're supposed to implement around.
The script cfa_main.py runs makes the early instantiation of a 'root' screen
, being the rest of screens child nodes in an inverted tree scheme.
in endless loop, then it enters an endless loop, handling events, and the screen
 workflow.

The CfaScreen class provides:
- licecycle and event methods/functions to be overwritten as needed on every
instance (I know ... ugly...) to implement desired functionality.
- methods to put CfaScreen instances as a next, right screen, or
bellow/down screen.
- methods to ease writing stuff, including bars, controls, etc.
- it handles auto-generation of navigation arrows as needed to navigate
to neighboring screens.

Current code status:
- It allows to control my ALSA, Intel HDA card (but test on other PCs worked).
(Work on AudioScience 5620/5720 5640/5740 is on the way)
- See some System Info/Status such as CPU, Mem, DiskUsage or Temp.
(work on networking status and control of DHCP client, VPN client)

About needs, dependencies, environment:
- The main cfa_main.py binds as client to lcdproc LCDd.
- I'm using exclusively CFA-635 LCDs and runing with Debian packaged lcdproc
binaries.
- Connection with CFA635 was via USB.
- To control the side leds, I'm using CFLIB, a C library/binary tools...
specifically the 'cfont' bin.
CFLIB can be public downloaded as its author, 'ScottishCaptain', posted the
code at https://forum.crystalfontz.com ... I removed my built bin from repo
just in case.

NOTE:
- Overall the code would need a proper refactor by a skilled python developer...
I'm not a pro developer, but just systems/networking administrator.
- There surely is a way to have kind of 'java interfaces' without needing to
overwritte methods in a per-instance base... I feel it not elegant.
- Handling of async events is horrible ... it is out of my python skills ...
and using sleeps is very ugly.
- I would like to have something like a real 'time delta' (like on LibGLX) to
control looping, again, ugly sleeps are used.
- I was unable to get 'lcdproc' working on python 3 ... so just python 2.7
