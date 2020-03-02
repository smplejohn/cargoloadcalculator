#!/usr/bin/python
# This script takes POST data

# POST variables expected:

# cwidth            - Container width
# cdepth            - Container depth
# cheight           - Container height
# palette_load      - Whether or not this load should be on palettes
# palette_height    - Height of palettes

# name[]    - Array of package identifiers
# length[]  = Array of package depths
# width[]   = Array of package widths
# height[]  - Array of package heights
# qty[]     - Array of how many individual packages this entry represents

# ***** WARNING ABOUT FLAGS *****
# Flags are usually handled by checkboxes. However, POST data only sends the checkboxes that have been checked,
# with no indication which row it belongs to. Therefore, every checkbox should be overwritten to send a value
# of either 'checked' or 'unchecked'

# top[]                 - Array of flags for whether this package may have others below it
# bottom[]              - Array of flags for whether this package may have others below it
# rotation[]            - Array of flags for whether this package may be rotated in space or not
# rotation_standard[]   - Whether this package can be unrotated
# rotation_side[]       - Whether this package can be rotated without changing its bottom face
# rotation_up[]         - Whether this package can be tipped on its side

# Because everything uses sys
import sys
import json

# for handling POST data
import cgi
import cgitb

# Set this to your preferred log destination
logpath = './log'

# default size
container_size = [50,100,50]

# image render size
width, height = 640, 480

# lists of all packages (to start) and containers
packages = []
containers = []

# defines a volume in which a package could be placed
class Zone:
    def __init__(self,px,pz,py,sx,sz,sy,f=False):
        self.posx = px
        self.posz = pz
        self.posy = py
        self.x = sx
        self.z = sz
        self.y = sy
        self.floor=f

    def doesfit(self,xs,ys,zs):
        return xs <= self.x and ys <= self.y and zs <= self.z

    # returns two volumes left over from placing a package in this volume
    def subs(self,xs,zs):
        s = []
        if (self.x-xs > 1.0):
            s.append(Zone(self.posx+xs,self.posz,self.posy,self.x-xs,self.z,self.y,self.floor))
        if (self.z-zs > 1.0):
            s.append(Zone(self.posx,self.posz+zs,self.posy,xs,self.z-zs,self.y,self.floor))
        return s
            
# defines a packages attributes, and position in container space
class Package:
    def __init__(self,name,l,w,h,m,above,below,rotation_ok,r,rs,ru):
        self.name = name
        self.z = l
        self.x = w
        self.y = h
        self.m = m
        self.v = self.x*self.y*self.z
        self.q = self.v*m
        self.above = above
        self.below = below
        self.rotation_ok = rotation
        self.placed = False
        self.posx = 0
        self.posy = 0
        self.posz = 0
        self.r = r
        self.rs = rs
        self.ru = ru
        self.orientations = []
        if rotation_ok:
            if self.r:
                self.orientations.append((w,h,l))
            if self.rs:
                self.orientations.append((h,w,l))
            if self.ru:
                self.orientations.append((h,l,w))
        if len(self.orientations) < 1:
            self.orientations.append((w,h,l))
        self.orientation = 0

    # for sorting: packages locked to the floor should be placed first, then the bulkiest packages
    def __lt__ (self,other):
        if self.below != other.below:
            return other.below
        return other.q < self.q
        
    def rotate(self):
        no_overrun_flag = True
        self.orientation = self.orientation + 1
        if self.orientation >= len(self.orientations):
            self.orientation = 0
            no_overrun_flag = False
        self.x = self.orientations[self.orientation][0]
        self.y = self.orientations[self.orientation][1]
        self.z = self.orientations[self.orientation][2]
        return no_overrun_flag

# a shipping container; it has a root zone that all other zones are cut from, and a list of packages placed within it
class Container:
    def __init__(self,x,z,h):
        self.zone = Zone(0,0,0,x,z,h,True)
        self.packages = []

    def reportefficiency(self):
        cv = self.zone.x*self.zone.y*self.zone.z
        v = 0
        for p in self.packages:
            v = v + p.v
        return v/cv

