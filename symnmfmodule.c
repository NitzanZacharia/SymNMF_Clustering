#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* symnmf(PyObject *self, PyObject *args){}
static PyObject* sym(PyObject *self, PyObject *args){}
static PyObject* ddg(PyObject *self, PyObject *args){}
static PyObject* norm(PyObject *self, PyObject *args){}

static PyMethodDef symnmfMethods[] = {
   {
        "sym",
        (PyCFunction)py_sym,
        METH_VARARGS,
        PyDoc_STR("sym(X) -> list[list[float]]\n"
                  "Compute the similarity matrix A from data matrix X (n×m).")
    },
    {
        "ddg",
        (PyCFunction)py_ddg,
        METH_VARARGS,
        PyDoc_STR("ddg(A) -> list[list[float]]\n"
                  "Compute the diagonal degree matrix D where D_ii = sum_j A_ij.")
    }
    {NULL, NULL, 0, NULL}
};