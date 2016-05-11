#!/usr/bin/python

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import thread
import time
import simpy
import random
import json
import requests
import urllib
import urllib2
import math
import sys
from flask import Flask, request, jsonify
app = Flask(__name__) 

step = 0
step1 = 0

width, height = 400, 600			       # window size
rect1_x=50
rect1_y=10
rect2_x=150
rect2_y=10
rect3_x=250
rect3_y=10
rect4_x=350
rect4_y=10
rect1_a=0
rect1_b=height-40
rect2_a=100
rect2_b=height-40
rect3_a=200
rect3_b=height-40
rect4_a=300
rect4_b=height-40

flag_a =width/2
flag_b =height/2

rect_width=10
rect_length=30

window = 0                                             # glut window number

playerPosition = [ 
		{  
		'X': rect1_x,
		'Y': rect1_y

		},
		{  
		'X': rect2_x,
		'Y': rect2_y
		},
		{  
		'X': rect3_x,
		'Y': rect3_y
		},
		
		{  
		'X': rect1_a,
		'Y': rect1_b

		},
		{  
		'X': rect2_a,
		'Y': rect2_b
		},
		{  
		'X': rect3_a,
		'Y': rect3_b
		}

		]


playerData = 	[ 
		{  
		'ACTION' : 'InitializeGame',
		'playerLives' : '3',
		'playerBullets' : '100',
		'playerRole' : 'Attacker',
		'gridMaxX' : '100',
		'gridMaxY' : '100',
		'gridPositionX' : '10',
		'gridPositionY' : '0',
                'team' : 'a',
                'url' : ''

		},
		{  
		'ACTION' : 'InitializeGame',
		'playerLives' : '3',
		'playerBullets' : '100',
		'playerRole' : 'Supporter',
		'gridMaxX' : '100',
		'gridMaxY' : '100',
		'gridPositionX' : '30',
		'gridPositionY' : '0',
                'team' : 'a',
		'url' : ''

		},
		{  
		'ACTION' : 'InitializeGame',
		'playerLives' : '3',
		'playerBullets' : '100',
		'playerRole' : 'Defender',
		'gridMaxX' : '100',
		'gridMaxY' : '100',
		'gridPositionX' : '20',
		'gridPositionY' : '0',
                'team' : 'a',
		'url' : ''
		},
		{  
		'ACTION' : 'InitializeGame',
		'playerLives' : '3',
		'playerBullets' : '100',
		'playerRole' : 'Attacker',
		'gridMaxX' : '100',
		'gridMaxY' : '100',
		'gridPositionX' : '20',
		'gridPositionY' : '0',
                'team' : 'b',
		'url' : ''
		},
		{  
		'ACTION' : 'InitializeGame',
		'playerLives' : '3',
		'playerBullets' : '100',
		'playerRole' : 'Supporter',
		'gridMaxX' : '100',
		'gridMaxY' : '100',
		'gridPositionX' : '20',
		'gridPositionY' : '0',
                'team' : 'b',
		'url' : ''
		},
		{  
		'ACTION' : 'InitializeGame',
		'playerLives' : '3',
		'playerBullets' : '100',
		'playerRole' : 'Defender',
		'gridMaxX' : '100',
		'gridMaxY' : '100',
		'gridPositionX' : '20',
		'gridPositionY' : '0',
                'team' : 'b',
		'url' : ''
		}

		]

playerCount = 0


# Define a function for the thread
def print_time( threadName, delay):
   count = 0
   while True:
      time.sleep(delay)
      count += 1
      print "%s: %s" % ( threadName, time.ctime(time.time()) )

