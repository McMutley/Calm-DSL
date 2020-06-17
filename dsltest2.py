
#BluePrint File

from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint


def main():
  print(None)

if __name__ == '__main__':
  main()



#Credentials
from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint
from calm.dsl.builtins import read_local_file, basic_cred

CENTOS_PASSWD = read_local_file('centos')
CENTOS_CRED = basic_cred('centos', CENTOS_PASSWD, name='CENTOS_CRED', default=True)

def main():
  print(None)

if __name__ == '__main__':
  main()



#Define VM Resource Object
from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint
from calm.dsl.builtins import read_local_file, basic_cred
from calm.dsl.builtins import vm_disk_package, AhvVmResources, AhvVmDisk, AhvVmNic, AhvVmGC, AhvVm

CENTOS_PASSWD = read_local_file('centos')
CENTOS_CRED = basic_cred('centos', CENTOS_PASSWD, name='CENTOS_CRED', default=True)

CENTOS_IMAGE_SOURCE = 'https://cloud.centos.org/centos/8/x86_64/images/CentOS-8-ec2-8.1.1911-20200113.3.x86_64.qcow2'
CentosPackage = vm_disk_package( name='centos_disk',
                               config={'image': {'source': CENTOS_IMAGE_SOURCE}})

class CentosVmResources(AhvVmResources):
  memory = 4
  vCPUs = 2
  cores_per_vCPU = 1
  disks = [AhvVmDisk.Disk.Scsi.cloneFromVMDiskPackage(CentosPackage, bootable=True)]
  nics = [AhvVmNic.DirectNic.ingress("dnd-demo")]
  guest_customization = AhvVmGC.CloudInit(
    config={
        'password': CENTOS_PASSWD,
        'ssh_pwauth': True,
        'chpasswd': { 'expire': False }
    })

class CentosVm(AhvVm):
  resources = CentosVmResources


def main():
  print(None)

if __name__ == '__main__':
  main()


#Create Deployment Classes
from calm.dsl.builtins import action, CalmTask

class ApachePHP(SimpleDeployment):
    provider_spec = CentosVm
    os_type = 'Linux'
    min_replicas = '@@{COUNT}@@'

    @action
    def __install__(self):
        CalmTask.Exec.ssh(name='install_apache', filename='scripts/Apache_install.sh')

class HAProxy(SimpleDeployment):
    provider_spec = CentosVm
    os_type = 'Linux'

    @action
    def __install__(self):
        CalmTask.Exec.ssh(name='install_haproxy', filename='scripts/haproxy_install.sh')

class MySQL(SimpleDeployment):
    provider_spec = CentosVm
    os_type = 'Linux'

    @action
    def __install__(self):
        CalmTask.Exec.ssh(name='install_mysql', filename='scripts/mysql_install.sh')


#Define Blueprint Class
from calm.dsl.builtins import CalmVariable

class LAMPBlueprint(SimpleBlueprint):
    credentials = [CENTOS_CRED]
    deployments = [ApachePHP, HAProxy, MySQL]

    MYSQL_PASSWORD = CalmVariable.Simple.Secret('MYSQL_PASSWORD', label='MySQL root password', runtime=True)
    COUNT = CalmVariable.WithOptions.Predefined.string(['1', '2', '3'], default='1', name='COUNT',
                                                        label='Apache Count', runtime=True)


