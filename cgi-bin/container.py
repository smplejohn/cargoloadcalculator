logpath = './log'
container_size = [50,100,50]

# config for palette height, and margin of error %, prefer flat to back, heaviest on bottom

# container dimensions are width, height, depth

# package data is label, quantity, weight, w,h,d, v, bools for palette, whether the package can be rotated, tipped on its side, whether it can have something on top of it, and whether it can be stacked on something else

# retrieve list of objects
# if q>1, explode

# sort list by volume, weight, and floorlocked

# make columns with the least wasted volume out of objects

# column data: objects and relative positions

# arrange columns against back wall

import cgi
import cgitb
cgitb.enable(display=0,logdir=logpath)
postdata = cgi.FieldStorage()

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


class Zone:
    def __init__(self,px,pz,py,sx,sz,sy,f=False):
        #print("Zone made P:{0},{1},{2} S:{3},{4},{5}<br/>".format(px,pz,py,sx,sz,sy))
        if sx < 1 or sz < 1 or sy < 1:
            print("Warning : Zone made P:{0},{1},{2} S:{3},{4},{5}<br/>".format(px,pz,py,sx,sz,sy))
        self.posx = px
        self.posz = pz
        self.posy = py
        self.x = sx
        self.z = sz
        self.y = sy
        self.floor=f
    def doesfit(self,xs,zs,ys):
#        return (xs < self.x and zs < self.z and ys < self.y)
        #print("Testing fit: ")
        if xs > self.x:
            #print("x{0} doesn't fit into {1}<br/>".format(xs,self.x))
            return False
        if zs > self.z:
            #print("z{0} doesn't fit into {1}<br/>".format(zs,self.z))
            return False
        if ys > self.y:
            #print("y{0} doesn't fit into {1}<br/>".format(ys,self.y))
            return False
        #print("Fit!<br/>")
        return True
    def subs(self,xs,zs):
        s = []
        if (self.x-xs > 1.0):
            #print("Making zone from sub A<br/>")
            s.append(Zone(self.posx+xs,self.posz,self.posy,self.x-xs,self.z,self.y,self.floor))
        if (self.z-zs > 1.0):
            #print("Making zone from sub B<br/>")
            s.append(Zone(self.posx,self.posz+zs,self.posy,xs,self.z-zs,self.y,self.floor))
        return s
            

class Package:
    def __init__(self,name,l,w,h,m,above,below,rotation):
        self.name = name
        self.z = l
        self.x = w
        self.y = h
        self.m = m
        self.v = self.x*self.y*self.z
        self.q = self.v*m
        self.above = above
        self.below = below
        self.rotation = rotation
        self.rotated = False
        self.placed = False
        self.posx = 0
        self.posy = 0
        self.posz = 0

    def __str__(self):
        return '"{0}" {1}x{2}x{3} ({4}) w {5} z {6} Above {7} Below {8} Rotate {9}'.format(self.name, self.z, self.x, self.y, self.v, self.m, self.q, self.above, self.below, self.rotation)
        
    def __lt__ (self,other):
        if self.below != other.below:
            return other.below
        return other.q < self.q
        
    def rotate(self):
        if self.rotation:
            c = self.z
            self.z = self.x
            self.x = c
            self.rotated = not self.rotated
    def verts(self):
        #return ((self.posx,self.posy,self.posz),(self.posx,self.posy,self.posz+self.z),(self.posx+self.x,self.posy,self.posz+self.z),(self.posx,self.posy,self.posz+self.z),(self.posx,self.posy+self.y,self.posz),(self.posx,self.posy+self.y,self.posz+self.z),(self.posx+self.x,self.posy+self.y,self.posz+self.z),(self.posx,self.posy+self.y,self.posz+self.z))
        return [[   self.posx,          self.posy,          self.posz           ],
                [   self.posx,          self.posy,          self.posz+self.z    ],
                [   self.posx+self.x,   self.posy,          self.posz+self.z    ],
                [   self.posx+self.x,   self.posy,          self.posz           ],
                [   self.posx,          self.posy+self.y,   self.posz           ],
                [   self.posx,          self.posy+self.y,   self.posz+self.z    ],
                [   self.posx+self.x,   self.posy+self.y,   self.posz+self.z    ],
                [   self.posx+self.x,   self.posy+self.y,   self.posz           ]]

        

