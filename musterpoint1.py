#!/usr/bin/python
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import pygame, sys, os
import binascii
import Adafruit_PN532 as PN532
import sqlite3
import datetime

from time import sleep,time
from pygame.locals import *

# Setup how the PN532 is connected to the Raspbery Pi/BeagleBone Black.
# It is recommended to use a software SPI connection with 4 digital GPIO pins.

# Configuration for a Raspberry Pi:
CS   = 18
MOSI = 23
MISO = 24
SCLK = 25

# Create an instance of the PN532 class.
pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)

# Get the firmware version from the chip and print it out.
ic, ver, rev, support = pn532.get_firmware_version()
print 'Found PN532 with firmware version: {0}.{1}'.format(ver, rev)

# Configure PN532 to communicate with MiFare cards.
pn532.SAM_configuration()

# window screen size
WINWIDTH = 656
WINHEIGHT = 512

pygame.font.init()

# load images

BGHOMESCREEN    = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/Admin_MusterPoint-01.png")
BGADMIN         = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/Musterpoint B-01.png")
BGMASTERPOINT   = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/Musterpoint_Profile-011.png")
BGTRACKER1      = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/visitorstracker1.png")
BGPRINTVIEW     = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/Musterpoint_Profile_White-02.png")
BGCLEARLOG      = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/Filters - Copy1.png")
CONFIRMBOX      = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/Message_Box3.png")
#TESTIMAGE       = pygame.image.load("/home/pi/image.jpg")
#TESTIMAGE       = pygame.transform.scale(TESTIMAGE,(195,195))
closebtn         = pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/X-Button.png")
closebtn1        = pygame.transform.scale(closebtn,(25,25))
#WINDISPLAY.blit(closebtn1, (615,20))

#            R    G    B
GRAY     = (100, 100, 100)
BLACK     = (0,   0,   0)
WHITE    = (255, 255, 255)
RED 	 = (170, 0,	  0)
ALPHA	 = (255, 255, 255,50)
GRAY1    = (109, 110, 113)
BGCOLOR = WHITE
cardno=''
employee_id=''
command=''
screenMode = 10
ypos=156
location=''
list_xy=[]
y=''
defaultloc='Musterpoint A'
defaultloc2='Musterpoint B'

pygame.font.init()	
pygame.init()
#pygame.mouse.set_visible(False)


WINDISPLAY = pygame.display.set_mode((WINWIDTH, WINHEIGHT),pygame.FULLSCREEN)
drawsurface = WINDISPLAY.copy()                                         # get a screen copy to draw on
drawsurface.set_colorkey(WHITE)                                         # the color black will be TRANSPARENT

#WINDISPLAY.blit(TESTIMAGE,((656 - TESTIMAGE.get_width() ) / 2,(512 - TESTIMAGE.get_height()) / 2))                                                    
WINDISPLAY.blit(BGHOMESCREEN,((656 - BGHOMESCREEN.get_width() ) / 2,(512 - BGHOMESCREEN.get_height()) / 2))


print 'Waiting for MiFare card...'
pygame.display.update()

#Define function mainscreen which holds the global variables screenMode and employeeno
def mainscreen():
        global screenMode
        global employeeno
        
        employee_id = ''
        screenMode = 10
        
        WINDISPLAY.blit(BGHOMESCREEN,((656 - BGHOMESCREEN.get_width() ) / 2,(512 - BGHOMESCREEN.get_height()) / 2))
        

def sql_viewlogs():
        global screenMode
        global ypos
        
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()
       
        query ="SELECT * FROM tbllogs  l left join tblemployee2 e on l.employee_id = e.employee_id"
        c.execute(query)

        all_rows = c.fetchall()
        for rows in all_rows:
    
                print rows[5],rows[1],rows[6]
                myfont1 = pygame.font.SysFont('Calibri',15 )
                employee_name = myfont1.render(rows[5], 1, WHITE)
                currenttime = myfont1.render(rows[1], 1, WHITE)
                department = myfont1.render(rows[6], 1, WHITE)
                
                WINDISPLAY.blit(employee_name, (50, ypos))      #Employee_name
                WINDISPLAY.blit(currenttime, (196, ypos))       #Time-In
                WINDISPLAY.blit(department, (285, ypos))
                
                ypos += 19
        conn.close()

def sql_logexist(cardnum):
        global cardno
        global screenMode
        global employee_id
        global sqlquery
        
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()
        sqlquery = "SELECT * FROM tbllogs where employee_id='%s'" % cardnum     
        c.execute(sqlquery)
        carduid = c.fetchone()
        if carduid == None:
                print "not found"
                return 0
        else:
                print "Found"
                return 1

        conn.close
        