def draw():                                            # ondraw is called all the time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
    glLoadIdentity()                                   # reset position
    refresh2d(width, height)                           # set mode to 2d
    
    
    glColor3f(1.0, 0.0, 0.0)
    glClearColor(1.0, 1.0, 1.0,0.0)
    glBegin(GL_QUADS)
    glVertex3f( 0,-0.001, 0)
    glVertex3f( 0,-0.001,10)
    glVertex3f(10,-0.001,10)
    glVertex3f(10,-0.001, 0)
    glEnd()
   
    glColor3f(0.0, 0.0, 0.0)
    draw_grid()

    glColor3f(0.3, 0.3, 0.3)                           # set color to blue
    draw_rect(rect1_x,rect1_y, rect_width, rect_length)
    draw_rect(rect2_x,rect2_y, rect_width, rect_length)
    draw_rect(rect3_x,rect3_y, rect_width, rect_length)
 
    glColor3f(0.6, 0.6, 0.3)
    draw_rect(rect1_a,rect1_b, rect_width, rect_length)
    draw_rect(rect2_a,rect2_b, rect_width, rect_length)
    draw_rect(rect3_a,rect3_b, rect_width, rect_length)

    glColor3f(0.0, 0.0, 1.0)                            #Draw referee
    draw_rect(rect4_x,rect4_y, rect_width, rect_length)
    draw_rect(rect4_a,rect4_b, rect_width, rect_length)

    glColor3f(0.95, 0.0, 0.0)
    draw_flag(flag_a,flag_b) 
    time.sleep(1)                                      # thread sleep for a second                         
    update_var()
    
    glutSwapBuffers()  

def refresh2d(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, 0.0, height, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()
  
def draw_rect(x, y, width, height):
    glBegin(GL_QUADS)                                  # start drawing a rectangle
    glVertex2f(x, y)                                   # bottom left point
    glVertex2f(x + width, y)                           # bottom right point
    glVertex2f(x + width, y + height)                  # top right point
    glVertex2f(x, y + height)			       # top left point                
    glEnd()                                            # done drawing a rectangle

def draw_flag(x,y):
    glBegin(GL_QUADS)                                 
    glVertex2f(x, y)                                  
    glVertex2f(x, y+15)                           
    glVertex2f(x + 10, y + 15)                  
    glVertex2f(x + 10, y )
    glEnd()
    
    glBegin(GL_QUADS)
    glVertex2f(x , y + 15)
    glVertex2f(x , y + 30)
    glVertex2f(x + 30, y + 30)
    glVertex2f(x + 30, y+15)  			                   
    glEnd()                                            # done drawing a flag

def draw_grid():
    glLineWidth(1)

    glBegin(GL_LINES)
    glVertex2f(0,0)
    glVertex2f(0, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(50,0)
    glVertex2f(50, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(100,0)
    glVertex2f(100, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(150,0)
    glVertex2f(150, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(200,0)
    glVertex2f(200, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(250,0)
    glVertex2f(250, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(300,0)
    glVertex2f(300, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(350,0)
    glVertex2f(350, height)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(400,0)
    glVertex2f(400, height)
    glEnd()


    glBegin(GL_LINES)
    glVertex2f(0,0)
    glVertex2f(width, 0)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,50)
    glVertex2f(width, 50)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,100)
    glVertex2f(width, 100)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,150)
    glVertex2f(width, 150)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,200)
    glVertex2f(width, 200)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,250)
    glVertex2f(width, 250)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,300)
    glVertex2f(width, 300)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,350)
    glVertex2f(width, 350)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,400)
    glVertex2f(width, 400)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,450)
    glVertex2f(width, 450)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,500)
    glVertex2f(width, 500)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,550)
    glVertex2f(width, 550)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,600)
    glVertex2f(width, 600)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,650)
    glVertex2f(width, 650)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,700)
    glVertex2f(width, 700)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,750)
    glVertex2f(width, 750)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,800)
    glVertex2f(width, 800)
    glEnd()
           
