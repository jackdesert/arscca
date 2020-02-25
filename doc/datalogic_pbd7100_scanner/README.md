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

MAKE SURE THE CABLE SNAPS INTO PLACE
You may need to remove the bottom cover of the base in order to accomplish this.
If it doesn't snap it, it may not be connected.

Cable Pinout
------------

See pp 302 (ref)
But also see pp 52 (RTS/CTS can be ignored)


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



USAGE
-----

### Power On And Check if Paired
  - Insert Battery
  - Hold down trigger 2+ seconds until you hear four high beeps (Now it's on)
  - If the scanner is already paired with a base, you will also hear beeps L-M-H
    and the base LED will blink at 50hz for half a second (transmission).


### Pair with Base if Not Paired

  - Hold Base Button more than 1 second, then release
    (You may have to pry it up---spring return is weak)
    Now Base is in "Pairing Mode", and LED will blink
  - While base is in "Pairing Mode", scan the base barcode.
  - Success is indicated by L-M-H

### Scan a Barcode

  - Point at a barcode and pull the trigger
  - Success indicated by three things:
    - The red laser turns off and a green dot appears in its place
    - The yellow base LED on the base blinks on for a super short duration (transmission?)
    - The lights on the USB-serial converter light up (transmission)
    - The green base LED turns on for one second.
    - The scanner beeps (hard to tell if it's a single H or another note with it)

How to Turn it On
-----------------


Insert battery, then hold trigger until you hear four high beeps.


How to Ask Where the Scanner is
-------------------------------

Press the Yellow button on the base and immediately release it
(Scanner will beep at 1Hz for several seconds)


LED Indications
---------------

See pp 316, Reference.

BASE LED INDICATIONS
50 Hz Yellow    Transmission in Progress


HANDHELD LED INDICATIONS
1 Hz Green  (Programming Mode)



BEEP Indications
----------------

H M L  (Power to base disconnected)
L M H  (Power to base reconnected)

L   (Attempted to scan barcode, but base is disconnected)



Open Axware

Plug in Serial to USB Converter

Bar Coding -> Bar Code Scanner Config

Radio Button: Select "Use Default Bar Code Values"
Bar Code Width (Printing): 60 (mm) (or as wide as will fit on the labels)
Checkboxes: Check "Use strict bar code scanning" (This makes it so any errors will generate a popup)
Scanner Port: Make sure something is selected. Try disconnecting the Serial to USB converter, click "Refresh Port List" to see which one went away. Then reconnect it and click "Refresh Port List" again. Now you know which one is for the scanner---choose that on.

Parity: None (This matches the scanner default)
Baud Rate: 9600 (This matches the scanner default)
Repeat Scan Timeout: (Default is 2, but set it more if that makes sense)
Prefix Delimiter: (Leave Blank)
Postfix Delimiter (Thi is IMPORTANT): 0x0d (This is the scanner default and represents a carriage return, sometimes depicted as "\r". But as of the 2020 version of AxWare, this "\r" is not printed in the staging log, so if you don't get this you'll wonder why it keeps saying "Warning: scanned entry 'DS 32' not found. What it actually scanned was 'DS 32\r', but the log doesn't print that.

You can verify what EXACTLY is coming through your scanner by connecting it to a computer and
running something like this python script, which will print ALL CHARACTERS that come through.
(PuTTY is not adequate to show you exactly what's coming through, because PuTTY swallows "\r")

    import serial
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=10)
    try:
        while True:
            data = ser.read()
            print(data)
    finally:
        ser.close()

The scanner in its default config, when it reads "HS 14" on a barcode, will print this;

    b'H'
    b'S'
    b' '
    b'1'
    b'4'
    b'\r'

Note the b'\r' at the end. That's the same as 0x0d or 0x0D.



Note it is possible to configure the scanner to NOT send a postfix character,
but then we have to remember that the scanner requires a non-default configuration.
So for now, keep the scanner with its default settings and just tell axware to use 0x0d as the
postfix character.


computer and "not recognized".


Click "Refresh Port List" if your COM port does not show up.
Select the appropriate Port. (Name depends on make/model of Serial to USB converter)
Set Bar Code Width (Printing) to something large like 60 (mm).
Make sure "Use strict bar code scanning" is checked. (So it will show popup if any errors)
Make sure "Use default bar code values" is checked. (Class CarNumber)
Click OK

Bar Coding -> Activate Scanner
Bar Coding -> Staging Mode

Printing Bar Code Labels
------------------------

First make sure there is a default printer selected (Setup -> Options -> Print Settings)

To print one label, right click on a participant and select "Print bar code label"
To print several labels, highlight several participants (Click, then SHIFT + Click)
and click Bar Coding -> Print Bar Codes for Selected Entries

To print all labels,
Bar Coding -> Print Bar Codes for All Entries

Scan a bar code.

