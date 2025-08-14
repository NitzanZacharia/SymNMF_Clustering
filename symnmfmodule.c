#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "symnmf.h"

static double *pyobj_to_matrix(PyObject *py_mat, Py_ssize_t numRows, Py_ssize_t numCols){
    double *mat;
    PyObject *inner;
    int i, j;
    mat = malloc((size_t)numRows*numCols*sizeof(double));
    if(!mat) return NULL;
    for(i=0; i<numRows; i++){
        inner = PyList_GetItem(py_mat, i);
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

static double *datapoints_to_matrix(PyObject *datapoints){
    Py_ssize_t numRows, numCols;
    double *mat;
    if ((!PyList_Check(datapoints)) || PyList_Size(datapoints) <= 0) return NULL;
    numRows = PyList_Size(datapoints);
    numCols = PyList_Size(PyList_GetItem(datapoints, 0));
    mat = pyobj_to_matrix(datapoints, numRows, numCols);
    return mat;
}

static PyObject *arr_to_list(const double *arr, int len){
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

static PyObject *matrix_to_lists(const double *mat, int numRows, int numCols){
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

static PyObject *shared_work(PyObject *py_datapoints, int option){
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
    PyObject *py_h, *py_w, *py_matrix=NULL;
    int n,k;
    double *h_matrix=NULL, *w_matrix=NULL, *final_h=NULL;
    if(!PyArg_ParseTuple(args, "OOii", &py_h, &py_w, &n, &k)) return NULL;
    if((!PyList_Check(py_h)) || (!PyList_Check(py_w))){
        PyErr_SetString(PyExc_RuntimeError, "An Error Has Occurred.");
        return NULL;
    }
    h_matrix = pyobj_to_matrix(py_h, n, k);
    w_matrix = pyobj_to_matrix(py_w, n, n);
    if((!h_matrix) || (!w_matrix)){
        PyErr_SetString(PyExc_RuntimeError, "An Error Has Occurred.");
        goto end;
    }
    final_h = converge_h(h_matrix, w_matrix, n, k);
    if(!final_h){
        PyErr_SetString(PyExc_RuntimeError, "An Error Has Occurred.");
        goto end;
    }
    py_matrix = matrix_to_lists(final_h, n, k);
    if(!py_matrix) PyErr_SetString(PyExc_RuntimeError, "An Error Has Occurred.");
end: free(w_matrix);
    free(final_h);
    return py_matrix;
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