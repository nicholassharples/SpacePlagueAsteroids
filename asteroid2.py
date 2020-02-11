import sys, pygame, datetime
import numpy, random
pygame.init()

pygame.mouse.set_visible(False)
pygame.key.set_repeat(1000,1000)


## Distance between Greenwich piers is 650m. This is 200 pixels in our map, so 3.25m = 1 pixel
pixeltodistance = 3.25
## Speed of sound = 343 m/s, so 105 pixels per second
speed = 105 # shockwave speed in pixels per second
distancetomap = 1  ## update once we see the maps!


clock = pygame.time.Clock()

showFPS = True

size = width, height = 1366,768

## Define Colours
black = 0,0,0
background = 64,64,64

screen = pygame.display.set_mode((width,height), pygame.FULLSCREEN | pygame.HWSURFACE| pygame.DOUBLEBUF | pygame.RESIZABLE)
#screen = pygame.display.set_mode((width,height),pygame.SCALED)
gameCaption = pygame.display.set_caption("Asteroid Tracking")

Font = pygame.font.Font("C:\\Windows\\Fonts\\Verdana.ttf", 20)


screen.fill(background)
map = pygame.image.load("SmallMap.png")
maprect = map.get_rect()


def drawMap():
	screen.blit(map,maprect)
	for tower in stations:
		tower.draw()

def drawFPS():
	FPS = int(clock.get_fps())				
	screen.blit(Font.render("FPS: " + str(FPS), True, black), (0, 0))	

def drawConsole():
	pygame.draw.rect(screen, background, (maprect.right, 0, width-maprect.width, height))
	for tower in stations:
		tower.drawtext()
	for text in ISStexts:
		text.drawtext()

impacts = []
stations = []
ISStexts = []

class ISStext(object):
	def __init__(self,x,y,text):
		self.x = x
		self.y = y
		self.text = text
		self.colour = (122,122,0)
		ISStexts.append(self)
	
	def drawtext(self):
		screen.blit(Font.render(self.text, True, self.colour), (self.x, self.y))

	
class impact(object):
	def __init__(self,x,y,visible):
		self.x = x
		self.y = y
		self.visible = visible
		self.creationtime = pygame.time.get_ticks()
		self.timetotower = []
		for tower in stations:
			distance = numpy.sqrt((self.x - tower.x)**2 + (self.y - tower.y)**2)
			self.timetotower.append(distance/speed)
		print(self.timetotower)
		self.detected = numpy.repeat(False, len(stations))
		self.radius = 2
		
		impacts.append(self)
	
	def draw(self):
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
		self.text = text
		self.state = "Listening"
		self.lasttriggered = pygame.time.get_ticks()
		self.defaultcolour = colour
		self.flashcolour = flashcolour
		self.colour = colour
		stations.append(self)
	
	def draw(self):
		pygame.draw.circle(screen, self.colour, (self.x,self.y), 10)

	def trigger(self):
		self.colour = self.flashcolour
		self.lasttriggered = pygame.time.get_ticks()
		self.state = "Triggered"
	
	def reset(self):
		self.colour = self.defaultcolour
		self.state = "Listening"
		
	def drawtext(self):
		screen.blit(Font.render(self.text, True, self.colour), (self.textx, self.texty))


## Create stations
station(int(maprect.width/2), 20 , "red", (255,0,0), (255,255,0), maprect.width + 100, 40, "Red Tower: Listening")
station(20, maprect.height-20 , "green", (0,255,0), (0,255,255), maprect.width + 100, 80, "Green Tower: Listening")
station(maprect.width-20, maprect.height-20 , "blue", (0,0,255), (255,0,255), maprect.width + 100, 120, "Blue Tower: Listening")

## Create text
ISStext(maprect.width + 40, 20, "ISS: tracking asteroids...")

drawMap()

pygame.display.flip()

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q: sys.exit()
			if event.key == pygame.K_SPACE:
				impact(200,450, True)
			if event.key == pygame.K_r:
				impact(random.randint(1,maprect.width), random.randint(1,maprect.height), True)
	clock.tick(30)
	drawMap()
	if showFPS == True:
		drawFPS()
	
	## Update stations
	for tower in stations:
		elapsedtime = pygame.time.get_ticks() - tower.lasttriggered
		if elapsedtime/1000 > 2 and tower.state == "Triggered":
			tower.reset()
	
	
	## Draw impact shockwaves
	for site in impacts:
		if site.visible == True:
			site.draw()
		#site.radius == int(site.clock.get_time())
		elapsedtime = pygame.time.get_ticks() - site.creationtime
		site.radius = int(speed*elapsedtime/1000)
	
	drawConsole()
	
	## Check for impacts
	## ToDo: Calculate these once? We know the impact times, after all! Done. Now we need to fix impact detection.
	for site in impacts:
		elapsedtime = pygame.time.get_ticks() - site.creationtime
		for j in range(len(stations)):
			if elapsedtime/1000 > site.timetotower[j]:
				if site.detected[j] == False:
					site.detected[j] = True
					stations[j].trigger()
					actualtime = datetime.datetime.now().strftime("%H:%M:%S.") + datetime.datetime.now().strftime("%f")[:2]
					stations[j].text = "Detected at {0}.  Impact +{1:.2f} seconds".format(actualtime, elapsedtime/1000)
				#if elapsedtime/1000 > site.timetotower[j] + 2:
				#	stations[j].reset()
		#if elapsedtime/1000 > 10: ## Remove impact sites after 10 seconds
		#	del site
		#for tower in stations:
		#	distance = numpy.sqrt((site.x - tower.x)**2 + (site.y-tower.y)**2)
		#	if  distance <= site.radius and distance > site.radius - 1:
		#		print("Impact detected")
		#		tower.trigger()
		#		elapsedtime = pygame.time.get_ticks() - site.creationtime
		#		tower.text = str("Recorded after " + str(int(elapsedtime/1000)) + " seconds")
		
	
	
	pygame.display.flip()
