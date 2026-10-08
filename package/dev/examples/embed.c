/* Exercise initialization, stdlib imports and a builtin host module. */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#ifdef __AROS__
#include <dos/dosextens.h>
#include <proto/exec.h>
static APTR saved_window;
static void restore_requesters(void)
{
    ((struct Process *)FindTask(NULL))->pr_WindowPtr = saved_window;
}
#endif

static PyObject *answer(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;
    return PyLong_FromLong(42);
}

static PyMethodDef methods[] = {
    {"answer", answer, METH_NOARGS, "Return the host's answer."},
    {NULL, NULL, 0, NULL}
};
static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, "embedding_host", NULL, -1, methods,
    NULL, NULL, NULL, NULL
};
PyMODINIT_FUNC PyInit_embedding_host(void) { return PyModule_Create(&module); }

int main(int argc, char **argv)
{
    PyConfig config;
    PyStatus status;
    int result;
    if (argc != 2) {
        fprintf(stderr, "Usage: embed /Python\n");
        return 2;
    }
#ifdef __AROS__
    /* Embedding bypasses the interpreter executable's AROS startup hook.
       Missing Unix paths can otherwise become blocking volume requesters. */
    saved_window = ((struct Process *)FindTask(NULL))->pr_WindowPtr;
    if (atexit(restore_requesters) != 0)
        return 7;
    ((struct Process *)FindTask(NULL))->pr_WindowPtr = (APTR)-1;
#endif
    if (PyImport_AppendInittab("embedding_host", PyInit_embedding_host) < 0)
        return 3;
    PyConfig_InitIsolatedConfig(&config);
    config.install_signal_handlers = 0;
    status = PyConfig_SetBytesString(&config, &config.home, argv[1]);
    if (!PyStatus_Exception(status))
        status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        fprintf(stderr, "Initialization failed: %s\n", status.err_msg);
        PyConfig_Clear(&config);
        return 4;
    }
    PyConfig_Clear(&config);
    result = PyRun_SimpleString(
        "import sys, embedding_host, json, decimal, hashlib, ssl, lzma, sqlite3, bz2, zlib\n"
        "assert sys.version_info[:3] == (3, 14, 7)\n"
        "assert embedding_host.answer() == 42\n"
        "assert json.loads('{\"value\":42}')[\"value\"] == 42\n"
        "assert decimal.Decimal('0.1') + decimal.Decimal('0.2') == decimal.Decimal('0.3')\n"
        "assert hashlib.sha256(b'abc').hexdigest() == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'\n"
        "for codec in (lzma, bz2, zlib):\n"
        "    assert codec.decompress(codec.compress(b'embed-test')) == b'embed-test'\n"
        "db = sqlite3.connect(':memory:')\n"
        "assert db.execute('select 42').fetchone()[0] == 42\n"
        "db.close()\n"
        "assert ssl.OPENSSL_VERSION.startswith('OpenSSL 4.0.1')\n"
        "print('EMBED PASS: initialization, host module, stdlib and static dependencies', flush=True)\n");
    if (Py_FinalizeEx() < 0)
        return 5;
    if (result != 0)
        return 6;
    puts("FINALIZE PASS");
    return 0;
}
