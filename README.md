# sgx-nifti
Prototypes to analyze neuroimaging data in trusted hardware (SGX).

The current very small prototype is based on gramine's Python examples. You
may find it useful to refer to it at
https://github.com/gramineproject/gramine/tree/master/CI-Examples/python.

> **Note**: For Debian-based systems, the gramine examples expect Python
packages to be installed under `/usr/lib/python3/dist-packages`. The examples
in this repository try to use packages installed via `pip` instead.


## Prerequisites
> **Warning**: Only tested on Ubuntu (should work on Debian), and with the
out-of-tree (OOT) SGX driver.

To try the "mvp" (minimal viable prototype), you need:

* An SGX enabled machine
* To Install [gramine][gramine]

To perform remote attestation:

* Obtain an **Unlinkable** subscription key (SPID) for [IAS](ias).

**TODO**: minimal instructions on installing gramine


## Quick Demo (without remote attestation)
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

> **Note**: In the above the `RA_CLIENT_SPID` is set to a dummy value, and you
can ignore it for the sake of this brief demo. See the
[Remote Attestation](#remote-attestation) section to see how to perform the
attestation phase.

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

## Remote Attestation
If you haven't done so already, subsribe to [IAS](ias) to get an SPID and
API key.

Set the `RA_CLIENT_SPID` and `IAS_PRIMARY_KEY` enviroment variables:

```
export RA_CLIENT_SPID=<YOUR_SPID>
export IAS_PRIMARY_KEY=<YOUR_IAS_PRIMARY_KEY>
```

<!--
You may alternatively create a `.env` file to store your SPID and API key:

```
RA_CLIENT_SPID=<YOUR_SPID>
IAS_PRIMARY_KEY=<YOUR_IAS_PRIMARY_KEY>
```

Source the `.env` file:

```
source .env
```
-->

### Generate the Quote
Run the following command, making sure to provide your own SPID.

```
make SGX=1 PYTHON=python3.10 VENV_PATH=~/.venvs/nifti \
    RA_CLIENT_SPID=$RA_CLIENT_SPID RA_CLIENT_LINKABLE=0
```

Notice the measurement or mrenclave in the output, e.g.:

```console
Measurement:
    554052c3730934ec0868eea6796f75b9a97d248d029803c35ad78cd0bbb9cd83
gramine-sgx-get-token --output python.token --sig python.sig                                                                            Attributes:
    mr_enclave:  554052c3730934ec0868eea6796f75b9a97d248d029803c35ad78cd0bbb9cd83
    mr_signer:   5d9fd619b25ed0de75ea71d0d211522c80e14d4eb417fa8869babf62656c5b84
    ...
```

Let's set an environemnt variable for the MRENCLAVE so that we can easily
refer to it later when parsing the report from IAS.

```bash
export MRENCLAVE=554052c3730934ec0868eea6796f75b9a97d248d029803c35ad78cd0bbb9cd83
```

Generate a quote:

```
gramine-sgx ./python scripts/sgx-quote.py
```

Notice the `QUOTE base 64` output, e.g.:

```console
QUOTE base 64: 
 AgAAAEsMAAANAA0AAAAAAFOrdeScwC/lZP1RWReIG+hfJ7BJNls6vpHvqy2dOXqEExMCB/+ABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAFVAUsNzCTTsCGjupnlvdbmpfSSNApgDw1rXjNC7uc2DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABdn9YZsl7Q3nXqcdDSEVIsgOFNTrQX+ohpur9iZWxbhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqAIAACjTKbgsgOCw9A4v58WRhDDbuGvbuB4BdDPIVetcyWIlIFSGuLxIDAqukAGYTfvG3xCB5hHTqJkg86/P2TF6NTf7V4wN+PHXB1Csqm3chHBjNdOPRBcDIYyWIrWAhNb17+RafZsGW524lOfyZJUEs6GG0rAe1EK1VmEeqUpDdyWcXo9jTtOHMHh517kF7hSRSnBon2/aO6JdIu2Acc0rEEWI60S8ySolFeLYn825yUW+drMV+Zi++g9y5i7qPBtdJDRaCfHBzZlDAjiTISrabV1lOyw/SkkGofy7WUrND0rdhOD50LsyngJuCglzd5f5Uexo2iFjKrTSAuwFfRZIU+VUWmklmqcLHKhHNZS1mANmZpqGIMghuqe9W2En3csOJOzmpYQaUUEOkGxU7GgBAABeyPrHVEYDJCNc6MNE3bqxeMGNsgMYHt8OOgR7jR/lVNjBs0E47PrMndMqFQ13etccv7/+h4qcyXfsMqRKcKlR9QB1EQT1ha+JcOOiBMx9m5/VceAx/Pj0JgNweEnT22vSaJtAmfANajUc7dIpnjWWnAmZHTrLgbNg8i2rclic9ZNHOdAP1HCx7y8RycJYwITFZW3d40Q2Snhk27aqZLswXho4EZ0jbJESv24oy6x4NYcbiXPQ5FoGF+VUtNg3WxSRfQNOgwI/TGT1g3wZzst7yKaXkYPPDK2VeV8jOAcO62Jd16z+wQ/oaqs2YHWzo4Ldmjr2el5MEqjA+3UysRs7NNuSAItlHsGL67cHOQ5BgYvv4Yxvh1o4wwcYlXiYcbvOlFau4sO3Gct2hwYckReT+R0eXHmboldpl70peG1NCRWJ/+s/Gw+zAt1byzGTZ9zfQOL8hGRY80OmFaAJysg6EP0eyocGkXnsJ73UUDRdHd6lcZduVYAs
```

### Sending the quote to IAS
Here's a simple example of sending out the quote to IAS for verification using Python's
`requests` library:
Copy-paste the quote to send to Intel for verification. In a Python shell:

```python
quote = "AgAAAEsMAAANAA0AAAAAAFOrdeScwC/lZP1RWReIG+hfJ7BJNls6vpHvqy2dOXqEExMCB/+ABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAFVAUsNzCTTsCGjupnlvdbmpfSSNApgDw1rXjNC7uc2DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABdn9YZsl7Q3nXqcdDSEVIsgOFNTrQX+ohpur9iZWxbhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqAIAACjTKbgsgOCw9A4v58WRhDDbuGvbuB4BdDPIVetcyWIlIFSGuLxIDAqukAGYTfvG3xCB5hHTqJkg86/P2TF6NTf7V4wN+PHXB1Csqm3chHBjNdOPRBcDIYyWIrWAhNb17+RafZsGW524lOfyZJUEs6GG0rAe1EK1VmEeqUpDdyWcXo9jTtOHMHh517kF7hSRSnBon2/aO6JdIu2Acc0rEEWI60S8ySolFeLYn825yUW+drMV+Zi++g9y5i7qPBtdJDRaCfHBzZlDAjiTISrabV1lOyw/SkkGofy7WUrND0rdhOD50LsyngJuCglzd5f5Uexo2iFjKrTSAuwFfRZIU+VUWmklmqcLHKhHNZS1mANmZpqGIMghuqe9W2En3csOJOzmpYQaUUEOkGxU7GgBAABeyPrHVEYDJCNc6MNE3bqxeMGNsgMYHt8OOgR7jR/lVNjBs0E47PrMndMqFQ13etccv7/+h4qcyXfsMqRKcKlR9QB1EQT1ha+JcOOiBMx9m5/VceAx/Pj0JgNweEnT22vSaJtAmfANajUc7dIpnjWWnAmZHTrLgbNg8i2rclic9ZNHOdAP1HCx7y8RycJYwITFZW3d40Q2Snhk27aqZLswXho4EZ0jbJESv24oy6x4NYcbiXPQ5FoGF+VUtNg3WxSRfQNOgwI/TGT1g3wZzst7yKaXkYPPDK2VeV8jOAcO62Jd16z+wQ/oaqs2YHWzo4Ldmjr2el5MEqjA+3UysRs7NNuSAItlHsGL67cHOQ5BgYvv4Yxvh1o4wwcYlXiYcbvOlFau4sO3Gct2hwYckReT+R0eXHmboldpl70peG1NCRWJ/+s/Gw+zAt1byzGTZ9zfQOL8hGRY80OmFaAJysg6EP0eyocGkXnsJ73UUDRdHd6lcZduVYAs"
```
```python
json = {"isvEnclaveQuote": quote}
```

Set the request headers. You need your **unlinkable** subscription key from the
[Intel SGX Attestation Service Utilizing Enhanced Privacy ID (EPID)](https://api.portal.trustedservices.intel.com/).

```python
import os

headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': os.environ['IAS_PRIMARY_KEY'],
}
```

Using the `requests` library post the quote to IAS:

```python
import requests

url = 'https://api.trustedservices.intel.com/sgx/dev/attestation/v4/report'

res = requests.post(url, json=json, headers=headers)
```

Check the response status:

```ipython
res.ok
```

Check the response body:

```python
>>> res.json()
{'id': '121855069149404306319130152257933697178',
 'timestamp': '2022-10-06T03:24:59.639030',
 'version': 4,
 'advisoryURL': 'https://security-center.intel.com',
 'advisoryIDs': ['INTEL-SA-00334'],
 'isvEnclaveQuoteStatus': 'SW_HARDENING_NEEDED',
 'isvEnclaveQuoteBody': 'AgAAAEsMAAANAA0AAAAAAFOrdeScwC/lZP1RWReIG+hfJ7BJNls6vpHvqy2dOXqEExMCB/+ABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAFVAUsNzCTTsCGjupnlvdbmpfSSNApgDw1rXjNC7uc2DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABdn9YZsl7Q3nXqcdDSEVIsgOFNTrQX+ohpur9iZWxbhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'}
```

### Verifying the MRENCLAVE, and REPORT DATA
Getting the **MRENCLAVE**, **MRSIGNER** and **REPORT DATA** out of the report
 requires to know the structure of a quote:

```C
typedef struct _quote_t
{
    uint16_t            version;        /* 0   */
    uint16_t            sign_type;      /* 2   */
    sgx_epid_group_id_t epid_group_id;  /* 4   */
    sgx_isv_svn_t       qe_svn;         /* 8   */
    sgx_isv_svn_t       pce_svn;        /* 10  */
    uint32_t            xeid;           /* 12  */
    sgx_basename_t      basename;       /* 16  */
    sgx_report_body_t   report_body;    /* 48  */
    uint32_t            signature_len;  /* 432 */
    uint8_t             signature[];    /* 436 */
} sgx_quote_t;
```

The report body is the structure that contains the MRENCLAVE:

```C
typedef struct _report_body_t
{
    sgx_cpu_svn_t           cpu_svn;        /* (  0) Security Version of the CPU */
    sgx_misc_select_t       misc_select;    /* ( 16) Which fields defined in SSA.MISC */
    uint8_t                 reserved1[SGX_REPORT_BODY_RESERVED1_BYTES];  /* ( 20) */
    sgx_isvext_prod_id_t    isv_ext_prod_id;/* ( 32) ISV assigned Extended Product ID */
    sgx_attributes_t        attributes;     /* ( 48) Any special Capabilities the Enclave possess */
    sgx_measurement_t       mr_enclave;     /* ( 64) The value of the enclave's ENCLAVE measurement */
    uint8_t                 reserved2[SGX_REPORT_BODY_RESERVED2_BYTES];  /* ( 96) */
    sgx_measurement_t       mr_signer;      /* (128) The value of the enclave's SIGNER measurement */
    uint8_t                 reserved3[SGX_REPORT_BODY_RESERVED3_BYTES];  /* (160) */
    sgx_config_id_t         config_id;      /* (192) CONFIGID */
    sgx_prod_id_t           isv_prod_id;    /* (256) Product ID of the Enclave */
    sgx_isv_svn_t           isv_svn;        /* (258) Security Version of the Enclave */
    sgx_config_svn_t        config_svn;     /* (260) CONFIGSVN */
    uint8_t                 reserved4[SGX_REPORT_BODY_RESERVED4_BYTES];  /* (262) */
    sgx_isvfamily_id_t      isv_family_id;  /* (304) ISV assigned Family ID */
    sgx_report_data_t       report_data;    /* (320) Data provided by the user */
} sgx_report_body_t;
```

Extract the report body:

```python
import base64

isv_enclave_quote_body = res.json()['isvEnclaveQuoteBody']
report_body = base64.b64decode(isv_enclave_quote_body)[48:432]
```

Check the **MRENCLAVE**:
Recall that after running the `make` command above there was a measurement
output also known as MRENCLAVE. If you haven't done so, set an environment
variable `MRENCLAVE` to the value that was output after the build command
with `make`, e.g.:

```bash
export MRENCLAVE=554052c3730934ec0868eea6796f75b9a97d248d029803c35ad78cd0bbb9cd83
```

Now, let's compare the expected `MRENCLAVE` with what we have in the report:

```python
>>> report_body[64:96].hex() == os.environ['MRENCLAVE']
True
```

If it is `False`, it means that the attestation phase reported a different
measurement of the code, which would mean that the code that was loaded in
SGX differs from the code that was built.


Extract the **REPORT DATA**:

```python
report_body[320:384].hex()  # report data
```


## TODO
* Encrypt the files before processing them in SGX. Input files should only be
  decrypted within SGX.
* Provide a Dockerfile for easier setup.
* ...

[gramine]: https://gramine.readthedocs.io/en/latest/quickstart.html#install-gramine
[ias]: https://api.portal.trustedservices.intel.com/EPID-attestation
