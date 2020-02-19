import sys, pygame, datetime
import numpy, random
pygame.init()

pygame.mouse.set_visible(False)
pygame.key.set_repeat(1000,1000)


## Distance between Greenwich piers is 650m. This is 200 pixels in our map, so 3.25m = 1 pixel
pixeltodistance = 3.25
speedofsound = 343
## Speed of sound = 343 m/s, so 105 pixels per second
speed = 105 # shockwave speed in pixels per second
mapconversion = 0.01  ## Meters of world to cm of map. Update once we see the maps!


clock = pygame.time.Clock()

showFPS = False

size = width, height = 1366,768

## Define Colours
black = 0,0,0
background = 0,0,0

screen = pygame.display.set_mode((width,height), pygame.FULLSCREEN | pygame.HWSURFACE| pygame.DOUBLEBUF | pygame.RESIZABLE)
#screen = pygame.display.set_mode((width,height),pygame.SCALED)
gameCaption = pygame.display.set_caption("Asteroid Tracking")

Font = pygame.font.Font("C:\\Windows\\Fonts\\Verdana.ttf", 20)


screen.fill(background)
map = pygame.image.load("SmallMap.png")
maprect = map.get_rect()

### Asteroid list
asteroids = [(252,328), (29,283), (376,251), (111,381), (413,474)] 


def drawMap():
	screen.blit(map,maprect)
	for tower in game.stations:
		tower.draw()

def drawFPS():
	FPS = int(clock.get_fps())				
	screen.blit(Font.render("FPS: " + str(FPS), True, black), (0, 0))	

def drawConsole():
	pygame.draw.rect(screen, background, (maprect.right, 0, width-maprect.width, height))
	for tower in game.stations:
		tower.drawtext()
		tower.draw()
	for text in game.ISStexts:
		text.drawtext()
	for deltainfo in game.deltas:
		deltainfo.drawtext()

class game(object):
	def __init__(self):
		self.impacts = []
		self.stations = []
		self.ISStexts = []
		self.ISSuplink = True
		self.asteroidcount = 0
		self.deltas = []
		
	def reset(self):
		self.impacts = []
		self.stations = []
		self.ISStexts = []
		self.ISSuplink = True
		self.asteroidcount = 0
		self.deltas = []
		
	
		## Create stations
		station(int(maprect.width/2), 20 , "red", (255,0,0), (255,255,0), maprect.width + 20, 150, "Red Tower: Listening")
		station(20, maprect.height-20 , "green", (0,255,0), (0,255,255), maprect.width + 20, 250, "Green Tower: Listening")
		station(maprect.width-20, maprect.height-20 , "blue", (0,0,255), (255,0,255), maprect.width + 20, 350, "Blue Tower: Listening")

		## Create text
		ISStext(maprect.width + 40, 20, "ISS: uplink established...")
		ISStext(maprect.width + 40, 40, "")
		ISStext(maprect.width + 40, height - 200, "Total asteroids: {0}".format(self.asteroidcount))
		ISStext(maprect.width + 20, height - 40, "Mapping data copyright OpenStreetMap.org")
		
		## Create deltas
		delta(maprect.width + 300, 230, (128,0,0) )
		delta(maprect.width + 300, 330, (0,128,0) )
		

		## Draw
		drawMap()
		pygame.display.flip()


	def ISSloseuplink(self):
		self.ISSuplink = False
		self.ISStexts[0].text = "ISS: uplink LOST"
		self.ISStexts[1].text = ""
	
	def ISSgetuplink(self):
		self.ISSuplink = True
		self.ISStexts[0].text = "ISS: uplink established..."
		
class ISStext(object):
	def __init__(self,x,y,text):
		self.x = x
		self.y = y
		self.text = text
		self.colour = (28,118,48)
		game.ISStexts.append(self)
	
	def drawtext(self):
		screen.blit(Font.render(self.text, True, self.colour), (self.x, self.y))
	