def check_employee(cardnum):
        global cardno
        global screenMode
        global employee_id
        global sqlquery
        
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()
        sqlquery = "SELECT * FROM tblemployee2 where employee_id='%s'" % cardno     
        c.execute(sqlquery)
      
        conn.close
     
def check_carduid(cardnum):
        global cardno
        global screenMode
        global employee_id
        global location
        global department
        global sqlquery
        global employee_name
        global currenttime
        global currentdatetime
        global time
        global ypos
        global position
        global currentdate
        
       
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()
        
        if screenMode == 12:
                sqlquery = "SELECT * FROM tblemployee2 where employee_id='%s'" % cardnum

        c.execute(sqlquery)
       
        while True:
                carduid = c.fetchone()
                if carduid == None:
                        
                        print 'Not yet Register!'
                        
                if screenMode == 12:
                        if sql_logexist(carduid[0]) == 0:
                                
                                #print carduid[1],carduid[2]
                                myfont1 = pygame.font.SysFont('Calibri',15 )
                                employee_name = myfont1.render(carduid[1], 1, WHITE)
                                currenttime = myfont1.render(datetime.datetime.strftime(datetime.datetime.now(),'%H:%M'), 1, WHITE)
                                currentdatetime = myfont1.render(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S'),1, WHITE)
                                department = myfont1.render(carduid[2], 1, WHITE)
                                position=myfont1.render(carduid[3],1,WHITE)
                                location=myfont1.render(carduid[4],1,WHITE)

                                #if c.last_insert_rowid()==0:
                                #Display data from the database to the Masterpoint screen
                                WINDISPLAY.blit(employee_name, (50, ypos))      #Employee_name
                                WINDISPLAY.blit(currenttime, (196, ypos))       #Time-In
                                WINDISPLAY.blit(department, (285, ypos))        #Department
                                                       
                                #Load and Display images 
                                VISITORIMAGE    = pygame.image.load('%s.jpg' % cardnum)
                                VISITORIMAGE1   = pygame.transform.scale(VISITORIMAGE,(153,141))
                                WINDISPLAY.blit(VISITORIMAGE1, (454,152))
                                pygame.draw.rect(WINDISPLAY,BLACK,((449, 305),(165,29)),0)
                                
                                WINDISPLAY.blit(pygame.font.SysFont('Orator Std',18).render(carduid[1],1,WHITE),(449,307))
                                WINDISPLAY.blit(pygame.font.SysFont('Orator Std',18).render(carduid[3],1,WHITE),(449,320))
                                
                                conn.commit()
                                #increment y position of the display data
                               
                                ypos+=19 
                                sql_logs(carduid[0])
                        if sql_logexist(carduid[0]) == 0:
                                print "Already exist!"
                        break
                        
              
        conn.close()

def sql_empid(cardno):
        global screenMode

        
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()
       
        query ="SELECT Location FROM tblemployee2 where employee_id='%s'" % cardno
        c.execute(query)

        all_rows = c.fetchall()
        for rows in all_rows:
    
                currentlocation= rows[0]    
                print "location:",currentlocation
                break
        return currentlocation
        conn.close()
        

        
#Inserting data to the tbllogs 
def sql_logs(cardno):
        global screenMode
        
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()

        conn.execute("SELECT * FROM tblemployee2 where employee_id='%s'" % cardno)
        
        while True:
                        
                        sql_query = "INSERT INTO tbllogs VALUES(?,?,?,?)"
                        currentdate = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
                        currenttime = datetime.datetime.strftime(datetime.datetime.now(),'%H:%M')
                        params = (cardno,currenttime,currentdate,sql_empid(cardno))       #insert the values of cardno,currenttime,currentdate,loc
                        conn.execute(sql_query,params)
                        conn.commit()
                        print "entered"
                        
                        break
                        conn.close()
                        c.close()

#Function that will display all employees in Masterpoint A & B in Admin View
def retrieve_employee(squery):    
        global screenMode

        #Text Horizontal Position        
        x = 67
        x2=212
        if screenMode==11:
                x3=316
        else:
                x3=277
         
        if screenMode == 11:
                x4=467
        else:
                x4=399
        x5=516
        count=0
        
        #Text Vertical Position
        y = 156
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()

        query ="select Employee_name,LogTime, tbllogs.Location,Department,Position from tbllogs left join tblemployee2 on tbllogs.Employee_id = tblemployee2.Employee_id where tbllogs.Location in ('%s')" % squery
        c.execute(query)
        
        all_rows = c.fetchall()
        del list_xy[:]
        for rows in all_rows:
                if screenMode==13:
                        myfont =pygame.font.Font('/home/pi/Desktop/Musterpoint_rev2/fonts/arial.ttf',12)
                        label = myfont.render(rows[0], 1, BLACK)        #Employee Name
                        WINDISPLAY.blit(label, (x, y))
                        label1=myfont.render(rows[1],1,BLACK)           #Time
                        WINDISPLAY.blit(label1,(x2,y))
                        label2 = myfont.render(rows[4], 1, BLACK)       #Position
                        WINDISPLAY.blit(label2, (x3, y))
                        label3 = myfont.render(rows[3], 1, BLACK)       #Department
                        WINDISPLAY.blit(label3, (x4, y))
                if screenMode == 11:
                        myfont =pygame.font.Font('/home/pi/Desktop/Musterpoint_rev2/fonts/arial.ttf',12)
                        label = myfont.render(rows[0], 1, WHITE)        #Employee Name
                        WINDISPLAY.blit(label, (x, y))
                        label1=myfont.render(rows[1],1,WHITE)           #Time
                        WINDISPLAY.blit(label1,(x2,y))
                        label2 = myfont.render(rows[4], 1, WHITE)       #Position
                        WINDISPLAY.blit(label2, (x3, y))
                        label3 = myfont.render(rows[3], 1, WHITE)       #Department
                        WINDISPLAY.blit(label3, (x4, y))
                if screenMode == 11:
                        visitorlist = [rows[0],rows[1],rows[4],rows[3]]
                else:
                        label4 = myfont.render(rows[2], 1, BLACK)       #location
                        WINDISPLAY.blit(label4, (x5, y))
                        visitorlist = [rows[0],rows[1],rows[4],rows[3],rows[2]]    
                        
                list_xy.append(visitorlist)
                y += 19
                count+=1
        if screenMode==11:
                pygame.draw.rect(WINDISPLAY,BLACK,((49,476),(145,15)),0)
                myfont =pygame.font.Font('/home/pi/Desktop/Musterpoint_rev2/fonts/arial.ttf',12)
                labelnum = myfont.render('Total No. of Employee: '+str(count), 1, WHITE)
                WINDISPLAY.blit(labelnum, (49, 476))
                pygame.draw.rect(WINDISPLAY,BLACK,((584,489),(130,10)),0)
                myfont =pygame.font.Font('/home/pi/Desktop/Musterpoint_rev2/fonts/arial.ttf',10)
                labelnum = myfont.render('Preview',1,WHITE)
                WINDISPLAY.blit(labelnum, (584, 489))
                
                
        
        else:
                pygame.draw.rect(WINDISPLAY,WHITE,((49,476),(145,15)),0)
                labelnum=myfont.render('Total No. of Employee:'+str(count),1,BLACK)
                WINDISPLAY.blit(labelnum, (49, 476))
        conn.close()
        
#Function that will display all employees who logged-in (Admin View)                      
def sql_EmpLogs():
        
        global screenMode

        #Text Horizontal Position        
        x = 100
        x2=212
        x3=309
        x4=423
        x5=430
        
        
        #Text Vertical Position
        y = 154
        conn = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        conn.text_factory = str
        c = conn.cursor()

        c.execute("select * from tblemployee2, tbllogs where tblemployee2.employee_id =tbllogs.employee_id")
        
        all_rows = c.fetchall()
        del list_xy[:]
        for rows in all_rows:

                
                myfont = pygame.font.SysFont('Orator Std',15 )
                label = myfont.render(rows[1], 1, BLACK)
                WINDISPLAY.blit(label, (x, y))
                label1=myfont.render(rows[6],1,BLACK)
                WINDISPLAY.blit(label1,(x2,y))
                label2 = myfont.render(rows[3], 1, BLACK)
                WINDISPLAY.blit(label2, (x3, y))
                label3 = myfont.render(rows[2], 1, BLACK)
                WINDISPLAY.blit(label3, (x4, y))
           
                visitorlist = [rows[1],rows[6],rows[3],rows[2]]
                list_xy.append(visitorlist)
                y += 19
             
        
        conn.close()
def del_record():
        global screenMode

        con = sqlite3.connect('/home/pi/Desktop/Musterpoint_rev2/masterpoint.db')
        con.text_factory = str
        cur = con.cursor()

        query = "Delete FROM tbllogs"
        cur.execute(query)
        con.commit()
        con.close()
    
def keypad_pressed(pos):
        global screenMode
        global cardno
        global command
        global employeeno
        global currentloc
        global check1
        global check2   
        global chckbox2
        global chckbox1
        global count
        global screenM
        #MainScreen 
        if screenMode == 10:
               
                #Display Admin Screen if it meets the mouse position according to the condition
                if (pos[1] >= 238 and pos[1] <= 311) and (pos[0] >=208 and pos[0] <= 265):
                        screenMode = 11
                        WINDISPLAY.blit(BGADMIN,((656 - BGADMIN.get_width() ) / 2,(512 - BGADMIN.get_height()) / 2))
                        chckbox2=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOff.png")
                        WINDISPLAY.blit(chckbox2, (193,94))
                        check1=0
                        pygame.draw.rect(WINDISPLAY,GRAY1,((210, 91),(125,22)),0)
                        WINDISPLAY.blit(pygame.font.SysFont('Orator Std',19).render(defaultloc2,1,BLACK),(217,94))
                        chckbox4=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOff.png")
                        WINDISPLAY.blit(chckbox4, (319,94))
                        check2=0
                        pygame.draw.rect(WINDISPLAY,BLACK,((584,489),(130,10)),0)
                        myfont =pygame.font.Font('/home/pi/Desktop/Musterpoint_rev2/fonts/arial.ttf',10)
                        labelnum = myfont.render('Preview',1,WHITE)
                        WINDISPLAY.blit(labelnum, (584, 489))
                #Masterpoint Screen
                elif (pos[1] >= 238 and pos[1] <= 311) and (pos[0] >=392 and pos[0] <=443 ):
                        screenMode = 12
                        WINDISPLAY.blit(BGMASTERPOINT,((656 - BGMASTERPOINT.get_width() ) / 2,(512 - BGMASTERPOINT.get_height()) / 2))
                        sql_viewlogs()
        #AdminScreen
        if screenMode == 11:
                #screenM = False
                pygame.draw.rect(WINDISPLAY,GRAY1,((73, 94),(105,19)),0) 
                WINDISPLAY.blit(pygame.font.SysFont('Orator Std',19).render(defaultloc,1,BLACK),(81,94))
                        
                #If the user click the checkbox for Masterpoint B
                if (pos[0] >=319 and pos[0] <= 334) and (pos[1] >= 95 and pos[1] <= 108):
                        
                         if ( check2==0 ):
                                chckbox1=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
                                WINDISPLAY.blit(chckbox1, (319,94))
                                retrieve_employee("Musterpoint B")
                                check2=1   
                                
                         else:
                                chckbox2=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOff.png")
                                WINDISPLAY.blit(chckbox2, (319,94))
                                WINDISPLAY.blit(BGCLEARLOG,((656 - BGCLEARLOG.get_width() ) / 2,(512 - BGCLEARLOG.get_height()) / 2))
                                check2=0
                                count=""
                                if (check1==1):
                                        retrieve_employee("Musterpoint A")
                                
                #If the user click the checkbox for Masterpoint A
                if (pos[0] >=193 and pos[0] <= 208) and (pos[1] >= 95 and pos[1] <= 108):
                        if (check1==0):
                                chckbox1=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
                                WINDISPLAY.blit(chckbox1, (193,94))
                                retrieve_employee("Musterpoint A")
                                check1=1
                        else:
                                chckbox2=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOff.png")
                                WINDISPLAY.blit(chckbox2, (193,94))
                                WINDISPLAY.blit(BGCLEARLOG,((656 - BGCLEARLOG.get_width() ) / 2,(512 - BGCLEARLOG.get_height()) / 2))
                                check1=0
                                count=""
                                if (check2==1):
                                        retrieve_employee("Musterpoint B")
                if(check1==1 and check2==1):
                        WINDISPLAY.blit(BGCLEARLOG,((656 - BGCLEARLOG.get_width() ) / 2,(512 - BGCLEARLOG.get_height()) / 2))
                        retrieve_employee("""Musterpoint A','Musterpoint B""")

                if (pos[1] >= 475 and pos[1] <= 495) and (pos[0] >=590 and pos[0] <= 606):
                        if (check1==0 and check2==1):
                                        screenMode = 13 
                                        WINDISPLAY.blit(BGPRINTVIEW,((656 - BGPRINTVIEW.get_width() ) / 2,(512 - BGPRINTVIEW.get_height()) / 2))
                                        retrieve_employee("Musterpoint B")
                                
                        elif(check1==1 and check2==0):
                                        screenMode = 13
                                        WINDISPLAY.blit(BGPRINTVIEW,((656 - BGPRINTVIEW.get_width() ) / 2,(512 - BGPRINTVIEW.get_height()) / 2))
                                        retrieve_employee("Musterpoint A")
                        elif(check1==1 and check2==1):
                                        screenMode =13
                                        WINDISPLAY.blit(BGPRINTVIEW,((656-BGPRINTVIEW.get_width() )/2,(512-BGPRINTVIEW.get_height())/2))
                                        retrieve_employee("""Musterpoint A','Musterpoint B""")
                        else:
                                print "Nothing to print"
                        print check1,check2
                                
                if (pos[1] >= 24 and pos[1] <= 62) and (pos[0] >=240 and pos[0] <= 415):
                                mainscreen()
                                
               
                        
                print  check1,check2
        #MasterpointScreen       
        if screenMode == 12:
                global ypos
                if (pos[1] >= 24 and pos[1] <= 62) and (pos[0] >=240 and pos[0] <= 415):
                        ypos = 156
                        mainscreen()
                        
        #PrintViewScreen
        if screenMode == 13:
                #Function Call for Displaying Employees in Print View
                 WINDISPLAY.blit(pygame.font.SysFont('Orator Std',18).render("Logs Report",1,BLACK),(49,103))
                 #updated 10-26-15 -- BEGIN
                 if (pos[1] >= 24 and pos[1] <= 62) and (pos[0] >=240 and pos[0] <= 415):
                        #mainscreen()
                        screenMode = 11
                        WINDISPLAY.blit(BGADMIN,((656 - BGADMIN.get_width() ) / 2,(512 - BGADMIN.get_height()) / 2))
                        pygame.draw.rect(WINDISPLAY,GRAY1,((79, 91),(125,22)),0)
			WINDISPLAY.blit(pygame.font.SysFont('Orator Std',19).render(defaultloc,1,BLACK),(82,94))
			chckbox2=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOff.png")
                        WINDISPLAY.blit(chckbox2, (193,94))
                        pygame.draw.rect(WINDISPLAY,GRAY1,((210, 91),(125,22)),0)
                        WINDISPLAY.blit(pygame.font.SysFont('Orator Std',19).render(defaultloc2,1,BLACK),(217,94))
                        chckbox4=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOff.png")
                        WINDISPLAY.blit(chckbox4, (319,94))
                        print  check1,check2
                        if ( check2==1 ):
                                print check2
                                retrieve_employee("Musterpoint B")
                                chckbox2=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
                                WINDISPLAY.blit(chckbox1, (319,94))
                        elif (check1==1):
                                print check1
                                retrieve_employee("Musterpoint A")
                                chckbox1=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
                                WINDISPLAY.blit(chckbox1, (193,94))
                        elif (check1==0 and check2==1):
                                retrieve_employee("Musterpoint B")
                                chckbox2=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
                                WINDISPLAY.blit(chckbox1, (319,94))
                                
                                
                        elif(check1==1 and check2==0):
                                chckbox1=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
                                WINDISPLAY.blit(chckbox1, (193,94))
                                retrieve_employee("Musterpoint A")
                        elif(check1==1 and check2==1):
                                print "a and b"
                                chckbox1=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
 				WINDISPLAY.blit(chckbox1, (193,94))
                                chckbox2=pygame.image.load("/home/pi/Desktop/Musterpoint_rev2/img/CheckedBoxOn.png")
                                WINDISPLAY.blit(chckbox2, (319,94))
				retrieve_employee("""Musterpoint A','Musterpoint B""")
                                
                                
                        print check1, check2
                #END
        print 'Screen Mode: ',screenMode
        WINDISPLAY.blit(closebtn1, (615,20))
        if(pos[1] >= 5 and pos[1] <= 48) and (pos[0] >=555 and pos[0] <= 645):
                del_record()
                pygame.quit()
                sys.exit()

        pygame.display.update()
        
        
        


while True:
        for event in pygame.event.get():
                if(event.type is MOUSEBUTTONDOWN):
                        pos = pygame.mouse.get_pos()
			print pos[0],pos[1]
			keypad_pressed(pos)
		elif (event.type is KEYUP and event.key is K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                elif(event.type is KEYUP and event.key is (K_LCTRL and K_DELETE)):
                        del_record()
        # Check if a card is available to read.
        uid = pn532.read_passive_target()
        # Try again if no card is available.
        if uid is None:
                continue
        else:
                uiddata =  '0x{0}'.format(binascii.hexlify(uid))
                uiddec = int(uiddata,16)
                print uiddec
                #myfont = pygame.font.Font('fonts/LiquidCrystal-Bold.otf',60)
                #label = myfont.render(str(uiddec), 1, WHITE)
                #WINDISPLAY.blit(label, (15, 70))
                if screenMode == 12:                       
                     check_carduid(str(uiddec))

                else:
                     check_carduid(str(uiddec))    
        
        pygame.display.update()
