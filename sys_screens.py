#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Imports
from lcdproc.server import Server
import CfaScreen
import os, psutil, time
import signal

rootScreen = None

# Single/Root screen is returned with all its eventual
# subtree of screens to the main cfa_screen logic
def get():
	rootScreen = CfaScreen.CfaScreen("System")
	rootScreen.ledLabels = ['CPU', 'Mem', 'FS', 'Uptime']
	rootScreen.tDelta = 500

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		rootScreen.widgets['cpu_value_widget'] = screen.add_string_widget("cpu_value_widget", "0.0%", 6, 1)
		rootScreen.update_LED_meter(0, 0)
		rootScreen.widgets['mem_value_widget'] = screen.add_string_widget("mem_value_widget", "0.0%", 6, 2)
		rootScreen.update_LED_meter(1, 0)
		rootScreen.widgets['fs_value_widget'] = screen.add_string_widget("fs_value_widget", "OK", 6, 3)
		rootScreen.update_LED_meter(2, 0)
		rootScreen.widgets['upt_value_widget'] = screen.add_string_widget("upt_value_widget", "0d", 6, 4)
		rootScreen.update_LED_meter(3, 0)
	rootScreen.init = init

	# MAIN LOGIC -> Value updates
	def updateWidgets(screen):
		percent = psutil.cpu_percent()
		rootScreen.update_widget_text(rootScreen.widgets['cpu_value_widget'], str(percent) + "%")
		rootScreen.update_LED_meter(0, percent)

		vmem = psutil.virtual_memory()[2]
		rootScreen.update_widget_text(rootScreen.widgets['mem_value_widget'], str(vmem) + "%")
		rootScreen.update_LED_meter(1, vmem)

		fsstat = os.statvfs('/')
		if bool(fsstat.f_flag & os.ST_RDONLY):
			rootScreen.update_widget_text(rootScreen.widgets['fs_value_widget'], "OK")
			rootScreen.update_LED_meter(2, 20)
		else:
			rootScreen.update_widget_text(rootScreen.widgets['fs_value_widget'], "WARN")
			rootScreen.update_LED_meter(2, 100)

		uptime = (int(time.time()) - int(psutil.boot_time())) / 86400
		rootScreen.update_widget_text(rootScreen.widgets['upt_value_widget'], str(uptime) + "d")
		if uptime >= 360:
			rootScreen.update_LED_meter(3, 100)
		elif 360 > uptime >= 180:
			rootScreen.update_LED_meter(3, 70)
		else:
			rootScreen.update_LED_meter(3, 20)

	rootScreen.updateWidgets = updateWidgets

	# Attach subscreens as needed before return
	rootScreen.pushNextScreen(defineSysMenuScreen())

	# finally, return the screen
	return rootScreen



# Subscreens definitions

# First Level Screen (shows menu to next level screens)
def defineSysMenuScreen():
	newScreen = CfaScreen.CfaScreen("SysSubmenu")
	newScreen.pushNextScreen(defineMainSysInfoScreen())
	newScreen.pushDownScreen(defineCPUMenuScreen())
	newScreen.pushDownScreen(defineMemMenuScreen())
	newScreen.pushDownScreen(defineDiskMenuScreen())
	newScreen.pushDownScreen(defineTempMenuScreen())
	return newScreen


# Second Level Screens (entry point for chained screens)
def defineCPUMenuScreen():
	newScreen = CfaScreen.CfaScreen("SysSubmenu")
	cpucount = psutil.cpu_count()
	newScreen.pushNextScreen(defineMainCpuScreen())
	for i in range (0, cpucount):
		newScreen.pushNextScreen(definePerCpuInfoScreen(i))
	return newScreen

def defineMemMenuScreen():
	newScreen = CfaScreen.CfaScreen("MemSubmenu")
	vmeminfo = psutil.virtual_memory()
	newScreen.pushNextScreen(defineMainMemScreen())
	for field in vmeminfo._fields:
		if field == "total" or field == "available" or field == "percent":
			pass
		else:
			newScreen.pushNextScreen(definePerMemtypeInfoScreen(vmeminfo, field))
	return newScreen

def defineDiskMenuScreen():
	newScreen = CfaScreen.CfaScreen("DiskSubmenu")
	partitions = psutil.disk_partitions()
	newScreen.pushNextScreen(defineMainPartitionsScreen())
	for partition in partitions:
		newScreen.pushNextScreen(definePerPartitionInfoScreen(partition))
	return newScreen

