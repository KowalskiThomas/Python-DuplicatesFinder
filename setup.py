"""
Module utilisé pour la compilation avec Cython.
Pas encore fonctionnel.
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
 
extensions = [
    Extension("Recherche", ["recherche.py"]),
    Extension("Traitement", ["traitement.py"])
]
 
setup(
    cmdclass = {'build_ext':build_ext},
    ext_modules = cythonize(extensions),
)