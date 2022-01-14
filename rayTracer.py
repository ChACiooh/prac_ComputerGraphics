#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

def vector_length(a):
    return np.sqrt(np.dot(a,a))

def normalize(vec):
    return vec / np.linalg.norm(vec)

# Color
class Color:
    def __init__(self, R, G, B):
        self.color=np.array([R,G,B]).astype(np.float_)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)

# Shader
class Shader:
    def __init__(self, name, type, diffuseColor):
        self.name = name # same with ref
        self.type = type
        self.diffuseColor = diffuseColor

class Lambertian(Shader):
    def __init(self, name, type, diffuseColor):
        super().__init__(name, type, diffuseColor)

class Phong(Shader):
    def __init__(self, name, type, diffuseColor, specularColor, exponent):
        super().__init__(name, type, diffuseColor)
        self.specularColor = specularColor
        self.exponent = exponent

class Camera:
    def __init__(self, viewPoint, viewDir, projNormal,
                    viewUp, projDistance, viewWidth, viewHeight):
        self.viewPoint = viewPoint
        self.viewDir = viewDir
        self.projNormal = projNormal
        self.viewUp = viewUp
        self.projDistance = projDistance
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight

        if self.projDistance == None:
            self.projDistance = vector_length(viewPoint)

        self.u = normalize(np.cross(viewDir, viewUp))
        self.v = normalize(np.cross(self.u, viewDir))
        self.w = -normalize(viewDir)
        self.e = self.viewPoint

        M_v = np.zeros((4,4), dtype=np.float_)
        M_v[:3, 0] = self.u
        M_v[:3, 1] = self.v
        M_v[:3, 2] = self.w
        M_v[:3, 3] = self.e
        M_v[3][3] = 1.0
        self.M_view = np.linalg.inv(M_v)

    def getNormalizedRate(self):
        l = vector_length(self.viewPoint)
        a = normalize(self.viewPoint)
        la = vector_length(a)
        return la / l


# Surface
class Surface:
    def __init__(self, type_, shader):
        self.shader = shader
        self.type = type_

    def getNormal(self, ray):
        print('super')
        return -normalize(ray)

    # s.light(viewPoint, scenePoint, t, surface_list, light) in rayTrace
    def light(self, viewPoint, scenePoint, t, surface_list, light):
        m = viewPoint + scenePoint * t
        n = self.getNormal(m)
        color = np.array([0., 0., 0.]).astype(np.float_)

        l = normalize(light.position - m)
        v = -scenePoint

        not_blocked = True
        for s in surface_list:
            if s != self and s.intersect(m + n * 0.001, l) != np.inf:
                not_blocked = False
                break

        diffuseFactor = light.intensity * self.shader.diffuseColor * max(np.dot(n, l), 0) * not_blocked
        color += diffuseFactor

        if type(self.shader) == Phong:
            phong = np.dot(n, normalize(v + l))
            specularFactor = light.intensity * self.shader.specularColor * max(np.power(np.clip(phong, 0, 1), self.shader.exponent), 0) * not_blocked
            color += specularFactor

        return color

        
class Sphere(Surface):
    def __init__(self, type_, shader, center, radius):
        super().__init__(type_, shader)
        self.center = center
        self.radius = radius

    def getNormal(self, ray):
        #print('Sphere normal')
        return normalize(ray - self.center)

    def intersect(self, O, dir):
        p = O - self.center
        a = np.dot(dir, dir)
        b = 2 * np.dot(dir, p)
        c = np.dot(p, p) - (self.radius ** 2)
        dist = b ** 2 - 4 * a * c

        if dist > 0:
            delta = np.sqrt(dist)
            tmax = (-b + delta) / (2.0 * a)
            tmin = (-b - delta) / (2.0 * a)
            if tmin >= 0:
                return tmin
            elif tmin < 0 and tmax >= 0:
                return tmax
        return np.inf
    
