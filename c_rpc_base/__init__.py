"""Creates Client for rpc_server. """
import docker

CLIENT = docker.APIClient(base_url='unix://var/run/docker.sock')
