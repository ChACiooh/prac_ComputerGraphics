import glfw
from OpenGL.GL import *
import numpy as np

modelist = ['Q', 'E', 'A', 'D', '1', 'W', 'S']
IdM = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
gComposedM = np.array(IdM)
localZero = np.array([0., 0., 1.])

def initialize():
    global gComposedM, localZero
    gComposedM = np.array(IdM)
    localZero = np.array(IdM[2])

def LocalTransformation(LT):
    translate = np.array(IdM)
    translate[:, 2][:-1] = -localZero[:-1]
    translate2 = np.array(IdM)
    translate2[:, 2][:-1] = localZero[:-1]
    return translate2 @ LT @ translate

def Rotate(degree):
    angle = np.radians(degree)
    rotate = np.array([[np.cos(angle), -np.sin(angle), 0.],
                        [np.sin(angle), np.cos(angle), 0.],
                        [0., 0., 1.]])
    return rotate

def RotateAt(degree):
    return LocalTransformation(Rotate(degree))

def ScaleX(times):
    scale = np.array(IdM)
    scale[0][0] = times
    return scale

def gen_new_matrix(mode):
    newM = np.array(IdM)
    global localZero
    if mode == 'Q':
        newM[0][2] = -0.1
        localZero[:-1] += newM[:,2][:-1]
    elif mode == 'E':
        newM[0][2] = 0.1
        localZero[:-1] += newM[:,2][:-1]
    elif mode == 'A':
        newM = RotateAt(10)
    elif mode == 'D':
        newM = RotateAt(-10)
    elif mode == '1':
        localZero = np.array(IdM[2])
    elif mode == 'W':
        scale = np.array(IdM)
        scale[0][0] = 0.9
        newM = LocalTransformation(scale)
    elif mode == 'S':
        newM = Rotate(10)
    return newM

def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv( (T @ np.array([.0,.5,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.0,.0,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.5,.0,1.]))[:-1] )
    glEnd()


def main():
    # Initialize the library
    if not glfw.init():
        return
    global gComposedM
    # mode input from user
    print('====Please input keword of mode====')
    print('Q | Translate by -0.1 in x direction w.r.t global coordinate')
    print('E | Translate by 0.1 in x direction w.r.t global coordinate')
    print('A | Rotate by 10 degrees counterclockwise w.r.t local coordinate')
    print('D | Rotate by 10 degrees clockwise w.r.t local coordinate')
    print('1 | Reset the triangle with identity matrix')
    print('W | Scale by 0.9 times in x direction w.r.t global coordinate')
    print('S | Rotate by 10 degrees counterclockwise w.r.t global coordinate')
    
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(480,480,"4-1", None, None,)
    if not window:
        glfw.terminate()
        return
    
    # Make the window's context current
    glfw.make_context_current(window)

    # set the number of screen refresh to wait before calling glfw.swap_buffer().
    # if your monitor refresh rate is 60Hz, the while loop is repeated every k/60
    k = 1
    glfw.swap_interval(k)
    mode = '1'

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll events
        glfw.poll_events()
        if mode == '1':
            initialize()
        gComposedM = gen_new_matrix(mode) @ gComposedM        
        
        render(gComposedM)
        glfw.swap_buffers(window)

        # Input for next transformation with terminal
        while True:
            mode = input('mode >')
            if mode in modelist or mode == 'exit':
                break
            else:
                print('please only input with Q, E, A, D, 1, W, S')
        if mode == 'exit':
            break
    
    glfw.terminate()

if __name__ == "__main__":
    main()

print('done.')