def isInBias(x, bias, minPt):
    bias = np.array([bias, bias, bias])
    return x < minPt + bias and x > minPt - bias

class Box(Surface):
    def __init__(self, type, shader, minPt, maxPt):
        super().__init__(type, shader)
        self.minPt = minPt
        self.maxPt = maxPt

    def getNormal(self, ray):
        #print('Box normal')
        x, y, z = ray[0], ray[1], ray[2]
        bias = .005
        if x < self.minPt[0] + bias and x > self.minPt[0] - bias:
            return np.array([-1, 0, 0]).astype(float)
        elif x < self.maxPt[0] + bias and x > self.maxPt[0] - bias:
            return np.array([1, 0, 0]).astype(float)
        elif y < self.minPt[1] + bias and y > self.minPt[1] - bias:
            return np.array([0, -1, 0]).astype(float)
        elif y < self.maxPt[1] + bias and y > self.maxPt[1] - bias:
            return np.array([0, 1, 0]).astype(float)
        elif z < self.minPt[2] + bias and z > self.minPt[2] - bias:
            return np.array([0, 0, -1]).astype(float)
        else:
            return np.array([0, 0, 1]).astype(float)

    def intersect(self, O, direction):
        if direction[0] >= 0:
            txmin = (self.minPt[0] - O[0]) / direction[0]
            txmax = (self.maxPt[0] - O[0]) / direction[0]
        else:
            txmin = (self.maxPt[0] - O[0]) / direction[0]
            txmax = (self.minPt[0] - O[0]) / direction[0]
        if direction[1] >= 0:
            tymin = (self.minPt[1] - O[1]) / direction[1]
            tymax = (self.maxPt[1] - O[1]) / direction[1]
        else:
            tymin = (self.maxPt[1] - O[1]) / direction[1]
            tymax = (self.minPt[1] - O[1]) / direction[1]

        if (txmin > tymax) or (tymin > txmax):
            return np.inf

        tmin = max(txmin, tymin)
        tmax = min(txmax, tymax)

        if direction[2] >= 0:
            tzmin = (self.minPt[2] - O[2]) / direction[2]
            tzmax = (self.maxPt[2] - O[2]) / direction[2]
        else:
            tzmin = (self.maxPt[2] - O[2]) / direction[2]
            tzmax = (self.minPt[2] - O[2]) / direction[2]

        if tmin > tzmax or tzmin > tmax:
            return np.inf
        tmin = max(tmin, tzmin)
        tmax = min(tmax, tzmax)

        if tmin >= 0:
            return tmin
        elif tmin < 0 and tmax >= 0:
            return tmax
        return np.inf


class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity


def rayTrace(camera, scenePoint, surface_list, light_list):
    viewPoint = camera.e
    t = np.inf
    for i, s in enumerate(surface_list):
        st = s.intersect(viewPoint, scenePoint)
        if st < t:
            t, idx = st, i

    color = np.array([0., 0., 0.]).astype(np.float_)
    if t == np.inf:
        return color

    s = surface_list[idx]
    for light in light_list:
        color += s.light(viewPoint, scenePoint, t, surface_list, light)
    return color