def defineTempMenuScreen():
	newScreen = CfaScreen.CfaScreen("TempSubmenu")
	sensorTemperatures = psutil.sensors_temperatures()
	for sensor, temperatures in sensorTemperatures.iteritems():
		index = 0
		for temperature in temperatures:
			if not temperature.label:
				label = sensor + str(index)
			else:
				label = temperature.label.replace(' ', '')
			newScreen.pushNextScreen(definePerTempSensorInfoScreen(sensor, label, index))
			index += 1
	return newScreen


# third Level screens.

# System Info, single, Screen.
def defineMainSysInfoScreen():
	newScreen = CfaScreen.CfaScreen("SysInfo")

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		Kernel = str(os.uname()[0][:10])
		newScreen.widgets['os-type_widget'] = screen.add_string_widget("os-type_widget", "Kernel: " + Kernel, 1, 1)
		Version = str(os.uname()[2][:10])
		newScreen.widgets['hostname_widget'] = screen.add_string_widget("hostname_widget", "Version: " + Version, 1, 2)
		hostname = str(os.uname()[1][:10])
		newScreen.widgets['kernel_widget'] = screen.add_string_widget("kernel_widget", "Host: " + hostname, 1, 3)
	newScreen.init = init

	return newScreen


# CPU Info, entry/main Screen, and per-CPU screens
def defineMainCpuScreen():
	newScreen = CfaScreen.CfaScreen("CPUInfo")
	newScreen.tDelta = 300

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		cpucount = psutil.cpu_count()
		newScreen.widgets['freq_widget'] = screen.add_string_widget("freq_widget", "Total cores: " + str(cpucount), 1, 1)
		newScreen.widgets['prcnt_widget'] = screen.add_string_widget("prcnt_widget", "Avg. usage: 0%", 1, 2)
		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		percent = psutil.cpu_percent()
		barlength = int(percent)
		newScreen.update_widget_text(newScreen.widgets['prcnt_widget'], "Avg: " + str(percent) + "%")

		newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)
		newScreen.update_LED_meter_bar(percent)
	newScreen.updateWidgets = updateWidgets

	return newScreen

def definePerCpuInfoScreen(CpuIndex):
	newScreen = CfaScreen.CfaScreen("CPU" + str(CpuIndex) + "info")
	newScreen.tDelta = 300

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		newScreen.widgets['freq_widget'] = screen.add_string_widget("freq_widget", "0 MHz", 1, 1)
		newScreen.widgets['prcnt_widget'] = screen.add_string_widget("prcnt_widget", "0%", 1, 2)
		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		freq = str(psutil.cpu_freq(percpu=True)[CpuIndex][0])
		newScreen.update_widget_text(newScreen.widgets['freq_widget'],"CPU" + str(CpuIndex) + ": " + freq + "MHz")

		percent = psutil.cpu_percent(interval=1, percpu=True)[CpuIndex]
		newScreen.update_widget_text(newScreen.widgets['prcnt_widget'],"CPU" + str(CpuIndex) + ": " + str(percent) + "%")

		barlength = int(percent)
		newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)

		newScreen.update_LED_meter_bar(percent)
	newScreen.updateWidgets = updateWidgets

	return newScreen


# Memory Info, entry/main Screen, and per-memory type screens
def defineMainMemScreen():
	newScreen = CfaScreen.CfaScreen("MemInfo")
	newScreen.tDelta = 300

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		vmeminfo = psutil.virtual_memory()
		newScreen.widgets['total_widget'] = screen.add_string_widget("total_widget", "Total: " + format_bytes(vmeminfo.total), 1, 1)
		newScreen.widgets['available_widget'] = screen.add_string_widget("available_widget", "Available: 0B", 1, 2)
		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		vmeminfo = psutil.virtual_memory()
		available = format_bytes(vmeminfo.available)
		newScreen.update_widget_text(newScreen.widgets['available_widget'],"Avail: " + available)

		percent = vmeminfo.percent
		barlength = int(percent)
		newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)

		newScreen.update_LED_meter_bar(percent)
	newScreen.updateWidgets = updateWidgets

	return newScreen

