from setuptools import Extension, setup

module = Extension(
    "symnmf",
    sources=["symnmfmodule.c", "symnmf.c"]       
)

setup(
    name="symnmf",
    version="1.0",
    description="A Python wrapper for the Symmetric NMF algorithm",
    ext_modules=[module]
)
