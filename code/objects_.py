from bullets import Bullet_mat
from stats import *
from guns import Gun

tags = {
    'M':'smg',
    'S':'shotgun',
    'R':'rifle',
    'B':'banana_gun',
    'P':'plasma_gun',
    'L':'rocket_launcher',
    'C':'crossbow',
    'G':'grenade_launcher',
    'H':'pistol',
    'D':'double_barrel',
    'I':'sniper'
}

#handle,shootpoint,fire rate,inaccuracy,mag size,reload_speed,shots,chamber,,chamber_speed,ammo_type
#bullet_mat
#gun mat
#lifetime = how long the bullet lives
#speed = well the speed
#dmg = is the damage
#bouncy = makes the bullet bouncy
#physics = gives the bullet grav and bouncy and decceleration (decelration,bouncy_coefficient,gravity)
#grav = just grav and decelleration no bounce (deccleration,gravity)
#pierce = how many times it pierces, starts at 1 = 1 pierce
#explode = and explosion (takes the range of the explosion) and modifies damage based on distance from explosion.

# [Gun,[],Bullet_mat(),{}]

##GYNS
#semi = semiautomatic
#man = have to chamber
#shot = pellet reload

guns = {
    'smg':[Gun,[(3*scale,4*scale),(9*scale,1*scale),0.1,20,1600,1.5,1,1,0.5,'light_ammo'],Bullet_mat(lifetime = 5,dmg=11,speed=6*scale),{}],#smg
    'shotgun':[Gun,[(3*scale,4*scale),(13*scale,1*scale),1,10,5,0.75,7,1,1,'shells'],Bullet_mat(lifetime=5,dmg=15,speed=5*scale),{'man':True,'pellet':True,'shot':True}],#shotgun
    'rifle':[Gun,[(5*scale,4*scale),(14*scale,2*scale),0.25,1,20,2,1,1,0.75,'medium_ammo'],Bullet_mat(lifetime=5,dmg=20,speed=10*scale),{}],#rifle
    'banana_gun':[Gun,[(3*scale,8*scale),(19*scale,6*scale),0,1,0,2,1,1,2,'rockets'],Bullet_mat(lifetime=11,dmg=80,speed=5*scale,explode=60,bouncy=True),{'man':True}],#banana gun
    'grenade_launcher':[Gun,[(3*scale,4*scale),(12*scale,2*scale),0.25,4,5,0.80,1,0,0.5,'rockets'],Bullet_mat(lifetime = 5,speed=15,dmg=70,physics=(0.7,20,0.25),explode=40),{'pellet':True,'semi':True,'drum':True}],#physics = (0.7,10,0.25)
    'plasma_gun':[Gun,[(4*scale,2*scale),(12*scale,3*scale),0.16,2,35,2,1,1,0.75,'medium_ammo'],Bullet_mat(lifetime = 3,speed = 5*scale,bouncy=True,dmg=20),{}],
    'crossbow':[Gun,[(2*scale,2*scale),(9*scale,1*scale),1,0,5,2,1,1,1,'sniper_ammo'],Bullet_mat(lifetime = 5,speed = 6*scale,grav= (0.7,0.25),dmg = 40,pierce = 2),{'man':True}],
    'double_barrel':[Gun,[(1*scale,2*scale),(8*scale,0),0.2,12,0,0.5,8,2,0.5,'shells'],Bullet_mat(lifetime = 5,speed = 5*scale,dmg = 20*scale),{'semi':True,'pellet':True,'drum':True,'shot':True}],
    'sniper':[Gun,[(4*scale,3*scale),(15*scale,1*scale),0,0,5,3,1,1,0.75,'sniper_ammo'],Bullet_mat(lifetime=5,speed= 7*scale,dmg= 140),{'semi':True,'man':True}],
    'pistol':[Gun,[(1*scale,2*scale),(5*scale,0),0.3,6,10,1.75,1,1,0.5,'light_ammo'],Bullet_mat(lifetime=5,dmg=30,speed=4*scale),{'semi':True}]
    
}

