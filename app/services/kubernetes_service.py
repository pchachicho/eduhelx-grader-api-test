import base64
from kubernetes import client, config
from app.models.user import UserType

class KubernetesService:
    def __init__(self):
        self.api_instance = self.get_v1_client()

    @staticmethod
    def get_v1_client() -> client.CoreV1Api:
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()

        return client.CoreV1Api()
    
    def get_current_namespace(self):
        contexts, current_context = config.list_kube_config_contexts()
        return current_context["context"]["namespace"]

    def create_credential_secret(self, course_name: str, onyen: str, password: str, user_type: UserType):
        current_namespace = self.get_current_namespace()

        secret_name = f"{course_name}-{onyen}-credential-secret"
        secret_data = {
            "onyen": onyen,
            "password": password,
            "user_type": user_type.value
        }
        encoded_secret_data = {
            key: base64.b64encode(value.encode()).decode() for (key, value) in secret_data.items()
        }

        secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(
                name=secret_name,
                namespace=current_namespace
            ),
            type="Opaque",
            data=encoded_secret_data
        )

        self.api_instance.create_namespaced_secret(
            namespace=current_namespace,
            body=secret
        )