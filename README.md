# sgx-nifti
Prototypes to analyze neuroimaging data in trusted hardware (SGX).

The current very small prototype is based on gramine's Python examples. You
may find it useful to refer to it at
https://github.com/gramineproject/gramine/tree/master/CI-Examples/python.

> **Note**: For Debian-based systems, the gramine examples expect Python
packages to be installed under `/usr/lib/python3/dist-packages`. The examples
in this repository try to use packages installed via `pip` instead.


## Prerequisites
Only tested on Ubuntu. (Should work on Debian.)

To try the "mvp" (minimal viable prototype), you need an SGX enabled machine,
and to install gramine.

**TODO**: minimal instructions on installing gramine

## Quick Demo
0. Clone this repository.

1. Create a virual environment, e.g.:

```
python3.10 -m venv ~/.venvs/nifti
```

2. Install `dicom2nifti` in the virtual environment, e.g.:

```
source ~/.venvs/nifti/bin/activate \
    && pip install dicom2nifti \
    && deactivate
```

3. From the root of this repo, copy the `data` directory under `/opt` and give
   set file permissions to your user, e.g.:

```
chown -R `id -un`:`id -gn` /opt/data
```

4. From the `mvp` directory, generate the `python.manifest.sgx` file:
```
cd mvp
```
```
make SGX=1 PYTHON=python3.10 VENV_PATH=~/.venvs/nifti \
    RA_CLIENT_SPID=12345678901234567890123456789012 RA_CLIENT_LINKABLE=0
```

5. Convert the dicom images to nifti:

```
gramine-sgx ./python scripts/test-dicom2nifti.py
```

6. Check that the output file is there:

```
ls -l /opt/data/out/nifti/
```

7. Slice a nifti image:

```
gramine-sgx ./python scripts/test-nibabel.py
```

8. Check the output:
```
ls -l /opt/data/out/nifti/
```

## TODO
* Add instructions on how to get the quote and do the remote attestation.
* Encrypt the files before processing them in SGX. iInput files should only be
decrypted within SGX.
* ...
