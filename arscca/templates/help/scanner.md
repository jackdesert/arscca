# DataLogic PBT7100 Barcode Scanner & AxWare

(You won't need everything in this document every time you set up the scanner. But if it doesn't work, this guide will get you going.)

## 1. Background

- AxWare only supports scanners that support the serial interface. That's why we have serial scanners with Serial-to-USB converters
- The club owns two scanners (handheld), two bases, one power supply, and three batteries. Either of the handhelds can be used with either of the bases. Only one handheld can be linked with a base at a time. See "Link the Handheld with the Base"
- This document comprises the "Quick Start" for connecting the PBT7100 to AxWare. The full reference guide for the PBT7100 is available at the end of this document. AxWare documentation is availble through the AxWare help menu.


## 2. Connecting the Cables

- Connect the power supply to the base and plug it into an outlet.
- Place the base near the laptop.
- Plug the Serial-USB adapter into the laptop
- Connect the (coiled) CAB-408 RS232 cable between the base and the Serial-USB adapter. (This cable looks like an Ethernet connector, but it actually has 10 conductors instead of 8.)


## 3. Turn On the Handheld

- Insert the battery fully into the handheld.
- Hold the trigger down for about three seconds until you hear four high beeps. (Now it's on)


## 4. Link the Handheld with the Base

If the scanner is already paired with a base, you will also hear beeps L-M-H, and the base LED will blink at 50hz for half a second to indicate transmission. If you do not hear this, you must link the handheld as follows:



- Hold Base Button for two seconds, then release. (If button doesn't spring back up immediately, pry it up with your fingernail)
- Now Base is in "Linking Mode", and LED will blink
- While base is in "Linking Mode", scan the barcode located in the cup of the base.
- Success is indicated by L-M-H beep.


Only one handheld may be linked at a time. If you link the other handheld, the first one will no longer be linked.


## 5. Verify Data Through Cable
Scan a barcode (just about anything will do) and listen to the sound it makes. With the default settings, you get a single beep when you get a successful scan. Also the transmission LED on the base will blink ever so briefly. If you make it this far, the handheld and the base are properly linked.

If the handheld and base are linked, you will see all of this:

- The red laser turns off and a green dot appears in its place
- The yellow base LED on the base blinks on for a super short duration (transmission?)
- The lights on the USB-serial converter light up (transmission)
- The green base LED turns on for one second.
- The scanner beeps (hard to tell if it's a single H or another note with it)


Note that the handheld and the scanner being linked is a prerequisite for getting data to the computer, but the scanner and handheld can be linked even if the cable to the computer is not present

Scan a barcode again, and this time watch the LEDs on the Gearmo GM-FTDI-A12 Serial to USB Converter. A couple of the LEDs will light up ever so briefly when you scan the barcode. If this is successful, it means data is making all the way out through the first cable. If no data goes through the first cable, check that it is properly seated in the base. If there is still no data, get a new cable. (See Part Numbers at the end of this document)



## 6. Configure AxWare Bar Code Settings


- Click Bar Coding -> Bar Code Scanner Config
- <img src='{{ settings_png }}'></img>
- Radio Button: Select "Use Default Bar Code Values". (This means car class + car number)
- Bar Code Width (Printing): 60 (mm) (or as wide as will fit on the labels)
- <span style='color: red; font-weight: bold;'>Checkboxes: Check "Use strict bar code scanning"</span> (This makes it so any unrecognized barcodes that come through will raise a popup error instead of being silently ignored)
- Scanner Port: Make sure something is selected. Try disconnecting the Serial to USB converter, click "Refresh Port List" to see which one went away. Then reconnect it and click "Refresh Port List" again. Now you know which one is for the scanner---choose that on.
- Parity: None (This matches the scanner default)
- Repeat Scan Timeout: (Default is 2, but set it more if that makes sense)
- Prefix Delimiter: (Leave Blank)
- <span style='color: red; font-weight: bold;'>Postfix Delimiter (This is IMPORTANT): 0x0d </span> (See the section in Troubleshooting on Postfix Delimiters)
- Select the appropriate Port. (Name depends on make/model of Serial to USB converter). Click "Refresh Port List" if your COM port does not show up.
- Click OK





## 7. Print Bar Code Labels in AxWare

First make sure the correct printer is selected (Setup -> Options -> Print Settings)


- To print one label, right click on a participant and select "Print bar code label"
- (Not working yet) To print several labels, highlight several participants (Click, then SHIFT + Click)
and click Bar Coding -> Print Bar Codes for Selected Entries
-  (Not working yet) To print all labels, Bar Coding -> Print Bar Codes for All Entries


### 7a. Bar Coding Size

Click In BarCoding -> Bar Code Scanner Config



In the upper right corner is "Bar Code Width". You must **select** a new width. If you
merely type over that last one, it doesn't stick.

Note this is not total width, it is more like "The width of a single character", and it's not
clear what the units of measurement are.



Basically, smaller "width" means the bars in the bar code are closer together.
Smaller is generally better as long as the scanner can still read them.
The PBT7100 appears to read sizes as small as width 25.


### 7b. Bar Coding Position

In order to get the bar code positioned properly on the label,
make sure that
BarCoding -> Dedicated Bar Code Printer
is selected.



At the moment, printing in bulk causes the text and bar code to be misplaced
within the label. Perhaps we will figure that out.



### 7c. Ripping Labels

Pull DOWN and to the side. (The teeth are UNDER the feeder, not above.)


### 7d. Label Jammed (BEEP)

If the label printer beeps and does not print, press the blue button on the front.
It will feed out a couple labels and you can print again.

If a label disintegrates inside the printer, and you need to pull it out,
there is a release mechanism on the left.






## 8. Activate Scanner in AxWare

There are two places you can activate the scanner in AxWare.
The first is in the menu, **Bar Coding -> Activate Scanner**. The second is the icon
in the toolbar.

When the scanner is activated, the icon (in the menu and the toolbar) will
gain a border around them indicating they are selected.

<img style='display: block' src='{{ icons_png }}'></img>

If this border is hard to
see, click **View -> Application Look -> Windows 2010 -> Blue 2010**. This gives
muted red borders which are easy to see.

Also when the scanner is activated, several lines will display in the **registration log**.
You can clear this log to make it more obvious which lines are new.

When the scanner is deactivated, a single line will display in the **registration log**.

The registration log can be viewed by clicking **View -> Registration Log**.
Often the last line of the registration log will be cut off and hard to read.
This is a pain, but if you resize the staging log by just a couple of pixels
you can by trial and error find a size where the last line will display.

### 8a. Select Staging Mode

Select Staging Mode from the toolbar or from the Bar Coding menu.

Staging Mode means when you scan a barcode, that driver will be added to the bottom of the staging grid.

Registration Mode means when you scan a barcode, that driver will be highlighted in the list of registered drivers. (You can also sort this list by double clicking on any header.)



## 9. Verify AxWare Receives Scanner Data

- Scan a bar code. If that car shows up in the staging screen, you're good to go.
- If you get a pop up with an error, view the staging log. Click View -> Staging Log. This will show you all the data that comes through. If the staging log says the barcode was not found, verify that the barcode you scanned represents a person actually in the event. If it represents a registered driver but it still was not recognized, see Troubleshooting.


## 10. Verify Alert Pops Up For Non-Registered Drivers

- Scan a bar code from a non-registered driver, or from any barcode that you have
  lying around.
- Make sure an alert pops up in AxWare. This is what you want to have happen if an
  unregistered driver (or a driver with an unknown barcode) is scanned.
  Otherwise the scan silently fails and the run will be attributed to the next driver in line.
- If alert does not pop up, go back to Barcoding -> Bar Code Setup and enable Strict Scanning.

## 11. Running Start
With the scanner activated, whoever is working the computer STILL has the ability to add other cars to the staging grid. Also, if you scan the same barcode twice, it will show up TWICE in the staging grid. If this happens and it was an accident, just call over the radio to have the computer worker delete one of them.


The club has two identical scanners. While you are scanning with one, make sure the other is charging on the base. This way if battery in one runs out, there is another charged battery.




## 12. Troubleshooting
<h3>11a. Strange Blinking Pattern</h3>
If it gets stuck in some strange mode, power cycle both the handheld (remove the battery, then insert again) and the base (disconnect, then reconnect power adapter). When they power back on, listen for the L M H beep pattern that indicates the handheld and the base are linked. If they are not linked, go back to the section "Link the Handheld with the Base"



### 12b. Postfix Delimiter

The PBT7100 is configurable such that given the barcode "STS 57", it can either send just "STS 57", or it can also include some delimiting character and the start and/or end of the string.
By default, the PBT7100 uses no prefix character, but it uses 0x0D as the postfix character.
0x0D is sometimes depicted as "\r". It's the carriage return character.



Unfortunately, the staging log in AxWare does not display "\r" when telling you what barcode
was scanned. So if you configure AxWare to use no prefix or postfix character, and the PBT7100
is using default settings, none of your barcodes will be recognized. And the staging log will
say "Warning: scanned entry 'STS 57' not recognized."
(It would be better if it said "Warning: scanned entry 'STS 57\r' not recognized.")
Then you would at least be alerted that there is an extra character coming from the scanner
and that's why AxWare is not recognizing the scan.



If the staging log shows that a scan came through, but it's not recognized, double check
your values for postfix character in Bar Coding -> Settings.



If you have the postfix character set correctly and it's still coming through strange,
see the section on Verifying Exactly What Data Comes Through.



### 12c. Verifying Exactly What Data Comes Through

If the staging log shows data coming through, but AxWare still does not match it up with a particular driver, you can verify what EXACTLY is coming through your scanner by connecting it to a computer and
running something like this python script, which will print ALL CHARACTERS that come through.
(PuTTY is not adequate to show you exactly what's coming through, because PuTTY swallows "\r")

<pre>

    import serial
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=10)
    try:
        while True:
            data = ser.read()
            print(data)
    finally:
        ser.close()
</pre>
The scanner in its default config, when it reads "HS 14" on a barcode, will print this;
<pre>

    b'H'
    b'S'
    b' '
    b'1'
    b'4'
    b'\r'
</pre>

Note the b'\r' at the end. That's the same as 0x0d or 0x0D.



Note it is possible to configure the scanner to NOT send a postfix character,
but then we have to remember that the scanner requires a non-default configuration.
So for now, keep the scanner with its default settings and just tell axware to use 0x0d as the
postfix character.



### 12d. Resetting Scanner to Factory Defaults
The scanner has lots of configurable settings, but it works fine with AxWare with its default settings as long as you tell AxWare that the postfix character is 0x0d. To reset the scanner to factory defaults, scan this barcode
<img class='barcode' src='{{ reset_png }}'></img>



### 12e. Getting AxWare to Recognize Serial to USB Converter
If AxWare doesn't show the Serial to USB device, you may need to install a driver. But first try clicking the "Refresh Port List" button.


### 12f. Paging the Handheld

Press the Yellow button on the base and immediately release it.
(Handheld will beep at 1Hz for several seconds)







## 13. Additional Resources



- [PBT7100 Reference Guide](https://www.manualslib.com/download/1162650/Datalogic-Powerscan-Pbt7100.html)
- [PBT7100 Quick Ref](https://www.manualslib.com/manual/882484/Datalogic-Powerscan-Pbt7100.html)
- [Dymo LabelWriter 450 Turbo User Guide](https://download.dymo.com/UserManuals/labelwriter%20user%20guides/LabelWriter%20Printer%20User%20Guide.en.pdf)


### 13a. LED and Beep Indications (Handheld)

In general, a L M H beep is a good thing, and H M L is a bad thing, a successful scan is one piercing beep, and an unsuccessful scan is one Low beep.

- 10 H beeps in one second: Low battery

For more details, see  [LED and Beep Indications]({{ ref_page_314 }}) from the Reference Guide.




## 14. Part Numbers
<div class='space-1rem'></div>

**DataLogic PBT7100 Scanner w/ Base**

- Available used on Ebay


**DataLogic Power Supply**

- Model: SA06-12S05R-V
- P/N: SA06-12S05-V-3A
- Output: 2.4A @ 5.2V
- Available used on Ebay




**[DataLogic 90A051891 Scanner Cable](https://www.amazon.com/gp/product/B00164MFFW/)**

- Looks like an ethernet plug on one end, but it actually has 10 conductors instead of 8.
- The other end is a serial connection
- Model/description: DATALOGIC 90A051891 CAB-408 RS232 PWR COIL9PIN FEM 6FT COILED
- When this cable was new, it did not fit into the PBT7100 base. But by removing a bit of the rubber around the CAB-408 end it fit fine.


**[Gearmo GM-FTDI-A12 Serial to USB Converter](https://www.amazon.com/gp/product/B073ZJHNK1/)**

- Has LEDs built in so you can see when data is passed through
- FTDI chip works on Linux









