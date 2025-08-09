from setuptools import Extension, setup
import numpy as np

module = Extension(
    "symnmf",
    sources=["symnmfmodule.c", "symnmf.c"], 
    include_dirs=[np.get_include()]          
)

setup(
    name="symnmf",
    version="1.0",
    description="A Python wrapper for the Symmetric NMF algorithm",
    ext_modules=[module]
)