class Container:
    def __init__(self,x,z,h):
        #print("Making zone from container<br/>")

        self.zone = Zone(0,0,0,x,z,h,True)
        self.packages = []
    def reportefficiency(self):
        cv = self.zone.x*self.zone.y*self.zone.z
        v = 0
        for p in self.packages:
            v = v + p.v
        #print("Container efficiency: {0}<br/>".format(v/cv))
        return v/cv
    def render(self):
        pass

packages = []

#initialize package list from POST data
container_size[0] = float(postdata.getvalue('cwidth'))
container_size[1] = float(postdata.getvalue('cdepth'))
container_size[2] = float(postdata.getvalue('cheight'))
for i in range(len(postdata.getvalue('name[]'))):
    name = postdata.getvalue('name[]')[i]
    l = float(postdata.getvalue('length[]')[i])
    w = float(postdata.getvalue('width[]')[i])
    h = float(postdata.getvalue('height[]')[i])
    m = float(postdata.getvalue('weight[]')[i])
    above = postdata.getvalue('top[]')[i] == 'checked'
    below = postdata.getvalue('bottom[]')[i] == 'checked'
    rotation = postdata.getvalue('rotation[]')[i] == 'checked'
    
    for j in range(int(postdata.getvalue('qty[]')[i])):
        p = Package(name,l,w,h,m,above,below,rotation)
        packages.append(p)

#sort packages by bulkiness
packages.sort()


def fitpackagesintozone(packages,zone):
    subzones = []
    for p in packages:
        if not zone.floor and not p.below:
            continue
        if p.placed:
            continue
        if zone.doesfit(p.x,p.z,p.y):
            p.placed = True
            p.posx = zone.posx
            p.posz = zone.posz
            p.posy = zone.posy
            if p.above and zone.y > p.y:
                #print("Making zone from package<br/>")
                subzones.append(Zone(p.posx,p.posz,p.posy+p.y,p.x,p.z,zone.y-p.y))
            subzones.extend(zone.subs(p.x,p.z))
            break
        elif p.rotation and zone.doesfit(p.z,p.x,p.y):
            p.rotate()
            p.placed = True
            p.posx = zone.posx
            p.posz = zone.posz
            p.posy = zone.posy
            if p.above and zone.y > p.y:
                #print("Making zone from package<br/>")
                subzones.append(Zone(p.posx,p.posz,p.posy+p.y,p.x,p.z,zone.y-p.y))
            subzones.extend(zone.subs(p.x,p.z))
            break
    for s in subzones:
        fitpackagesintozone(packages,s)

#print ("Placing {0} packages<br/>".format(len(packages)))
containers = []
while True:
    if len(packages) < 1:
        break
    containers.append(Container(container_size[0],container_size[1],container_size[2]))
    #print("Made container #{0} with dimensions {1}x{2}x{3}<br/>".format(len(containers),container_size[0],container_size[1],container_size[2]))
    fitpackagesintozone(packages,containers[-1].zone)
    placed = []
    for i in range(len(packages)):
        if packages[i].placed:
            placed.append(i)
    for i in reversed(placed):
        containers[-1].packages.append(packages.pop(i))
    if len(containers[-1].packages) < 1:
        print("No packages remaining fit in container<br/>")
        containers.pop(-1)
        #for p in packages:
            #print("{0}<br/>".format(p))
        break
    containers[-1].reportefficiency()
    containers[-1].render()
    #print("{0} packages placed. {1} remain.</br>".format(len(containers[-1].packages),len(packages)),flush=True)
    
 

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from PIL import Image
from PIL import ImageOps

import sys
import base64

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from PIL import Image
from PIL import ImageOps

import sys

width, height = 640, 480