# attempt to fit packages into a zone
def fitpackagesintozone(packages,zone):
    subzones = []
    for p in packages:
        # if the package can't have anything below it, and we're not on the floor, reject it
        if not zone.floor and not p.below:
            continue
        # if an already placed package slipped through, reject it
        if p.placed:
            continue
        # if the package fits in its natural orientation, mark it placed and set its position in the container
        while True:
            if zone.doesfit(p.x,p.y,p.z):
                p.placed = True
                p.posx = zone.posx
                p.posy = zone.posy
                p.posz = zone.posz
                # if the package can have things on top of it, and there's space left above it, then create a prioritized zone above the package
                if p.above and zone.y > p.y:
                    subzones.append(Zone(p.posx,p.posz,p.posy+p.y,p.x,p.z,zone.y-p.y))
                # create two new zones from the volume leftover from placing this package. Prioritize the back wall
                subzones.extend(zone.subs(p.x,p.z))
                break
            elif not p.rotate():
                break
        if p.placed:
            break

    # recurse into newly created smaller zones
    for s in subzones:
        fitpackagesintozone(packages,s)


def outputjson():
    print ('Content-type: application/json')
    print ('Access-Control-Allow-Origin: *')
    print ('')
    jstr = ('{')
    cn = 0
    if len(containers)>0:
        jstr += '"containers":['
    cfirst = True
    for c in containers:
        cn += 1
        if not cfirst:
            jstr += ','
        else:
            cfirst = False
        jstr += '{{"name" : "Container {0}",'.format(cn)
        jstr += '"width" : {0},'.format(c.zone.x)
        jstr += '"depth" : {0},'.format(c.zone.z)
        jstr += '"height" : {0},'.format(c.zone.y)
        jstr += '"efficiency" : {0},'.format(c.reportefficiency())
        jstr += '"packages":['
        pfirst = True
            
        for p in c.packages:
            if not pfirst:
                jstr += ','
            else:
                pfirst = False
            jstr += '{{"name" : "{0}",'.format(p.name)
            jstr += '"width" : {0},'.format(p.x)
            jstr += '"height" : {0},'.format(p.y)
            jstr += '"depth" : {0},'.format(p.z)
            jstr += '"position_x" : {0},'.format(p.posx)
            jstr += '"position_y" : {0},'.format(p.posy)
            jstr += '"position_z" : {0},'.format(p.posz)
            jstr += '"weight" : {0},'.format(p.m)
            jstr += '"volume" : {0},'.format(p.v)
            jstr += '"rotatable" : "{0}",'.format(p.rotation_ok)
            jstr += '"rotation_standard" : "{0}",'.format(p.r)
            jstr += '"rotation_side" : "{0}",'.format(p.rs)
            jstr += '"rotation_up" : "{0}",'.format(p.ru)
            jstr += '"orientation" : "{0}",'.format(p.orientation)
            jstr += '"items_ontop_ok" : "{0}",'.format(p.above)
            jstr += '"items_below_ok" : "{0}"'.format(p.below)
            jstr += '}' # close package
        jstr += ']}' # close packages and container
    jstr += ']' # close containers
    if len(packages) > 0:
        if len(containers) > 0:
            jstr += ','
        jstr += '"orphan_packages" : ['
        pfirst = True
        for p in packages:
            if not pfirst:
                jstr += ','
            else:
                pfirst = False
            jstr += '{{"name" : "{0}",'.format(p.name)
            jstr += '"width" : {0},'.format(p.x)
            jstr += '"height" : {0},'.format(p.y)
            jstr += '"depth" : {0},'.format(p.z)
            jstr += '"position_x" : {0},'.format(p.posx)
            jstr += '"position_y" : {0},'.format(p.posy)
            jstr += '"position_z" : {0},'.format(p.posz)
            jstr += '"weight" : {0},'.format(p.m)
            jstr += '"volume" : {0},'.format(p.v)
            jstr += '"rotatable" : "{0}",'.format(p.rotation_ok)
            jstr += '"rotation_standard" : "{0}",'.format(p.r)
            jstr += '"rotation_side" : "{0}",'.format(p.rs)
            jstr += '"rotation_up" : "{0}",'.format(p.ru)
            jstr += '"orientation" : "{0}",'.format(p.orientation)
            jstr += '"items_ontop_ok" : "{0}",'.format(p.above)
            jstr += '"items_below_ok" : "{0}"'.format(p.below)
            jstr += '}' # close package
        jstr += ']' # close orphan_packages
    jstr += '}' # close json
    print(jstr);

