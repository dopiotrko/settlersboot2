from distutils.core import setup
from babel.messages import frontend as babel

setup(name='settlersbot',
      version='1.0',
      py_modules=['settlersbot'],
      cmdclass={'compile_catalog': babel.compile_catalog,
                'extract_messages': babel.extract_messages,
                'init_catalog': babel.init_catalog,
                'update_catalog': babel.update_catalog}
      )
