
# Tools for MicroPython Async Development

Inspired by [aiorepl](https://github.com/micropython/micropython-lib/tree/master/micropython/aiorepl),
**asyncmd** is an *asyncio* based set of tools to help with the development of asynchronous applications implemented in MicroPython.

*Asyncio* is ideal for running multiple tasks concurrently[^1], however an easy way to 
**interactively** inspect running tasks in the event loop was not available
until the introduction of [aiorepl](https://github.com/micropython/micropython-lib/tree/master/micropython/aiorepl),
an asynchronous MicroPython REPL.

This set of tools builds upon this *aiorepl* capacity to interact with tasks running in the event loop.

**asyncmd** is intended to be flexible and extensible i.e. minimum requirement is `aioctl.py`
and then every script builds upon *aioctl* functionality.

#### Features

* Create async **traceable tasks** that can be controlled, tracked, managed, debugged or profiled --> `aioctl.py`


    Create a task that can be stopped or restarted, inspect its result/return value, 
    internal error, traceback message, know how long it has been running or how long it has been done.
    Also allows to add a custom name/id to the task, or run a callback function when the task is stopped
    or throws an error. 
    
    e.g. ``● hello_task: status: running since 2023-03-16 00:00:19; 4 s ago``

* Asynchronous **RAM logging** --> `aiolog.py`
    
    Create a "ring buffer stream" to log tasks output indefinitely. It 
    allocates a predefined amount of RAM and rotates automatically so it never allocates
    more RAM than the one predefined. 
    Also allows to interactively inspect its content the same way as using `cat`, `cat | grep` or `tail -F `, `tail -F | grep`.
    
    e.g. `2023-03-16 00:00:19 [pyb] [INFO] [hello_task] LED 3 toggled!`


* Asynchronous **scheduling** --> `aioschedule.py`

    Create a task and run it in `s` seconds (*from event loop start or task creation*) or at a time `(timetuple)` and repeat every `n` seconds. 
    This has a "scheduler task loop" that checks every second its schedule and runs a scheduled task when the time is due.

    e.g. 
    
    ```
    ● world_task: status: done @ 2023-03-16 00:12:44; 48 s ago --> result:
    ┗━► schedule: last @ 2023-03-16 00:12:39 --> next in 37 s  @ 2023-03-16 00:13:16
    ```


* Asynchronous **services**[^2] --> `aioservice.py`, `aioclass.py`, `aioservices/services`, `services.config`

    Create a service that can have one or more tasks, install/list/get status of services, load/unload, config services 
    as enabled or disabled, config service main task args and keyword args, get the traceback of services that failed to load, init/boot services 
    following a priority depending of another service dependency...

    e.g. 
    ```
    [ OK ] Service: hello_core.service from ./aioservices/services/hello_core_service.py loaded
    [ OK ] Service: hello_low.service from ./aioservices/services/hello_low_service.py loaded
    [ OK ] Service: world.service from ./aioservices/services/world_service.mpy loaded
    [ OK ] Service: hello.service from ./aioservices/services/hello_service.mpy loaded
    [ OK ] Service: watcher.service from ./aioservices/services/watcher_service.mpy loaded
    [ ERROR ] Service: dofail.service from ./aioservices/services/dofail_service.mpy not loaded: Error: ZeroDivisionError
    ```
    
    Finally to inspect a task or service enabling debug mode in `aioctl` gives the full service/task status
    
    ```
    ● hello.service - Hello example runner v1.0
        Loaded: Service: hello.service from ./aioservices/services/hello_service.mpy
        Active: (active) running since 2023-03-16 00:35:00; 00:02:31 ago
        Type: runtime.service
        Docs: https://github.com/Carglglz/asyncmd/blob/main/README.md
        Stats:     Temp: 25.79095 C   Loop info: exec time: 5 ms; # loops: 186
        Task: <Taskctl object at 20003010>
        ┗━► args: (Service: hello.service from ./aioservices/services/hello_service.mpy, 3, 10)
        ┗━► kwargs: { 'on_error': <bound_method>,
                      '_id': 'hello.service',
                      'log': <Logger object at 20008010>,
                      'on_stop': <bound_method> }
    2023-03-16 00:35:10 [pyb] [INFO] [hello.service] LED 3 toggled!
    2023-03-16 00:35:20 [pyb] [INFO] [hello.service] LED 2 toggled!
    ```


## Install

### Manual
For `aioctl.py`, `aioschedule.py`, `aiolog.py`, `aioservice.py` and `aioclass.py` just upload the scripts to the device[^3]


For `aioservices/services` make the directories first and then upload  `aioservices/services/__init__.py` (or directly sync `aioservices`)

Then to install a service upload it to this directory.

### Using MIP
See [MIP](https://docs.micropython.org/en/latest/reference/packages.html)

*Note that Network-capable boards must be already connected to WiFi/LAN and have internet access* 

To install `asyncmd` using `mip`
```
>>> import mip
>>> mip.install("github:Carglglz/asyncmd", target=".")
```

For simple installation .i.e only `aioctl.py`

```
>>> import mip
>>> mip.install("github:Carglglz/asyncmd/aioctl.py")
```

To install services using `mip`

```
>>> import mip
>>> mip.install("github:Carglglz/asyncmd/services", target=".")

# or only network (core network, wpa_supplicant)

>>> mip.install("github:Carglglz/asyncmd/services/network", target=".")

# or develop (watcher, mip, unittest)

>>> mip.install("github:Carglglz/asyncmd/services/develop", target=".")

# or ble 

>>> mip.install("github:Carglglz/asyncmd/services/ble", target=".")
```



Note that this set of tools (with exception of `aioservices/services`) can be frozen in the firmware too which will be the best option for saving memory. To freeze services, see `frz_services`. To learn more about freezing packages/modules see
[MicroPython manifest files](https://docs.micropython.org/en/latest/reference/manifest.html#manifest)


## Example
This basic example demonstrates how to use `@aioctl.aiotask` decorator to create
a traceable task

e.g. `async_blink.py`

```python
from machine import Pin
import uasyncio as asyncio
import aiorepl
import aioctl

# Define a task

@aioctl.aiotask
async def blink(pin, sleep=5):
    led = Pin(pin, Pin.OUT)
    while True:
        led.on()
        await asyncio.sleep_ms(500)
        led.off()
        await asyncio.sleep(sleep)


async def main():
    print("Starting tasks...")
    # Add tasks
    aioctl.add(blink, 2, sleep=5)
    aioctl.add(aiorepl.task, name="repl")
    # await tasks
    await asyncio.gather(*aioctl.tasks())


asyncio.run(main())
```
To run, copy and paste in paste mode or upload the script to the device then
```
>>> import async_blink
Starting tasks...
Starting asyncio REPL
--> import aioctl
--> aioctl.status()
● repl: status: running since 2023-03-16 11:27:11; 38 s ago
● blink: status: running since 2023-03-16 11:27:11; 38 s ago

# Enable aioctl debug mode
--> aioctl.debug()
debug mode: True
--> aioctl.status()
● repl: status: running since 2023-03-16 11:27:11; 00:01:01 ago
    Task: <Taskctl object at 2000c9d0>
    ┗━► args: ()
    ┗━► kwargs: {}
● blink: status: running since 2023-03-16 11:27:11; 00:01:01 ago
    Task: <Taskctl object at 2000c7d0>
    ┗━► args: (2,)
    ┗━► kwargs: { 'sleep': 5 }

# Stop blink task
--> aioctl.stop("blink")
True
--> aioctl.status()
● repl: status: running since 2023-03-16 11:27:11; 00:01:25 ago
    Task: <Taskctl object at 2000c9d0>
    ┗━► args: ()
    ┗━► kwargs: {}
● blink: status: stopped @ 2023-03-16 11:28:33; 3 s ago --> result:
    Task: <Taskctl object at 2000c7d0>
    ┗━► runtime: 00:01:22
    ┗━► args: (2,)
    ┗━► kwargs: { 'sleep': 5 }

# Change sleep kwarg
--> aioctl.group().tasks["blink"].kwargs.update(sleep=3)

# Start again
--> aioctl.start("blink")
True
--> aioctl.status()
● repl: status: running since 2023-03-16 11:27:11; 00:06:35 ago
    Task: <Taskctl object at 2000c9d0>
    ┗━► args: ()
    ┗━► kwargs: {}
● blink: status: running since 2023-03-16 11:33:43; 3 s ago
    Task: <Taskctl object at 20016110>
    ┗━► args: (2,)
    ┗━► kwargs: { 'sleep': 3 }

# Add another blink task
--> aioctl.add(blink, 3, sleep=6)
--> aioctl.status()
● blink@1: status: running since 2023-03-16 11:40:56; 11 s ago
    Task: <Taskctl object at 20015350>
    ┗━► args: (3,)
    ┗━► kwargs: { 'sleep': 6 }
● repl: status: running since 2023-03-16 11:27:11; 00:13:56 ago
    Task: <Taskctl object at 2000c9d0>
    ┗━► args: ()
    ┗━► kwargs: {}
● blink: status: running since 2023-03-16 11:37:48; 00:03:19 ago
    Task: <Taskctl object at 20010070>
    ┗━► args: (2,)
    ┗━► kwargs: { 'sleep': 3 }

```

See more [examples](examples/) to know how to add *"async" logging*,
callbacks, debugging errors, get results, scheduling and finally some [examples](lib-aioservices/) of `aioservice`
implementation.

## Docs

### [aioctl](docs/aioctl.md)



### [aiolog](docs/aiolog.md)


### [aioschedule](docs/aioschedule.md)


### [aioservice](docs/aioservice.md)


### [aioservices](docs/aioservices.md)


### [app](app/)

### [async_modules](async_modules/)

    

## Examples

Set of examples of increasing complexity to show the capabilities
of these tools.

- aiotasks --> [examples](examples)

- aioservices --> [example-aioservices](example-aioservices)


#### Use cases for **aioctl**

 - Building block for *asyncio* based applications that makes tasks
  traceable, manageable and easily debugged

#### Use cases for **aioservice**

 - Debug, develop and manage complex *asyncio* applications
 - Create reproducible/repeatable builds that can be fine tuned for each device using config files
 - Long term running and modular applications that need to be resilient and remotely:
    - monitored
    - debugged
    - updated


## Tutorial

See a tutorial for `unix` port in [develop example](develop/unix) using *MQTT*, *asyncmd* CLI and the following services: 
    
- `aiomqtt.service` --> control/debug and get/check OTA updates notifications over MQTT 
- `aiomqtt_sensor_bme280.service` --> sensor (simulated) reports Temperature,Humidity,Pressure over MQTT  
- `mip.service` --> check and update mip installable packages
- `unittest.service` --> check and run new tests regularly.
- `watcher.service` --> watch services tasks to add resiliency and enable watchdog to secure
  device continuous operation with minimum downtime

See a tutorial for `esp32` port in [develop example](develop/esp32) using *MQTT*, *asyncmd* CLI and the following services: 
    
- `aiomqtt.service` --> control/debug and get/check OTA updates notifications over MQTT 
- `aiomqtt_sensor_bme280.service` --> sensor (simulated) reports Temperature,Humidity,Pressure over MQTT  
- `ota.service` --> async OTA firmware upgrades using `asyncmd` CLI
- `network.service` --> enable WiFi connection and WebREPL (optional)
- `wpa_supplicant.service` --> check WiFi connection and reconnects if disconnected
- `watcher.service` --> watch services tasks to add resiliency and enable watchdog to secure
  device continuous operation with minimum downtime

## asyncmd CLI

### [asyncmd cli](cli/)


## Tested on ports:

- esp32 (WROOM ESP32-D0WDQ6 revision v1.0)
- stm32 (pyboard) (STM32F405RG)
- unix (see [develop/unix](develop/unix))

### Notes

[^1]: *Runnnig*
*multiple tasks concurrently where timing precision is only needed to be held up to a certain degree
which can vary with the number of tasks running , the amount of time they
take to run and how frequent they are scheduled*

[^2]: *Inspiration comes from Linux [systemd](https://github.com/systemd/systemd) specially `systemctl` and `journalctl`.*

[^3]: *Better if compiled to `.mpy` using `mpy-cross` to save memory, see [mpy-cross](https://docs.micropython.org/en/latest/reference/glossary.html#term-cross-compiler)*





