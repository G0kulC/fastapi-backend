import os
import fnmatch
import shutil
from setuptools import find_packages, setup, Extension
from setuptools.command.build_py import build_py as build_py_orig

try:
    from Cython.Build import cythonize
except:
    cythonize = None

# https://stackoverflow.com/a/56043918
extensions = [
    Extension("api.*", ["api/**/*.py"], extra_compile_args=["-O3", "-Wall"]),
]

cython_excludes = [
    "api/schemas/*",
    "api/core/dependencies.py",
    "api/migrations/*",
    "api/migrations/versions/*",
    "api/aws/*",
]

with open("requirements.txt") as f:
    requires = f.read().strip().splitlines()


def not_cythonized(tup):
    (package, module, filepath) = tup
    return any(
        fnmatch.fnmatchcase(filepath, pat=pattern) for pattern in cython_excludes
    ) or not any(
        fnmatch.fnmatchcase(filepath, pat=pattern)
        for ext in extensions
        for pattern in ext.sources
    )


class build_py(build_py_orig):
    def find_modules(self):
        modules = super().find_modules()
        return list(filter(not_cythonized, modules))

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return list(filter(not_cythonized, modules))


def __cleanup():
    for root, dirs, files in os.walk("api"):
        for fn in files:
            if os.path.splitext(fn)[1] == ".c":
                fp = os.path.join(root, fn)
                os.remove(fp)
        if os.path.exists(os.path.join(root, "__pycache__")):
            shutil.rmtree(os.path.join(root, "__pycache__"))


setup(
    name="api",
    packages=find_packages(),
    ext_modules=(
        cythonize(
            extensions,
            exclude=cython_excludes,
            compiler_directives={
                "language_level": 3,
                "always_allow_keywords": True,
            },
            build_dir="build",  # needs to be explicitly set, otherwise pollutes package sources
        )
        if cythonize is not None
        else []
    ),
    cmdclass={
        "build_py": build_py,
    },
    include_package_data=True,
    install_requires=requires,
)

__cleanup()

