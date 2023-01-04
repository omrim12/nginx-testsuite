## Nginx webserver tests
### Requirements:
- [openshift-python-wrapper](https://github.com/RedHatQE/openshift-python-wrapper)

### Follow the steps below to run nginx testsuite:
- Clone the repository:
```shell
git clone https://github.com/omrim12/nginx-testsuite.git
```
- Create & activate a virtualenv:
```shell
python -m venv venv && source venv/bin/activate
```
- Install package requirements:
```shell
pip install -r requirements.txt
```
- Export required variables:
```shell
export KUBECONFIG=<path_to_kubeconfig>
export KERBEROS_USER=<username>
```
- Run the tests:
```shell
pytest -sv -m nginx
```
