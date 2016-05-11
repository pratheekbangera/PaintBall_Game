#!/usr/bin/env python

"""
****** This is the client instance that models the players
****** v1.0
****** 
"""

import thread
import time
import json
from Queue import Queue
from flask import Flask
from flask import jsonify
from flask import request
import flask
import sys
import urllib
import urllib2
import json
import requests
import pprint

app = Flask(__name__)

debugMessage = "[PaintBall][Client]"
inboundQueue = Queue()
outboundQueue = Queue()
#serverUrl = 'http://10.189.130.235:5000/data'
serverUrl = ''
headers = {'Content-Type': 'application/json'}
clientState = {	
				'clientInitialized':False, 			# Client needs to be initialized after it is started by calling /startclient
				'requestsProcessed':0, 				# Keeps track of processed inbound requests
				'responsesProcessed': 0,			# Kepps track of processed outbound responses
				'requestsQueued':0,					# Debugging purpose: current size of size at any time instance
				'gameStarted': False,				# Populated by server - updated to True by server when game starts
				'gameEnded': False,
				'playerRole': '', 					# Populated by server - Paintball game role: ATTACKER, DEFENDER, COVER
				'gridPositionX': 0, 				# x co-ordinate on the grid
				'gridPositionY': 0,					# y co-ordinate on the grid
				'gridMaxX': 0,						# Populated by server - Max x co-ordinate of grid
				'gridMaxY': 0,						# Populated by server - Max y co-ordinate of grid
				'targetGridPositionX': 0,
				'targetGridPositionY': 0,
				'playerLives': 0,					# Populated by server - when lives reach 0, player dies
				'playerLivesTaken': 0,				# No of opposing team players shot
				'isPlayerAlive': True,				# Populated by server - ALIVE or DEAD - DEFAULT is ALIVE. server only updates player when DEAD
				'playerBullets': 0,					# Populated by server - when bullets reach 0, player cannot shoot anymore
				'client_host': '',
				'client_port': 0,
				'client_id': 0,
				'playerState': 'TRACKING'			# TRACKING, SHOOTING, MOVING
				}

@app.route("/")
def greet():
	return flask.render_template('greeting.html', clientURL="http://localhost:"+str(clientState['client_port']))

@app.route("/startclient")
def startclient():
	print debugMessage+"Initializing client"
	if clientState['clientInitialized'] == True:
		response = {
			'type': True,
			'data': 'Client Already Initialized!'
		}
		return jsonify(response)
	elif initialize():
		response = {
			'type': True,
			'data': 'Client Initialized!'
		}
		return jsonify(response)
	else:
		response = {
			'type': False,
			'data': 'Error Initializing Client'
		}
		return jsonify(response)

def initialize():
	try:
		thread.start_new_thread( processInboundRequest,() )
		print debugMessage+"Started processInboundRequest Thread"
		thread.start_new_thread( processOutboundResponse,() )
		print debugMessage+"Started processOutboundResponse Thread"
		clientState['clientInitialized'] = True
		#Inform the sever that I am up and running
		response = { 'ACTION' : "clientInitialized", 'client_id': clientState['client_id'], 'client_host': clientState['client_host'], 'client_port': clientState['client_port']}
		outboundQueue.put(response)
		return True
	except:
		print debugMessage+"Unable to start processInboundRequest Threads. Error:", sys.exc_info()[0]
		return False

@app.route("/enqueueRequest", methods=["GET", "POST"])
def enqueueRequest():
	if not clientState['clientInitialized']:
		response = {
			'type': False,
			'data': 'Client is not ready: Not Initialized'
		}
		return jsonify(response)
	print debugMessage+"Queueing a request"
	try:
		inboundQueue.put(request.json)
		clientState['requestsQueued'] = clientState['requestsQueued'] + 1
		response = {
			'type': True,
			'data': 'Request Enqueued'
		}
		return jsonify(response)
	except:
		print debugMessage+"Queueing Failed", sys.exc_info()[0]
		response = {
			'type': False,
			'data': 'Request could not be queued'
		}
		return jsonify(response)

