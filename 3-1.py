import glfw
from OpenGL.GL import *
import numpy as np

GL_PT = 0
while True:
    GL_PT = input('input Key(1~9):')
    if GL_PT not in '1234567890' or len(GL_PT) != 1:
        print('please input in 1~9.')
        continue
    GL_PT = int(GL_PT)
    break

GLs = [GL_POLYGON, GL_POINTS, GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP, GL_TRIANGLES,
        GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN, GL_QUADS, GL_QUAD_STRIP]


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GLs[GL_PT])
    # B, C and D
    for th in np.linspace(0, 360, 13):
        th = np.radians(th)
        glVertex2f(np.cos(th), np.sin(th))
    glEnd()

def main():
    if not glfw.init():
        return
    
    # A
    window = glfw.create_window(480,480,"3-1", None, None,)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)

    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        # E
        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()