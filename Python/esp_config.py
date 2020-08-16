import os

#os.system('python /Users/MarkNyberg/Library/Python/2.7/lib/python/site-packages/esptool.py -p /dev/tty.SLAB_USBtoUART erase_flash')
#os.system('python /Users/MarkNyberg/Library/Python/2.7/lib/python/site-packages/esptool.py -p /dev/tty.SLAB_USBtoUART -b 115200 write_flash --flash_size=detect 0 ~/Downloads/esp8266-20200421-v1.12-388-g388d419ba.bin')
os.system('python /Users/MarkNyberg/Library/Python/2.7/lib/python/site-packages/ampy/cli.py -p /dev/tty.SLAB_USBtoUART put  ~/Downloads/micropython-charlcd-master/LCD.py LCD.py ')
os.system('python /Users/MarkNyberg/Library/Python/2.7/lib/python/site-packages/ampy/cli.py -p /dev/tty.SLAB_USBtoUART put  ~/Arduino/EI_redesign/Python/display_build.py main.py')
os.system('python /Users/MarkNyberg/Library/Python/2.7/lib/python/site-packages/ampy/cli.py -p /dev/tty.SLAB_USBtoUART put  ~/Arduino/EI_redesign/Python/display_funcs.py df.py')
os.system('python /Users/MarkNyberg/Library/Python/2.7/lib/python/site-packages/ampy/cli.py -p /dev/tty.SLAB_USBtoUART put  ~/Arduino/EI_redesign/Python/boot_26Jul_1145.py boot.py')