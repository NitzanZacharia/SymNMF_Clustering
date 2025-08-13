#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "symnmf.h"

double *datapoints_to_matrix(PyObject *datapoints){
    Py_ssize_t numRows, numCols, i, j;
    double *mat;
    PyObject *inner;
    if ((!PyList_Check(datapoints)) || PyList_Size(datapoints) <= 0) return NULL;
    numRows = PyList_Size(datapoints);
    numCols = PyList_Size(PyList_GetItem(datapoints, 0));
    mat = malloc((size_t)numRows*numCols*sizeof(double));
    if(!mat) return NULL;
    for(i=0; i<numRows; i++){
        inner = PyList_GetItem(datapoints, i);
        if(!PyList_Check(inner)){
            free(mat);
            return NULL;
        }
        for(j=0; j<numCols; j++){
            mat[(i*numCols) + j] = PyFloat_AsDouble(PyList_GetItem(inner, j));
        }
    }
    return mat;
}

PyObject *arr_to_list(const double *arr, int len){
    PyObject *lst, *num;
    int i;
    lst = PyList_New(len);
    if(!lst) return NULL;
    for(i=0; i<len; i++){
        num = PyFloat_FromDouble(arr[i]);
        if(!num){
            Py_XDECREF(lst);
            return NULL;
        }
        PyList_SET_ITEM(lst, i, num);
    }
    return lst;
}

PyObject *matrix_to_lists(const double *mat, int numRows, int numCols){
    PyObject *outer, *inner;
    int i;
    outer = PyList_New(numRows);
    if(!outer) return NULL;
    for(i=0; i<numRows; i++){
        inner = arr_to_list(mat + (i*numCols), numCols);
        if(!inner){
            Py_XDECREF(outer);
            return NULL;
        }
        PyList_SET_ITEM(outer, i, inner);
    }
    return outer;
}

PyObject *shared_work(PyObject *py_datapoints, int option){
    PyObject *py_matrix=NULL;
    double *datapoints, *a_matrix=NULL, *d_matrix=NULL, *w_matrix=NULL;
    int n, d;
    datapoints = datapoints_to_matrix(py_datapoints);
    if(!datapoints) return NULL;
    n = (int)PyList_Size(py_datapoints);
    d = (int)PyList_Size(PyList_GetItem(py_datapoints, 0));
    a_matrix = build_a(datapoints, n, d);
    free(datapoints);
    if(!a_matrix) return NULL;
    /*sym*/
    if(option == 0){
        py_matrix = matrix_to_lists(a_matrix, n, n);
        goto end;
    }
    d_matrix = build_d(a_matrix, n);
    if(!d_matrix) goto end;
    /*ddg*/
    if(option == 1){
        py_matrix = arr_to_list(d_matrix, n);
        goto end;
    }
    w_matrix = build_w(d_matrix, a_matrix, n);
    if(!w_matrix) goto end;
    py_matrix = matrix_to_lists(w_matrix, n, n);
end: if(w_matrix) free(w_matrix);
    if(a_matrix) free(a_matrix);
    if(d_matrix) free(d_matrix);
    return py_matrix;
}

static PyObject* symnmf(PyObject *self, PyObject *args){
    PyObject *py_h, *py_w;
    int n,k;
    if(!PyArg_ParseTuple(args, "OOii", &py_h, &py_w, &n, &k)) return NULL;
}

static PyObject* sym(PyObject *self, PyObject *args){
    PyObject *py_datapoints, *py_matrix;
    if(!PyArg_ParseTuple(args, "O", &py_datapoints)) return NULL;
    py_matrix = shared_work(py_datapoints, 0);
    if(!py_matrix) PyErr_SetString(PyExc_RuntimeError, "An Error Has Occurred.");
    return py_matrix;
}

static PyObject* ddg(PyObject *self, PyObject *args){
    PyObject *py_datapoints, *py_matrix;
    if(!PyArg_ParseTuple(args, "O", &py_datapoints)) return NULL;
    py_matrix = shared_work(py_datapoints, 1);
    if(!py_matrix) PyErr_SetString(PyExc_RuntimeError, "An Error Has Occurred.");
    return py_matrix;
}

static PyObject* norm(PyObject *self, PyObject *args){
    PyObject *py_datapoints, *py_matrix;
    if(!PyArg_ParseTuple(args, "O", &py_datapoints)) return NULL;
    py_matrix = shared_work(py_datapoints, 2);
    if(!py_matrix) PyErr_SetString(PyExc_RuntimeError, "An Error Has Occurred.");
    return py_matrix;
}

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
    },
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