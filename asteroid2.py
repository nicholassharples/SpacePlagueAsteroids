import sys, pygame, time
import numpy, random
pygame.init()

pygame.mouse.set_visible(False)
pygame.key.set_repeat(1000,1000)

speed = 10

clock = pygame.time.Clock()

showFPS = True

size = width, height = 1366,768
speed = [2,2]
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

impacts = []
stations = []

impactsite = (300,450)
	
class impact(object):
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.clock = pygame.time.Clock()
		self.clock.tick()
		print(self.clock.get_time())
		self.radius = 2
		#self.radius = int(self.clock.get_time()) # /1000 * speed)
		
		impacts.append(self)
	
	def draw(self):
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
		self.cooldown = 30
		self.defaultcolour = colour
		self.flashcolour = flashcolour
		self.colour = colour
		stations.append(self)
	
	def draw(self):
		pygame.draw.circle(screen, self.colour, (self.x,self.y), 10)

	def trigger(self):
		self.colour = self.flashcolour
		self.cooldown = 29
	
	def reset(self):
		self.colour = self.defaultcolour
		self.cooldown = 30
		
	def drawtext(self):
		screen.blit(Font.render(self.text, True, self.colour), (self.textx, self.texty))

station(int(maprect.width/2), 20 , "red", (255,0,0), (255,255,0), maprect.width + 100, 40, "Red Tower: Listening")
station(20, maprect.height-20 , "green", (0,255,0), (0,255,255), maprect.width + 100, 80, "Green Tower: Listening")
station(maprect.width-20, maprect.height-20 , "blue", (0,0,255), (255,0,255), maprect.width + 100, 120, "Blue Tower: Listening")

drawMap()

pygame.display.flip()

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q: sys.exit()
			if event.key == pygame.K_SPACE:
				impact(200,450)
			if event.key == pygame.K_r:
				impact(random.randint(1,maprect.width), random.randint(1,maprect.height))
	#pygame.time.wait(5)
	clock.tick(30)
	drawMap()
	if showFPS == True:
		drawFPS()
	
	## Update stations
	for tower in stations:
		if tower.cooldown == 0:
			tower.reset()
		elif tower.cooldown < 30:
			tower.cooldown -= 1
	
	
	## Draw impact shockwaves
	for site in impacts:
		site.draw()
		#site.radius == int(site.clock.get_time())
		site.radius +=1
	
	drawConsole()
	
	## Check for impacts
	for site in impacts:
		for tower in stations:
			distance = numpy.sqrt((site.x - tower.x)**2 + (site.y-tower.y)**2)
			if  distance <= site.radius and distance > site.radius - 1:
				print("Impact detected")
				tower.trigger()
				site.clock.tick()
				tower.text = str(site.clock.get_time())
		
	
	pygame.display.flip()
