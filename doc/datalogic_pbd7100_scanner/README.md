Scanner
=======

Quick Reference Guide
---------------------

https://www.manualslib.com/manual/882484/Datalogic-Powerscan-Pbt7100.html

Reference Guide
---------------

https://www.manualslib.com/download/1162650/Datalogic-Powerscan-Pbt7100.html


Blinking
--------

The Amber LED will blink twice when a barcode is decoded
when the battery is getting low. pp 11 (quick ref)


Reset to Factory Settings
------------------------

Scann the barcode on pp 12 (quick ref).


Set BAUD Rate
-------------

pp 47 (ref) (default is 9600)



Stop Bits
----------

default: 1
see pp 50 (ref)


Parity (default == 1)
---------------------

See pp 51 (ref)


Handshaking Hardware Flow Control (default == RTS)
----------------------------

See pp 52 (ref)

ACK
---

See pp 57 (ref)


Transmission Failure (use with ACK)
--------------------

See pp 67


Setting Which Beeps Sound for Which Thing
-----------------------------------------

See pp 23 (ref)

### Good Read: When to Indicate
By default, it beeps as soon as barcode is decoded.
But you can change that to "after transmitted".
You can change it

(Enter/Exit programming mode; then scan; then Exit programming mode)

BUT for me, I selected "beep after transmit" even with the serial cable
disconnected, and it still beeps.

Error Beeps
-----------

See pp 313 (ref)


Cable
-----

The cable is a 10-pin (Larger than Ethernet)
(see Cable Pinout)

But also see pp 52 (RTS/CTS can be ignored)

Cable Pinout
------------

See pp 302 (ref)


PL2303 USB Adapter
-------------------
https://stackoverflow.com/questions/49104341/adding-driver-for-prolific-usb-rs232-pl2303-converter-to-linux-build-for-myb-am3


Connecting in Linux
-------------------

    sudo dmesg | grep Serial


### modprobe

https://blog.mypapit.net/2008/05/how-to-use-usb-serial-port-converter-in-ubuntu.html

    - lists some usb-serial converters on amazon
      (one of them specifically says Linux,
       one other one uses the same chipset)

    sudo modprobe usbserial vendor=0x067b product=0x2303

Linux Support
-------------

https://www.kernel.org/doc/html/v5.3/usb/usb-serial.html

  - list of devices supported
    (includes Prolific PL2303 that I have)


### Plug & Play

https://plugable.com/drivers/prolific/

This page says plug & play is recognized
