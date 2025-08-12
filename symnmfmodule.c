#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "symnmf.h"

static PyObject* symnmf(PyObject *self, PyObject *args){}
static PyObject* sym(PyObject *self, PyObject *args){}
static PyObject* ddg(PyObject *self, PyObject *args){}
static PyObject* norm(PyObject *self, PyObject *args){}

static PyMethodDef symnmfMethods[] = {
   {
        "sym",
        (PyCFunction)sym,
        METH_VARARGS,
        PyDoc_STR()
    },
    {
        "ddg",
        (PyCFunction)ddg,
        METH_VARARGS,
        PyDoc_STR()
    },
    {
        "norm",
        (PyCFunction)norm,
        METH_VARARGS,
        PyDoc_STR()
    },
    {
        "symnmf",
        (PyCFunction)symnmf,
        METH_VARARGS,
        PyDoc_STR()
    }
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef symnmfModule = {
    PyModuleDef_HEAD_INIT,
    "symnmf",                                
    NULL, 
    -1,                                      
    symnmfMethods                            
};

PyMODINIT_FUNC PyInit_symnmf(void) {
    PyObject *m;
    m = PyModule_Create(&symnmfModule);
    if (!m) return NULL;
    return m;
}