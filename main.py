from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math


app = Ursina()
grass_texture = load_texture('assets/grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture  = load_texture('assets/dirt_block.png')
red_brick_texture = load_texture('assets/red_brick_block.png')
sky_texture   = load_texture('assets/skybox.png')
arm_texture   = load_texture('assets/arm_texture.png')
punch_sound   = Audio('assets/punch_sound',loop = False, autoplay = False)
block_pick = 1

window.fps_counter.enabled = False
window.exit_button.visible = False

boardSize = Vec2(30,30)
enemiesNumber = 10
enemySpeed = 0.03
bulletList = []

def update():
	global block_pick
	moveEnemies()
	moveBullets()
	rotateEnemies()

	if held_keys['left mouse'] or held_keys['right mouse']:
		hand.active()
	else:
		hand.passive()

	if held_keys['1']: block_pick = 1
	if held_keys['2']: block_pick = 2
	if held_keys['3']: block_pick = 3
	if held_keys['4']: block_pick = 4
	if held_keys['5']: block_pick = 5

class Voxel(Button):
	def __init__(self, position = (0,0,0), texture = grass_texture):
		super().__init__(
			parent = scene,
			position = position,
			model = 'assets/block',
			collider='box',
			origin_y = 0.5,
			texture = texture,
			color = color.color(0,0,random.uniform(0.9,1)),
			scale = 0.5)
		self.bulletSpeed = 0.03
		self.ttl = 80

	def input(self,key):
		if self.hovered:
			if key == 'left mouse down':
				punch_sound.play()
				if block_pick == 1: voxel = Voxel(position = self.position + mouse.normal, texture = grass_texture)
				if block_pick == 2: voxel = Voxel(position = self.position + mouse.normal, texture = stone_texture)
				if block_pick == 3: voxel = Voxel(position = self.position + mouse.normal, texture = brick_texture)
				if block_pick == 4: voxel = Voxel(position = self.position + mouse.normal, texture = dirt_texture)
				if block_pick == 5: voxel = Voxel(position = self.position + mouse.normal, texture = red_brick_texture)

			if key == 'right mouse down':
				punch_sound.play()
				destroy(self)

class Sky(Entity):
	def __init__(self):
		super().__init__(
			parent = scene,
			model = 'sphere',
			texture = sky_texture,
			scale = 150,
			double_sided = True)

class Hand(Entity):
	def __init__(self):
		super().__init__(
			parent = camera.ui,
			model = 'assets/arm',
			texture = arm_texture,
			scale = 0.2,
			rotation = Vec3(150,-10,0),
			position = Vec2(0.4,-0.6))

	def active(self):
		self.position = Vec2(0.3,-0.5)

	def passive(self):
		self.position = Vec2(0.4,-0.6)
		
def generateEnemies():
	for i in range(enemiesNumber):
		enemyList.append(Entity(model='assets/creeper_model', texture="creeper_texture.png"))
		enemyList[i].collider = 'box'
		enemyList[i].position = Vec3(random.random()*boardSize.x,10,random.random()*boardSize.y)
		enemyList[i].scale*=(1.5+random.random())

def moveEnemies():
	playerPosition = player.get_position()
	for i in enemyList:
		direction = Vec3(enemySpeed if i.x < playerPosition[0] else -enemySpeed,0,enemySpeed if i.z < playerPosition[2] else -enemySpeed).normalized()
		origin = i.world_position + (i.up*.5) + (direction/2)
		ray = raycast(origin , direction, ignore=[i,], distance=.25, debug=False)
		if not ray.hit:
			i.x += enemySpeed if i.x < playerPosition[0] else -enemySpeed
			i.z += enemySpeed if i.z < playerPosition[2] else -enemySpeed
			if i.y>0:
				i.y -= time.dt * 9.81
			elif i.y<0:
				i.y = 0

def rotateEnemies():
	for i in enemyList:
		i.look_at(player.get_position())
		i.rotation_x = 0
		i.rotation_z = 0
		i.rotation_y += 180
		# enemyList[i].rotation_y = math.degrees(math.atan(float(playerPosition[0]-enemyList[i].x)/(playerPosition[2]-enemyList[i].z )))
		# if playerPosition[2] > enemyList[i].z:
		# 	enemyList[i].rotation_y = enemyList[i].rotation_y*-1

def input(key):
	if key == 'middle mouse down':
		nowyBullet = Voxel(position = player.position, texture = red_brick_texture)
		nowyBullet.collider = 'box'
		nowyBullet.rotation = player.rotation
		nowyBullet.y += 1.5
		bulletList.append(nowyBullet) 

def moveBullets():
	for i in bulletList:
		i.ttl -=1
		if i.ttl<=0:
			bulletList.remove(i)
			destroy(i)
			return
		
		direction = i.forward
		origin = i.world_position + (i.up*.5) + (direction/2)
		ray = raycast(origin , direction, ignore=[i,], distance=.25, debug=False)
		if ray.hit :
			bulletList.remove(i)
			destroy(i)
			enemyList.remove(ray.entity)
			destroy(ray.entity)
			return
		i.position += i.forward

for z in range(30):
	for x in range(30):
		voxel = Voxel(position = (x,0,z))

enemyList = []
generateEnemies()
player = FirstPersonController()
player.x += 10
player.z += 10
sky = Sky()
hand = Hand()


app.run()