def main():


    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir=np.array([0,0,-1]).astype(np.float_)
    viewUp=np.array([0,1,0]).astype(np.float_)
    viewProjNormal=-1*viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth=1.0
    viewHeight=1.0
    projDistance=1.0
    intensity=np.array([1,1,1]).astype(np.float_)  # how bright the light is.
    #print(np.cross(viewDir, viewUp))


    imgSize=np.array(root.findtext('image').split()).astype(int)
    Width = imgSize[0]
    Height = imgSize[1]

    # input sequence from xml files
    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float_)
        viewDir = np.array(c.findtext('viewDir').split()).astype(np.float_)
        viewProjNormal = np.array(c.findtext('projNormal').split()).astype(np.float_)
        viewUp = np.array(c.findtext('viewUp').split()).astype(np.float_)
        projDistance = c.findtext('projDistance')

        if projDistance != None:
            projDistance = np.array(projDistance.split()).astype(np.float_)
        else:
            projDistance = 1

        viewWidth = np.array(c.findtext('viewWidth').split()).astype(np.float_)
        viewHeight = np.array(c.findtext('viewHeight').split()).astype(np.float_)
    
    myCam = Camera(viewPoint, viewDir, viewProjNormal, viewUp,
                    projDistance, viewWidth, viewHeight)

    shader_list = []
    for c in root.findall('shader'):
        name_s = c.get('name')
        type_s = c.get('type')
        diffuseColor_s = np.array(c.findtext('diffuseColor').split()).astype(np.float_)
        if type_s == 'Phong':
            specularColor_s = np.array(c.findtext('specularColor').split()).astype(np.float_) 
            exponent_s = np.array(c.findtext('exponent').split()).astype(np.float_) 
            shader_list.append(Phong(name_s, type_s, diffuseColor_s, specularColor_s, exponent_s))
        #print('diffuse', diffuseColor_s)

        elif type_s == 'Lambertian':
            shader_list.append(Lambertian(name_s, type_s, diffuseColor_s))

    surface_list = []
    for c in root.findall('surface'):
        type_s = c.get('type')
        shader_s = c.find('shader').get('ref')
        #print('shader in surface', shader_s)
        shader_n = None
        for s in shader_list:
            if s.name == shader_s:
                shader_n = s
                break

        if type_s == 'Sphere':
            radius = np.array(c.findtext('radius').split()).astype(np.float_)
            #print('radius', radius)
            center = np.array(c.findtext('center').split()).astype(np.float_)
            surface_list.append(Sphere(type_s, shader_n, center=center, radius=radius))

        elif type_s == 'Box':
            minPt = np.array(c.findtext('minPt').split()).astype(np.float_)
            maxPt = np.array(c.findtext('maxPt').split()).astype(np.float_)
            surface_list.append(Box(type_s, shader_n, minPt=minPt, maxPt=maxPt))
            #print('minPt, maxPt', minPt, maxPt)

    light_list = []
    for c in root.findall('light'):
        position_l = np.array(c.findtext('position').split()).astype(np.float_)
        intensity_l = np.array(c.findtext('intensity').split()).astype(np.float_)
        light_list.append(Light(position_l, intensity_l))
        


        #print('name', c.get('name'))
        #print('diffuseColor', diffuseColor_c)
    #code.interact(local=dict(globals(), **locals()))  


    #print('Camera ray', myCam.getRay(imgSize[1], imgSize[0], 0))
    
    # Create an empty image
    channels = 3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    #pdb.set_trace() # debuger

    rate = myCam.viewWidth / myCam.viewHeight
    screen = (-1., -1. / rate, 1., 1. / rate)
    d = myCam.projDistance
    vw = myCam.viewWidth
    #d = d / myCam.getNormalizedRate() * rate * d * Width / (Width - vw)
    x = d / Width * vw
    nrate = myCam.getNormalizedRate()
    d = d * rate / nrate 
    d = np.sqrt(d)
    print(rate, d, nrate, x)
    for i, x in enumerate(np.linspace(screen[0], screen[2], Width)):    # -1 ~ 1
        for j, y in enumerate(np.linspace(screen[1], screen[3], Height)):
            s = x * myCam.u + y * myCam.v - d * myCam.w
            ns = normalize(s)

            color = rayTrace(myCam, ns, surface_list, light_list)

            c = Color(color[0], color[1], color[2])
            c.gammaCorrect(2.2)
            img[Height - j - 1][i] = c.toUINT8()
    

    rawimg = Image.fromarray(img, 'RGB')
    rawimg.save(sys.argv[1]+'_output.png')
    
if __name__=="__main__":
    main()