class impact(object):
	def __init__(self,coordinates,visible):
		self.x = coordinates[0]
		self.y = coordinates[1]
		self.visible = visible
		self.creationtime = pygame.time.get_ticks()
		self.timetotower = []
		for tower in game.stations:
			distance = numpy.sqrt((self.x - tower.x)**2 + (self.y - tower.y)**2)
			self.timetotower.append(distance/speed)
		print(self.timetotower)
		self.detected = numpy.repeat(False, len(game.stations))
		self.radius = 2
		game.impacts.append(self)
		if self.visible:
			actualtime = datetime.datetime.now().strftime("%H:%M:%S.") + datetime.datetime.now().strftime("%f")[:2]
			game.ISStexts[1].text = "Impact at {0}".format(actualtime) 
		game.asteroidcount += 1
		game.ISStexts[2].text = "Total asteroids: {0}".format(game.asteroidcount)
	
	def draw(self):
		if self.visible:
			pygame.draw.circle(screen, (255,0,0), (self.x,self.y), 4,0)
			if self.radius >= 2:
				pygame.draw.circle(screen, (128,128,255), (self.x,self.y), self.radius, 2)
			if self.radius > 11:
				pygame.draw.circle(screen, (128,128,255), (self.x,self.y), self.radius-10, 2)
			if self.radius > 22:
				pygame.draw.circle(screen, (128,128,255), (self.x,self.y), self.radius-20, 2)

class station(object):
	def __init__(self,x,y,name,colour,flashcolour,textx,texty,text):
		self.x = x
		self.y = y
		self.textx = textx
		self.texty = texty
		self.textline1 = text
		self.textline2 = ""
		self.textline3 = ""
		self.textline4 = ""
		self.state = "Listening"
		self.lasttriggered = pygame.time.get_ticks()
		self.defaultcolour = colour
		self.flashcolour = flashcolour
		self.colour = colour
		self.radius = 10
		self.detectedtime = 0
		game.stations.append(self)
	
	def draw(self):
		pygame.draw.circle(screen, self.colour, (self.x,self.y), self.radius)
		if self.state == "Triggered":
			pygame.draw.aaline(screen, self.colour, (self.x,self.y), (self.textx-10, self.texty+50))

	def trigger(self):
		self.colour = self.flashcolour
		self.lasttriggered = pygame.time.get_ticks()
		self.state = "Triggered"
	
	def reset(self):
		self.colour = self.defaultcolour
		self.state = "Listening"
		self.radius = 10
		
	def drawtext(self):
		screen.blit(Font.render(self.textline1, True, self.colour), (self.textx, self.texty))
		screen.blit(Font.render(self.textline2, True, self.colour), (self.textx+10, self.texty+20))
		screen.blit(Font.render(self.textline3, True, self.colour), (self.textx+10, self.texty+40))
		screen.blit(Font.render(self.textline4, True, self.colour), (self.textx+10, self.texty+60))

class delta(object):
	def __init__(self, textx, texty, colour):
		self.textx = textx
		self.texty = texty
		self.textline1 = ""
		self.textline2 = ""
		self.textline3 = ""
		self.colour = colour
		game.deltas.append(self)

	def drawtext(self):
		screen.blit(Font.render(self.textline1, True, self.colour), (self.textx, self.texty))
		screen.blit(Font.render(self.textline2, True, self.colour), (self.textx+10, self.texty+20))
		screen.blit(Font.render(self.textline3, True, self.colour), (self.textx+10, self.texty+40))
	