# Memory usage per memory type info screens
def definePerMemtypeInfoScreen(meminfo, memtype):
	newScreen = CfaScreen.CfaScreen(memtype)
	newScreen.tDelta = 300

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		newScreen.widgets[memtype + '_widget'] = screen.add_string_widget(memtype + "_widget", memtype + ": 0B", 1, 1)
		newScreen.widgets['percent_widget'] = screen.add_string_widget("percent_widget", "0%", 1, 2)
		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		vmeminfo = psutil.virtual_memory()
		percent = float(getattr(vmeminfo, memtype)) / float(vmeminfo.total) * 100
		newScreen.update_widget_text(newScreen.widgets[memtype + '_widget'],memtype + ": " + format_bytes(getattr(vmeminfo, memtype)))

		newScreen.update_widget_text(newScreen.widgets['percent_widget'], memtype + ": %.1f%%" % percent)

		barlength = int(percent)
		newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)

		newScreen.update_LED_meter_bar(percent)
	newScreen.updateWidgets = updateWidgets

	return newScreen


# Disk usage per partition/mount-point info screens
def defineMainPartitionsScreen():
	newScreen = CfaScreen.CfaScreen("DiskInfo")
	newScreen.tDelta = 300

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		newScreen.partitions = psutil.disk_partitions()
		newScreen.total = 0
		for partition in newScreen.partitions:
			newScreen.total += psutil.disk_usage(partition.mountpoint).total
		newScreen.widgets['total_widget'] = screen.add_string_widget("total_widget", "Total: " + format_bytes(newScreen.total), 1, 1)
		newScreen.widgets['available_widget'] = screen.add_string_widget("available_widget", "Available: 0B", 1, 2)
		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)

	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		free = 0
		used = 0
		for partition in newScreen.partitions:
			free += psutil.disk_usage(partition.mountpoint).free
			used += psutil.disk_usage(partition.mountpoint).used
		newScreen.update_widget_text(newScreen.widgets['available_widget'], "Available: "  + format_bytes(free))

		percent = float(used) / float(newScreen.total) * 100
		barlength = int(percent)
		newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)

		newScreen.update_LED_meter_bar(percent)
	newScreen.updateWidgets = updateWidgets

	return newScreen


def definePerPartitionInfoScreen(partition):
	newScreen = CfaScreen.CfaScreen(partition.mountpoint)
	newScreen.tDelta = 500

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		newScreen.mountpoint = partition.mountpoint
		newScreen.total = format_bytes(psutil.disk_usage(partition.mountpoint).total)
		newScreen.widgets['mount_widget'] = screen.add_string_widget("mount_widget", "mount: " + newScreen.mountpoint, 1, 1)
		newScreen.widgets['used_widget'] = screen.add_string_widget("used_widget", "0B", 1, 2)

		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		used = format_bytes(psutil.disk_usage(partition.mountpoint).used)
		newScreen.update_widget_text(newScreen.widgets['used_widget'], used + " of " + newScreen.total)

		percent = psutil.disk_usage(partition.mountpoint).percent
		barlength = int(percent)
		newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)

		newScreen.update_LED_meter_bar(percent)
	newScreen.updateWidgets = updateWidgets

	return newScreen

def definePerTempSensorInfoScreen(sensor, label, index):
	newScreen = CfaScreen.CfaScreen(label)
	newScreen.tDelta = 500

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		newScreen.label = label
		newScreen.critical = psutil.sensors_temperatures()[sensor][index].critical
		newScreen.widgets['sensor_widget'] = screen.add_string_widget("mount_widget", "sensor: " + newScreen.label, 1, 1)
		newScreen.widgets['current_widget'] = screen.add_string_widget("current_widget", "0C", 1, 2)

		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		current = psutil.sensors_temperatures()[sensor][index].current
		percent = float(current / float(newScreen.critical) * 100)
		newScreen.update_widget_text(newScreen.widgets['current_widget'], str(current) + "C")

		barlength = int(percent)
		newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)

		newScreen.update_LED_meter_bar(percent)
	newScreen.updateWidgets = updateWidgets

	return newScreen


# Auxiliary functions/methods
def format_bytes(bytes_num):
    sizes = [ "B", "KB", "MB", "GB", "TB" ]
    i = 0
    dblbyte = bytes_num
    while (i < len(sizes) and  bytes_num >= 1024):
            dblbyte = bytes_num / 1024.0
            i = i + 1
            bytes_num = bytes_num / 1024
    return str(round(dblbyte, 2)) + sizes[i]