def init():
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow("Containers Render Window")
    glutHideWindow()

    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0,width/height,0.5,500.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(150.0, 150.0, 150.0, 25.0, 25.0, 50.0, 0.0, 1.0, 0.0)
    
def drawverts(v,unlocked,above,below):
    glPolygonOffset(1,1)
    glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glBegin(GL_QUADS)

    if unlocked:
        glColor4d(0.0,1.0,0.0,0.5)
    else:
        glColor4d(0.0,1.0,1.0,0.5)

    #front
    glVertex3dv(v[1])
    glVertex3dv(v[5])
    glVertex3dv(v[6])
    glVertex3dv(v[2])

    #top
    glVertex3dv(v[3])
    glVertex3dv(v[7])
    glVertex3dv(v[6])
    glVertex3dv(v[2])
    
    #side
    glVertex3dv(v[6])
    glVertex3dv(v[7])
    glVertex3dv(v[4])
    glVertex3dv(v[5])

    glEnd()

    topcolor = [0.0,0.0,0.0,1.0]
    bottomcolor = [0.0,0.0,0.0,1.0]
    if not above:
        topcolor = [1.0,0.0,0.0,1.0]
    if not below:
        bottomcolor = [1.0,0.0,0.0,1.0]


    glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
    glDisable(GL_POLYGON_OFFSET_FILL)
    glColor4f(0,0,0,1)
    glBegin(GL_QUADS)

    glColor4dv(bottomcolor)
    glVertex3dv(v[1])
    glColor4dv(topcolor)
    glVertex3dv(v[5])
    glVertex3dv(v[6])
    glColor4dv(bottomcolor)
    glVertex3dv(v[2])

    glVertex3dv(v[3])
    glColor4dv(topcolor)
    glVertex3dv(v[7])
    glVertex3dv(v[6])
    glColor4dv(bottomcolor)
    glVertex3dv(v[2])
    
    glColor4dv(topcolor)
    glVertex3dv(v[6])
    glVertex3dv(v[7])
    glVertex3dv(v[4])
    glVertex3dv(v[5])

    glEnd()
    
def drawcontainer(c):
    glPolygonOffset(1,1)
    glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
    glDisable(GL_POLYGON_OFFSET_FILL)
    # draw container
    
    glBegin(GL_QUADS)

    glColor4d(1.0,0.0,0.0,1.0)

    glVertex3d(0,0,c.zone.z)
    glVertex3d(0,c.zone.y,c.zone.z)
    glVertex3d(0,c.zone.y,0)
    glVertex3d(0,0,0)
    
    glVertex3d(c.zone.x,0,c.zone.z)
    glVertex3d(c.zone.x,c.zone.y,c.zone.z)
    glVertex3d(c.zone.x,c.zone.y,0)
    glVertex3d(c.zone.x,0,0)

    glVertex3d(0,0,0)
    glVertex3d(0,c.zone.y,0)
    glVertex3d(c.zone.x,c.zone.y,0)
    glVertex3d(c.zone.x,0,0)

    glVertex3d(0,0,c.zone.z)
    glVertex3d(0,c.zone.y,c.zone.z)
    glVertex3d(c.zone.x,c.zone.y,c.zone.z)
    glVertex3d(c.zone.x,0,c.zone.z)

    glVertex3d(0,0,0)
    glVertex3d(c.zone.x,0,0)
    glVertex3d(c.zone.x,0,c.zone.z)
    glVertex3d(0,0,c.zone.z)

    glVertex3d(0,c.zone.y,0)
    glVertex3d(c.zone.x,c.zone.y,0)
    glVertex3d(c.zone.x,c.zone.y,c.zone.z)
    glVertex3d(0,c.zone.y,c.zone.z)

    glEnd()
    

def render(c):

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    
    drawcontainer(c)

    for p in c.packages:
        drawverts(p.verts(),p.rotation,p.above,p.below)

    glFlush()

from io import BytesIO

