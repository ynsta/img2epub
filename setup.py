from distutils.core import setup

from i2e import config

if __name__ == '__main__':
    setup(name         = 'Img2Epub',
          version      = config.VERSION,
          description  = 'Convert images into epub documents',
          author       = config.AUTHOR,
          author_email = config.AUTHOR_EMAIL,
          url          = config.URL,
          scripts      = ['img2epub.py',
                          'img2epubgui.py',
                          'img2epubgui.pyw'],
          packages     = ['i2e'])