def processInboundRequest():
	while True:
		try:		
			request = inboundQueue.get(True)
			print debugMessage+"Received request: %s" %request
			if not clientState['clientInitialized']:
				print debugMessage+"Client not yet initialized. Ignoring inbound message."
			else:
				if request['ACTION'] == "InitializeGame":
					clientState['playerLives'] = request['playerLives']
					clientState['playerBullets'] = request['playerBullets']
					clientState['playerRole'] = request['playerRole']
					clientState['gridMaxX'] = request['gridMaxX']
					clientState['gridMaxY'] = request['gridMaxY']
					clientState['gridPositionX'] = request['gridPositionX']
					clientState['gridPositionY'] = request['gridPositionY']
					clientState['gameStarted'] = True
					thread.start_new_thread( startPlaying,() )
				elif request['ACTION'] == "PLAYER_TRACKING_SUCCESSFUL":
					#If there is a player in range, try to kill him
					print debugMessage+"Found a target to shoot at [%s,%s]" %(request['gridPositionX'], request['gridPositionY'])
					#Some logic to calculate the target grid position - based on what co-ordinates are provided by the server
					clientState['targetGridPositionX'] = request['gridPositionX'] #This will potentially change
					clientState['targetGridPositionY'] = request['gridPositionY'] #This will potentially change
					clientState['playerState'] = 'SHOOTING'
                                        print "%s"%clientState['playerState']
				elif request['ACTION'] == "PLAYER_TRACKING_FAILURE":	
					#If there is no player in range, move forward
					print debugMessage+"No targets in range."
					clientState['playerState'] = 'MOVING'
				elif request['ACTION'] == "PLAYER_SHOOTING_SUCCESSFUL" or request['ACTION'] == "PLAYER_SHOOTING_FAILURE":
					#If successful check if there is anyone else to shoot
					if request['ACTION'] == "PLAYER_SHOOTING_SUCCESSFUL":
						clientState['playerLivesTaken'] = clientState['playerLivesTaken'] + 1
						print debugMessage+"Shot a player! So far shot %d players!" %(clientState['playerLivesTaken'])
					clientState['playerState'] = 'MOVING'
                                        print "%s"%clientState['playerState']
				elif request['ACTION'] == "PLAYER_MOVING_SUCCESSFUL":
					print debugMessage+"Moved to location [%s,%s]" %(request['gridPositionX'],request['gridPositionY'])
					clientState['gridPositionX'] = request['gridPositionX']
					clientState['gridPositionY'] = request['gridPositionY']
					clientState['playerState'] = 'TRACKING'
				elif request['ACTION'] == "PLAYER_MOVING_FAILURE":
					#You will generally not come into this state
					print debugMessage+"Failed to move to location [%s,%s]" %(request['gridPositionX'],request['gridPositionY'])
					clientState['playerState'] = 'TRACKING'
				elif request['ACTION'] == "YOU_WERE_SHOT":
					print debugMessage+"OMG! I was shot!"
					clientState['playerLives'] = int(clientState['playerLives']) - 1
					#clientState['gridPositionX'] = request['gridPositionX']
					#clientState['gridPositionY'] = request['gridPositionY']
					clientState['playerState'] = 'TRACKING'
					if clientState['playerLives'] <= 0:
						print debugMessage+"This is the end! =_= Goodbye. I'm dead!"
						clientState['isPlayerAlive'] = False
				elif request['ACTION'] == "GAME_OVER_YOU_WON":
					print debugMessage+"We won! We won! Yaaaayyyyyy!"
					clientState['gameEnded'] = True
					break;
				elif request['ACTION'] == "GAME_OVER_YOU_LOST":
					print debugMessage+"We lost the game....... shucks"
					clientState['gameEnded'] = True
					break;
				else:
					print "Invalid action!"
				clientState['requestsProcessed'] = clientState['requestsProcessed'] + 1
				print debugMessage+"Request Processed"
		except:
			print debugMessage+"Could not process inbound request. Error:", sys.exc_info()[0]
	print debugMessage+"Ended processInboundRequest Thread"