game = game()
game.reset()

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q: sys.exit()
			if event.key == pygame.K_SPACE:
				impact(asteroids[game.asteroidcount], game.ISSuplink) ## we can see the impact if the ISS uplink is established.
				#actualtime = datetime.datetime.now().strftime("%H:%M:%S.") + datetime.datetime.now().strftime("%f")[:2]
				#game.ISStexts[1].text = "Impact at {0}".format(actualtime)
			if event.key == pygame.K_r:
				#del game ## ToDo: Fix removal.
				#print("Game deleted")
				#game = game()
				game.reset()
				#impact((random.randint(1,maprect.width), random.randint(1,maprect.height)), game.ISSuplink)
			#if event.key == pygame.K_i: # toggle ISS for debugging
			#	if game.ISSuplink == True:
			#		game.ISSloseuplink()
			#	else:
			#		game.ISSgetuplink()
	clock.tick(30)
	drawMap()
	if showFPS == True:
		drawFPS()
	
	if game.asteroidcount == 4 and game.ISSuplink and all(game.impacts[3].detected): ## 4 previous impacts, still have uplink and all stations have detected it
		game.ISSloseuplink()
	
	## Update stations
	for tower in game.stations:
		elapsedtime = pygame.time.get_ticks() - tower.lasttriggered
		if tower.state == "Triggered":
			tower.radius = int((1-elapsedtime/2000)*10 + 10)
			tower.linealpha = (1-elapsedtime/2000)
		if elapsedtime/1000 > 2 and tower.state == "Triggered":
			tower.reset()
	
	
	## Draw impact shockwaves
	for site in game.impacts:
		if site.visible == True:
			site.draw()
		#site.radius == int(site.clock.get_time())
		elapsedtime = pygame.time.get_ticks() - site.creationtime
		if elapsedtime < max(maprect.width, maprect.height)*1000/speed*1.41: # Update the radius until it is off the screen. 
			site.radius = int(speed*elapsedtime/1000)
	drawConsole()
	
	## Check for impacts
	for site in game.impacts:
		elapsedtime = pygame.time.get_ticks() - site.creationtime
		for j in range(len(game.stations)):
			if elapsedtime/1000 > site.timetotower[j]:
				if site.detected[j] == False:
					site.detected[j] = True
					game.stations[j].trigger()
					game.stations[j].detectedtime = datetime.datetime.now()
					prettytime = datetime.datetime.now().strftime("%H:%M:%S.") + datetime.datetime.now().strftime("%f")[:2]
					game.stations[j].textline1 = "Detected at {0}".format(prettytime) 
					if game.ISSuplink:
						game.stations[j].textline2 = "Impact: +{0:.2f} s".format(elapsedtime/1000)
						game.stations[j].textline3 = "Distance: {0:.2f} m".format(elapsedtime/1000*speedofsound)
						game.stations[j].textline4 = "Map distance: {0:.2f} cm".format(elapsedtime/1000*speedofsound*mapconversion)
					if not game.ISSuplink:
						game.stations[j].textline2 = "Impact: +Unknown"
						game.stations[j].textline3 = "Distance: Unknown"
						game.stations[j].textline4 = "Map distance: Unknown"

					## Update time delta information
					if j == 0:
						if site.detected[1] == True:
							timedelta = game.stations[j].detectedtime - game.stations[1].detectedtime
							prettytimedelta = datetime.datetime.utcfromtimestamp(timedelta.total_seconds())
							prettytimedelta = prettytimedelta.strftime("%S.") + prettytimedelta.strftime("%f")[:2]
							game.deltas[0].textline1 = "time delta: {0} s".format(prettytimedelta)
							game.deltas[0].textline2 = "distance delta: {0:.1f} m".format(timedelta.total_seconds()*speedofsound)
							game.deltas[0].textline3 = "map distance delta: {0:.1f} cm".format(timedelta.total_seconds()*speedofsound*mapconversion)
					
					if j == 1:
						if site.detected[0] == True:
							timedelta = game.stations[j].detectedtime - game.stations[0].detectedtime
							prettytimedelta = datetime.datetime.utcfromtimestamp(timedelta.total_seconds())
							prettytimedelta = prettytimedelta.strftime("%S.") + prettytimedelta.strftime("%f")[:2]
							game.deltas[0].textline1 = "time delta: {0} s".format(prettytimedelta)
							game.deltas[0].textline2 = "distance delta: {0:.1f} m".format(timedelta.total_seconds()*speedofsound)
							game.deltas[0].textline3 = "map distance delta: {0:.1f} cm".format(timedelta.total_seconds()*speedofsound*mapconversion)
							
						if site.detected[2] == True:
							timedelta = game.stations[j].detectedtime - game.stations[2].detectedtime
							prettytimedelta = datetime.datetime.utcfromtimestamp(timedelta.total_seconds())
							prettytimedelta = prettytimedelta.strftime("%S.") + prettytimedelta.strftime("%f")[:2]
							game.deltas[1].textline1 = "time delta: {0} s".format(prettytimedelta)
							game.deltas[1].textline2 = "distance delta: {0:.1f} m".format(timedelta.total_seconds()*speedofsound)
							game.deltas[1].textline3 = "map distance delta: {0:.1f} cm".format(timedelta.total_seconds()*speedofsound*mapconversion)
					
					if j == 2:
						if site.detected[1] == True:
							timedelta = game.stations[j].detectedtime - game.stations[1].detectedtime
							prettytimedelta = datetime.datetime.utcfromtimestamp(timedelta.total_seconds())
							prettytimedelta = prettytimedelta.strftime("%S.") + prettytimedelta.strftime("%f")[:2]
							game.deltas[1].textline1 = "time delta: {0} s".format(prettytimedelta)
							game.deltas[1].textline2 = "distance delta: {0:.1f} m".format(timedelta.total_seconds()*speedofsound)
							game.deltas[1].textline3 = "map distance delta: {0:.1f} cm".format(timedelta.total_seconds()*speedofsound*mapconversion)
		
	
	
	pygame.display.flip()
