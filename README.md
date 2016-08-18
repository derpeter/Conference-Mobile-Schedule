This python script is intended to be used with the XML output
of Pentabarf [1] or frab [2]. Its still under development and partially quiet hacky.

The orginal code is done by Ulrich Dangel.

There is also an android app that makes use of the output of this script.
You can find it on github [3].

To run this code you need jinjan (pip install jinjan) and python 2

a valid command line would be 

   python generator.py -b https://programm.froscon.de -i https://programm.froscon.org/mobil/froschbutton.png -e https://froscon.org https://programm.froscon.de/2016/schedule.xml mobile.html

it recommendet to host the jquery files together with this application, edit templates/mobile.html to change this.
This jquery files can be found at https://code.jquery.com/

[1] [pentabarf](http://www.pentabarf.org)
[2] [frab](https://github.com/frab/frab) 
[3] [FrOSCon app](https://github.com/derpeter/FrOSCon)