def processOutboundResponse():
	while True:
		try:
			response = outboundQueue.get(True)
			print debugMessage+"Sending response: %s" %response
			if not clientState['clientInitialized']:
				print debugMessage+"Client not yet initialized. Ignoring outbound message."
			else:
				# Code to send the response to the server
				data = {'type': True, 'data': response }
				r = requests.post(serverUrl, data=json.dumps(data), headers=headers)
				print debugMessage+"Response Sent"
				clientState['responsesProcessed'] = clientState['responsesProcessed'] + 1
		except:
			print debugMessage+"Could not process outbound request. Error:", sys.exc_info()[0]			

@app.route("/getClientState", methods=['GET'])
def getClientState():
	print debugMessage+"Returning client state"
	return jsonify(clientState)

def startPlaying():
	print debugMessage+"I have started playing!"
	while True:
		if clientState['gameStarted'] and clientState['isPlayerAlive'] and not clientState['gameEnded']:
                        print "I am still playing"
			if   clientState['playerState'] == 'TRACKING':
                                print "I Am tracking"
				response = { 'ACTION' : "PLAYER_TRACKING", 
							 'gridPositionX' : clientState['gridPositionX'], 'gridPositionY': clientState['gridPositionY'],
							 'client_id': clientState['client_id'], 'client_host': clientState['client_host'], 'client_port': clientState['client_port']
						   }
				outboundQueue.put(response)
			elif clientState['playerState'] == 'SHOOTING':
                                print "Inside the action for shooting"
				response = { 'ACTION' : "PLAYER_SHOOTING", 
							 'gridPositionX' : clientState['targetGridPositionX'], 'gridPositionY': clientState['targetGridPositionY'],
							 'client_id': clientState['client_id'], 'client_host': clientState['client_host'], 'client_port': clientState['client_port']
						   }
                                #print "%s"%response
				outboundQueue.put(response)
				clientState['playerBullets'] = int(clientState['playerBullets']) - 1
			elif clientState['playerState'] == 'MOVING':
				# Generate the location where we want to move
                                print "Leap aheaad"
				response = { 'ACTION' : "PLAYER_MOVING", 
							 'gridPositionX' : str(int(clientState['gridPositionX']) + 50), 'gridPositionY': str(int(clientState['gridPositionY']) + 50),
							 'client_id': clientState['client_id'], 'client_host': clientState['client_host'], 'client_port': clientState['client_port']
						   }
                                print "%s" %response
                                clientState['playerState'] = 'TRACKING'
				outboundQueue.put(response)
			else:
                                print "ambu %s"%clientState['playerState']
				print debugMessage+'Invalid player state! :O :O :O  - Something went horibbly wrong!'	
			time.sleep(8)
		elif not clientState['isPlayerAlive']:
			print debugMessage+"Player is dead :( "
			break
		elif clientState['gameEnded']:
			print debugMessage+"The game has ended!"
			break
		else:
			time.sleep(8)
	print debugMessage+"Ended processOutboundResponse Thread"

# Starting the web server
if(__name__ == "__main__"):
	try:
		if len(sys.argv) < 5:
			print debugMessage+"Syntax: python PaintBall_client.py [client_host] [client_port] [server_url - http://xx.xx.xx.xx:port/yyy] [client_id]"
		else:
			print debugMessage+"Starting the web server"
			serverUrl = str(sys.argv[3])
			clientState['client_host'] = str(sys.argv[1])
			clientState['client_port'] = int(sys.argv[2])
			clientState['client_id'] = int(sys.argv[4])
			app.run(host='0.0.0.0',port=int(sys.argv[2]))
	except:
		print debugMessage+"There was an error starting the client:", sys.exc_info()[0]