def update_var():
    global rect1_y, rect2_y, rect3_y, rect4_y          # importing the global variables
    global rect1_b, rect2_b, rect3_b, rect4_b
    global step1,step2,step3,step4
    #step1 = random.randint(10, 15)
    step2 = random.randint(5, 8)
    step3 = random.randint(3, 5)
    step4 = random.randint(10, 15)

    if rect1_y < (height/2):                                  # Updating the value of the variables to proceed ahead
       rect1_y=playerPosition[0]['Y'] 
       step1=0
    else:
       declare_winner('a')
    if rect2_y< (height/2):
       rect2_y=playerPosition[1]['Y'] 
    else:
       declare_winner('a')
    if rect3_y < (height/2):                                  
       rect3_y=playerPosition[2]['Y'] 
    else:
       declare_winner('a')
    if rect4_y< (height-50):
       rect4_y=rect4_y+10
    else:
       rect4_y=10

    if rect1_b > (height/2):                                  # Updating the value of the variables to proceed below
       #rect1_b=rect1_b-5
       rect1_b=playerPosition[3]['Y'] 
       #playerPosition[3]['Y'] = rect1_b
    else:
       declare_winner('b')
    if rect2_b > (height/2):
       #rect2_b=rect2_b-6
       #playerPosition[4]['Y'] = rect2_b
       rect2_b=playerPosition[4]['Y']
    else:
       declare_winner('b')
    if rect3_b > (height/2):                                  
       #rect3_b=rect3_b-8
       #playerPosition[5]['Y'] = rect3_b
       rect3_b=playerPosition[5]['Y']
    else:
       declare_winner('b')
    if rect4_b > 50:
       rect4_b=rect4_b-10
    else:
       rect4_b=height-40
   
     

def init_opengl():
    # initialization of the opengl code
    print "Inside initilization block"
   
    glutInit()                                             # initialize glut
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)                      # set window size
    glutInitWindowPosition(0, 0)                           # set window position
    window = glutCreateWindow("Paint ball in action")      # create window with title
    glutDisplayFunc(draw)                                  # set draw function callback
    glutIdleFunc(draw)                                     # draw all the time
    glutMainLoop()                                         # start everything


def player(env):

     
     print('am here')
     while True:
	 global step
	 step = random.randint(1, 5)
         print('Moved %d steps at %d' % (step,env.now))
       	 move_duration = 5
         time.sleep(1)      
         yield env.timeout(move_duration)
	 
	 print('Staying under cover %d' % (env.now))
       	 cover_duration = 10
         time.sleep(1) 
         yield env.timeout(cover_duration)
        

def declare_winner(win_team):
	if(win_team=='a'):
		for x in range(0, 3):
    			print "%s"%playerData[x]['url']
			url1=playerData[x]['url']
                        coordinates = {  
				'ACTION': 'GAME_OVER_YOU_WON'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)
		
		for y in range(3, 6):
    			print "%s"%playerData[y]['url']
			url1=playerData[y]['url']
                        coordinates = {  
				'ACTION': 'GAME_OVER_YOU_LOST'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)
		
	else:
		for x in range(3, 6):
    			print "%s"%playerData[x]['url']
			url1=playerData[x]['url']
                        coordinates = {  
				'ACTION': 'GAME_OVER_YOU_WON'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)
		
		for y in range(0, 3):
    			print "%s"%playerData[y]['url']
			url1=playerData[y]['url']
                        coordinates = {  
				'ACTION': 'GAME_OVER_YOU_LOST'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)

	sys.exit()
		
# setting up the web server
@app.route("/")
def hello():
    return "Hello World!"

@app.route("/hi")
def hi():
    return "Hello Ambur!"



def distance(x1,y1,x2,y2):
	result = math.sqrt(((x2-x1)**2)+ ((y2-y1)**2))
        
	return result