# ***** MAIN CODE START *****

# Log to file instead of publishing errors and code to the public
cgitb.enable(display=0,logdir=logpath)

# capture POST data
postdata = cgi.FieldStorage()

# get container size from POST data
container_size[0] = float(postdata.getvalue('cwidth'))
container_size[1] = float(postdata.getvalue('cdepth'))
container_size[2] = float(postdata.getvalue('cheight'))
palette_load = postdata.getvalue('palette_load') == 'checked'
palette_height = float(postdata.getvalue('palette_height'))

# get package details from POST data
if isinstance(postdata.getvalue('name[]'), list):
    for i in range(len(postdata.getvalue('name[]'))):
        name = postdata.getvalue('name[]')[i]
        l = float(postdata.getvalue('length[]')[i])
        w = float(postdata.getvalue('width[]')[i])
        h = float(postdata.getvalue('height[]')[i])
        if palette_load:
            h = h - palette_height
        if h <= 0.0:
            continue
        m = float(postdata.getvalue('weight[]')[i])
        above = postdata.getvalue('top[]')[i] == 'checked'
        below = postdata.getvalue('bottom[]')[i] == 'checked'
        rotation = postdata.getvalue('rotation[]')[i] == 'checked'
        rotation_standard = postdata.getvalue('rotation_standard[]')[i] == 'checked'
        rotation_side = postdata.getvalue('rotation_side[]')[i] == 'checked'
        rotation_up = postdata.getvalue('rotation_up[]')[i] == 'checked'
        
        # if many packages are included on the same line, make them separate entries
        for j in range(int(postdata.getvalue('qty[]')[i])):
            p = Package(name,l,w,h,m,above,below,rotation,rotation_standard,rotation_side,rotation_up)
            packages.append(p)
else:
    name = postdata.getvalue('name[]')
    l = float(postdata.getvalue('length[]'))
    w = float(postdata.getvalue('width[]'))
    h = float(postdata.getvalue('height[]'))
    if palette_load:
        h = h - palette_height
    if h <= 0.0:
        continue
    m = float(postdata.getvalue('weight[]'))
    above = postdata.getvalue('top[]') == 'checked'
    below = postdata.getvalue('bottom[]') == 'checked'
    rotation = postdata.getvalue('rotation[]') == 'checked'
    rotation_standard = postdata.getvalue('rotation_standard[]') == 'checked'
    rotation_side = postdata.getvalue('rotation_side[]') == 'checked'
    rotation_up = postdata.getvalue('rotation_up[]') == 'checked'
    
    # if many packages are included on the same line, make them separate entries
    for j in range(int(postdata.getvalue('qty[]'))):
        p = Package(name,l,w,h,m,above,below,rotation,rotation_standard,rotation_side,rotation_up)
        packages.append(p)

# sort packages by bulkiness
packages.sort()

# attempt to fit packages in a new container
while True:
    if len(packages) < 1:
        break
    containers.append(Container(container_size[0],container_size[1],container_size[2]))
    fitpackagesintozone(packages,containers[-1].zone)
    
    # remove packages that have been successfully placed from the orphan list
    placed = []
    for i in range(len(packages)):
        if packages[i].placed:
            placed.append(i)
    for i in reversed(placed):
        containers[-1].packages.append(packages.pop(i))
        
    # if we get to the end and no more packages have been placed, it's time to stop trying
    if len(containers[-1].packages) < 1:
        containers.pop(-1)
        break
# init render settings
#init()
# final output
outputjson()
