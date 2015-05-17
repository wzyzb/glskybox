from os import path, mkdir

from PIL import Image

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class Projector(object):
    DIRECTIONS = {
        'top': (180, 180, 0),
        'bottom': (0, 180, 0),
        'front': (90, 180, 0),
        'back': (90, 180, 180),
        'left': (90, 180, 90),
        'right': (90, 180, 270),
    }

    def __init__(self, size, dest):
        super(Projector, self).__init__()

        self.dest = dest
        self.x, self.y, self.z = 0, 0, 0
        self.w = self.h = size
        self.texture = None

        self.init_gl()


    def load_texture(self, f):
        im = Image.open(f)
        # im = im.resize((4096, 2048), Image.ANTIALIAS)

        ix, iy = im.size
        buf = im.convert("RGB").tostring("raw", "RGB")

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        glTexImage2D(
            GL_TEXTURE_2D, 0, 3, ix, iy, 0,
            GL_RGB, GL_UNSIGNED_BYTE, buf
        )

        self.texture = texture


    def run(self, src):
        if path.isdir(src):
            filelist = [path.join(src, filename) for filename in os.listdir(src) 
                if not filename.startswith('.')]

            map(lambda filename: self.run(filename), filelist)

        elif path.isfile(src):
            self.render(src)

        else:
            raise ValueError('Invalid source file.')

    def render(self, filename):
        self.load_texture(filename)
        prefix = path.splitext(path.basename(filename))[0]
        w, h = self.w, self.h

        if not path.isdir(self.dest):
            mkdir(self.dest)

        directions = Projector.DIRECTIONS
        for name, vec in directions.iteritems():
            self.x, self.y, self.z = vec
            self.draw()
            buf = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)
            image = Image.frombytes(mode="RGB", size=(w, h), data=buf)
            image.save("%s/%s_%s.jpg" % (self.dest, prefix, name))


    def init_gl(self):

        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
        glutInitWindowSize(self.w, self.h)
        glutCreateWindow("glskybox renderer")
        glutHideWindow()

        glClearColor(0., 0., 0., 0.)
        glClearDepth(1.)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, 1., .1, 100.)
        glMatrixMode(GL_MODELVIEW)


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0., 0., 0.)
        glScalef(-1, 1, 1)
        
        glRotatef(self.x, 1., 0., 0.)
        glRotatef(self.y, 0., 1., 0.)
        glRotatef(self.z, 0., 0., 1.)

        glEnable(GL_TEXTURE_2D)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        Q = gluNewQuadric()
        gluQuadricNormals(Q, GL_SMOOTH)
        gluQuadricTexture(Q, GL_TRUE)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        gluSphere(Q, 2.0, 100, 100)

        glDisable(GL_TEXTURE_2D)