@app.route('/data', methods=['POST'])
def get_data():
     
     jsonData=request.json
     print "Json: %s"%jsonData
     action = jsonData['data']['ACTION']
     port =   jsonData['data']['client_port']
     host =   jsonData['data']['client_host']
     playerNumber = jsonData['data']['client_id']
     
     if action == 'PLAYER_TRACKING':
	if playerNumber<3:
	  player3Y = playerPosition[3]['Y']
          player4Y = playerPosition[4]['Y']
          player5Y = playerPosition[5]['Y']
          
           
          #print "%s , %s" %(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'])
          #print "%s , %s" %(playerPosition[3]['X'],playerPosition[3]['Y'])
          
          dist3 = distance(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'],playerPosition[3]['X'],playerPosition[3]['Y'])
          dist4 = distance(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'],playerPosition[4]['X'],playerPosition[4]['Y'])
          dist5 = distance(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'],playerPosition[5]['X'],playerPosition[5]['Y'])	  

          Min = dist3
          closestPlayer = 3
          if dist4< Min:
		Min = dist4
                closestPlayer = 4
          if dist5 < Min:
		Min = dist5
		closestPlayer = 5
          if Min > 400:
		flag=False
          elif Min<400:
		flag=True
	 
	else:
	  print "Team 2"	  
	  player0Y = playerPosition[0]['Y']
          player1Y = playerPosition[1]['Y']
          player2Y = playerPosition[2]['Y']
          
           
          #print "%s , %s" %(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'])
          #print "%s , %s" %(playerPosition[3]['X'],playerPosition[3]['Y'])
      
          dist0 = distance(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'],playerPosition[0]['X'],playerPosition[0]['Y'])
          dist1 = distance(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'],playerPosition[1]['X'],playerPosition[1]['Y'])
          dist2 = distance(playerPosition[playerNumber]['X'],playerPosition[playerNumber]['Y'],playerPosition[2]['X'],playerPosition[2]['Y'])

	 
          Min = dist0
          closestPlayer = 0
          if dist1< Min:
		Min = dist1
                closestPlayer = 1
          if dist2 < Min:
		Min = dist2
		closestPlayer = 2
	  if Min > 400:
		flag=False
          elif Min<400:
		flag=True


	if(flag):
		print closestPlayer
		print "%s , %s" %(playerPosition[closestPlayer]['X'],playerPosition[closestPlayer]['Y'])
		coordinates = {  
				'gridPositionX': playerPosition[closestPlayer]['X'],
				'gridPositionY': playerPosition[closestPlayer]['Y'],
		                'ACTION': 'PLAYER_TRACKING_SUCCESSFUL'
			      }
		data_json = json.dumps(coordinates)
		headers = {'Content-type': 'application/json'}

		url = 'http://'+host+':'+str(port)+'/enqueueRequest'
		print "%s" %url
		response = requests.post(url, data=data_json, headers=headers)
	else:
		print "Cant track !! out of range"
	        coordinates = {  
		                'ACTION': 'PLAYER_TRACKING_FAILURE'
			      }
		data_json = json.dumps(coordinates)
		headers = {'Content-type': 'application/json'}

		url = 'http://'+host+':'+str(port)+'/enqueueRequest'
		print "%s" %url
		response = requests.post(url, data=data_json, headers=headers)

     elif action == 'PLAYER_SHOOTING':
       jsonData=request.json
       print "Json: %s"%jsonData
       
       X = jsonData['data']['gridPositionX']
       Y = jsonData['data']['gridPositionY']
       print X
       print Y
       if playerNumber<3:
		print "%s,%s"%(playerPosition[3]['X'],playerPosition[3]['Y'])
		print "%s,%s"%(playerPosition[4]['X'],playerPosition[4]['Y'])
		print "%s,%s"%(playerPosition[5]['X'],playerPosition[5]['Y'])
	

	        global rect1_a,rect1_b,rect2_a,rect2_b,rect3_a,rect3_b
                shot=False
		if X == playerPosition[3]['X']: #&& Y == playerPosition[3]['Y']
			print "Player 3 shot!"
			shot = True
                        #rect1_a=0
			#rect1_b=height-40
			playerPosition[3]['X'] = 0
			playerPosition[3]['Y'] = height-40
			url1=playerData[3]['url']
                        coordinates = {  
				'ACTION': 'YOU_WERE_SHOT'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)

		elif X == playerPosition[4]['X']: #&& Y == playerPosition[4]['Y']
			print "Player 4 shot!"
			shot = True
			#rect2_a=100
			#rect2_b=height-40
			playerPosition[4]['X'] = 100
			playerPosition[4]['Y'] = height-40
			url1=playerData[4]['url']
                        coordinates = {  
				'ACTION': 'YOU_WERE_SHOT'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)

		elif X == playerPosition[5]['X']: #&& Y == playerPosition[5]['Y']
			print "Player 5 shot!"
			shot = True
			#rect3_a=200
			#rect3_b=height-40

			playerPosition[5]['X'] = 200
			playerPosition[5]['Y'] = height-40
			url1=playerData[5]['url']
                        coordinates = {  
				'ACTION': 'YOU_WERE_SHOT'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)


       else:
		global rect1_x,rect1_y,rect2_x,rect2_y,rect3_x,rect3_y
                shot=False
		if X == playerPosition[0]['X']: #&& Y == playerPosition[0]['Y']
			print "Player 0 shot!"
			shot = True
                       
			playerPosition[0]['X'] = 50
			playerPosition[0]['Y'] = 10
			url1=playerData[0]['url']
                        coordinates = {  
				'ACTION': 'YOU_WERE_SHOT'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)

		elif X == playerPosition[1]['X']: #&& Y == playerPosition[1]['Y']
			print "Player 1 shot!"
			shot = True
			
			playerPosition[1]['X'] = 150
			playerPosition[1]['Y'] = 10
			url1=playerData[1]['url']
                        coordinates = {  
				'ACTION': 'YOU_WERE_SHOT'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)

		elif X == playerPosition[2]['X']: #&& Y == playerPosition[2]['Y']
			print "Player 2 shot!"
			shot = True
			playerPosition[2]['X'] = 250
			playerPosition[2]['Y'] = 10
			url1=playerData[2]['url']
                        coordinates = {  
				'ACTION': 'YOU_WERE_SHOT'
			      }
			data_json = json.dumps(coordinates)
			headers = {'Content-type': 'application/json'}

			print "%s" %url1
			response = requests.post(url1, data=data_json, headers=headers)





       if shot==True:
		shootingStatus = {  
				   'ACTION': 'PLAYER_SHOOTING_SUCCESSFUL'
				 }
       else:
		shootingStatus = {  
				   'ACTION': 'PLAYER_SHOOTING_FAILURE'
				 }
       data_json = json.dumps(shootingStatus)
       headers = {'Content-type': 'application/json'}

       url = 'http://'+host+':'+str(port)+'/enqueueRequest'
       print "%s" %url
       response = requests.post(url, data=data_json, headers=headers)






     elif action == 'PLAYER_MOVING':
	global step1,rect1_y
	jsonData=request.json
	print "Json: %s"%jsonData
	"""action = jsonData['data']['ACTION']
	port =   jsonData['data']['client_port']
	host =   jsonData['data']['client_host']"""
	
        #step1 = 10
	#rect1_y=rect1_y+10	
        playerPosition[playerNumber]['X'] = playerPosition[playerNumber]['X']
        if(playerNumber<3):
        	playerPosition[playerNumber]['Y'] = playerPosition[playerNumber]['Y']+30
        else:
		playerPosition[playerNumber]['Y'] = playerPosition[playerNumber]['Y']-30
	print 'Moved one position'
	#return request.data
     else:	   
	     #data = {'X' : '35', 'Y':'45','ACTION':'move'}
	     global playerCount
	     print("Initalizing player")
	     if playerCount < 6:
		     print "%s"%playerData[playerNumber]
		     temp=playerData[playerNumber]
		     data_json = json.dumps(temp)
		     #data_json = json.dumps(data)
		     playerCount=playerCount+1

		     headers = {'Content-type': 'application/json'}
		    
		     url = 'http://'+host+':'+str(port)+'/enqueueRequest'
		     print "%s" %url
		     playerData[playerNumber]['url']=url
		     response = requests.post(url, data=data_json, headers=headers)
	     else:
		     print "Player count exceeded"	
     return request.data





"""
@app.route('/move', methods=['POST'])
def move():
      global step1,rect1_y
      jsonData=request.json
      print "Json: %s"%jsonData
     
      #step1 = 10
      rect1_y=rect1_y+10
      print 'Moved one position'
      return request.data
"""



@app.route("/init")
def init():
    
    try:
     env = simpy.Environment()
     env.process(player(env))
     thread.start_new_thread( init_opengl,() )
     #thread.start_new_thread( env.run(until=10),() )
     #thread.start_new_thread( print_time,("thread1",2,) )
     return "A thread is started !!"
    except:
     print "Error: unable to start thread" 
    
    
    

if __name__ == "__main__":
    try:
     app.run(
         host="0.0.0.0",
         port=int("5000")
        )
    except:
     print "Error: unable to start app thread"
