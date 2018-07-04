from amixerPy import getAmixerContents
from amixerPy import amixerCset
from amixerPy import amixerCget
import math

contents = getAmixerContents(0)




print "\n\nPlayback contents:"
for content in contents:
	if "layback" in content['name']:
		print str(content)

print "\n\nCapture contents:"
for content in contents:
	if "apture" in content['name']:
		print str(content)

print "\n\nOther contents:"
for content in contents:
	if "layback" not in content['name'] and "apture" not in content['name']:
		print str(content)