def renderimg(c):
    render(c)

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGBA", (width, height), data)
    image = ImageOps.flip(image) # in my case image is flipped top-bottom for some reason
    buffer = BytesIO()
    image.save(buffer,format='PNG')
    im_data = base64.b64encode(buffer.getvalue())
    
    return im_data.decode()
    
    #img_tag='<img src="data:image/png;base64,{0}">'.format(im_data.decode())
    #print(img_tag)


def outputjson():
    print ('Content-type: application/json\n')
    print('{')
    cn = 0
    for c in containers:
        cn += 1
        print('\t"container" : {')
        print('\t\t"name" : "Container {0}"'.format(cn))
        print('\t\t"width" : "{0}"'.format(c.zone.x))
        print('\t\t"depth" : "{0}"'.format(c.zone.z))
        print('\t\t"height" : "{0}"'.format(c.zone.y))
        print('\t\t"efficiency" : "{0}"'.format(c.reportefficiency()))
        print('\t\t"imagedata" : "{0}"'.format(renderimg(c)))
        for p in c.packages:
            print('\t\t"package" : {')
            print('\t\t\t"name" : "{0}"'.format(p.name))
            print('\t\t\t"width" : "{0}"'.format(p.x))
            print('\t\t\t"height" : "{0}"'.format(p.y))
            print('\t\t\t"depth" : "{0}"'.format(p.z))
            print('\t\t\t"position_x" : "{0}"'.format(p.posx))
            print('\t\t\t"position_y" : "{0}"'.format(p.posy))
            print('\t\t\t"position_z" : "{0}"'.format(p.posz))
            print('\t\t\t"weight" : "{0}"'.format(p.m))
            print('\t\t\t"volume" : "{0}"'.format(p.v))
            print('\t\t\t"rotatable" : "{0}"'.format(p.rotation))
            print('\t\t\t"rotated" : "{0}"'.format(p.rotated))
            print('\t\t\t"items_ontop_ok" : "{0}"'.format(p.above))
            print('\t\t\t"items_below_ok" : "{0}"'.format(p.below))
            print('\t\t}')
        print('\t}')
    if len(packages) > 0:
        print('\t"orphan_packages" : {')
        for p in packages:
            print('\t\t"package" : {')
            print('\t\t\t"name" : "{0}"'.format(p.name))
            print('\t\t\t"width" : "{0}"'.format(p.x))
            print('\t\t\t"height" : "{0}"'.format(p.y))
            print('\t\t\t"depth" : "{0}"'.format(p.z))
            print('\t\t\t"position_x" : "{0}"'.format(p.posx))
            print('\t\t\t"position_y" : "{0}"'.format(p.posy))
            print('\t\t\t"position_z" : "{0}"'.format(p.posz))
            print('\t\t\t"weight" : "{0}"'.format(p.m))
            print('\t\t\t"volume" : "{0}"'.format(p.v))
            print('\t\t\t"rotatable" : "{0}"'.format(p.rotation))
            print('\t\t\t"rotated" : "{0}"'.format(p.rotated))
            print('\t\t\t"items_ontop_ok" : "{0}"'.format(p.above))
            print('\t\t\t"items_below_ok" : "{0}"'.format(p.below))
            print('\t\t}')
        print('\t}')
    print('}')

def outputhtml():
    print ('Content-type: text/html\n')
    print ('<html><body>')
    cn = 0
    for c in containers:
        cn += 1
        print("<h3>Container #{0} {1}% space filled</h3>".format(cn,c.reportefficiency()*100))
        print("W: {0} D: {1} H: {2}<br/>".format(container_size[0],container_size[1],container_size[2]))
        print("<table><tr><th>Name</th><th>X</th><th>Z</th><th>H</th><th>Rotated</th><th>Width</th><th>Depth</th><th>Height</th><th>Stackable (Above)</th><th>Stackable (Below)</th></tr>")
        for p in c.packages:
            print("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td><td>{8}</td><td>{9}</td></tr>".format(p.name,p.posx,p.posz,p.posy,p.rotated,p.x,p.z,p.y,p.above,p.below))
        print("</table>")
        print('<img src="data:image/png;base64,{0}">'.format(renderimg(c)))
        print("<br/>")
    print ('</body></html>')


init()
outputjson()
