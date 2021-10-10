from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS
from .tasks import provision_service, calculate_inventory, start_vm, stop_vm, reboot_vm, reset_vm, shutdown_vm

from rest_framework.decorators import action
from .serializers import \
    PlanSerializer, \
    ServiceSerializer, \
    IPPoolSerializer, \
    ServicePlanSerializer, \
    TemplateSerializer, \
    ServiceNetworkSerializer, \
    ConfigSettingsSerializer, \
    IPSerializer, \
    NewServiceSerializer, \
    OrderNewServiceSerializer, \
    VMNodeSerializer, \
    BillingTypeSerializer, \
    InventorySerializer, \
    BlestaBackendSerializer, \
    DomainSerializer, \
    NodeDiskSerializer

from .models import \
    IPPool, \
    IP, \
    Plan, \
    Service, \
    ServicePlan, \
    Template, \
    ServiceNetwork, \
    Config, \
    VMNode, \
    BillingType, \
    Inventory, \
    BlestaBackend, \
    Domain, \
    NodeDisk


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and
            request.method in SAFE_METHODS
        )


class FormModelViewSet(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "form":
            if "pk" not in kwargs:
                serializer = self.get_serializer()
                return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def get_renderer_context(self):
        context = super().get_renderer_context()
        if "style" not in context:
            context['style'] = {}
        context['style']['template_pack'] = 'drf_horizontal'
        return context


class DomainViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Domain.objects.order_by('pk')
    serializer_class = DomainSerializer


class ConfigSettingsViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Config.objects.order_by('pk')
    serializer_class = ConfigSettingsSerializer


class NodeDiskViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = NodeDisk.objects.order_by('pk')
    serializer_class = NodeDiskSerializer


class BlestaBackendViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = BlestaBackend.objects.order_by('pk')
    serializer_class = BlestaBackendSerializer


class VMNodeViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = VMNode.objects.order_by('pk')
    serializer_class = VMNodeSerializer


class BillingTypeViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = BillingType.objects.order_by('pk')
    serializer_class = BillingTypeSerializer


class ServiceNetworkViewSet(FormModelViewSet):
    permission_classes = [ReadOnly]
    queryset = ServiceNetwork.objects.order_by('pk')
    serializer_class = ServiceNetworkSerializer


class TemplateViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Template.objects.order_by('pk')
    serializer_class = TemplateSerializer


class ServicePlanViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = ServicePlan.objects.order_by('pk')
    serializer_class = ServicePlanSerializer


class IPViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = IP.objects.order_by('pk')
    serializer_class = IPSerializer


class IPPoolViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = IPPool.objects.order_by('pk')
    serializer_class = IPPoolSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            used_ips = IP.objects.filter(pool=instance, owner__isnull=False).count()
            if used_ips > 0:
                return Response(data={'message': "IPs in pool are currently in use"},
                                status=status.HTTP_400_BAD_REQUEST)
        return super(IPPoolViewSet, self).destroy(request, *args, **kwargs)


class PlanViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Plan.objects.order_by('pk')
    serializer_class = PlanSerializer


class InventoryViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Inventory.objects.order_by('pk')
    serializer_class = InventorySerializer

    @action(detail=False)
    def calculate(self, request):
        task = calculate_inventory.delay()
        return Response({"task_id": task.id}, status=202)


class ServiceViewSet(FormModelViewSet):
    permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = ServiceSerializer

    admin_serializer_classes = {
        'list': NewServiceSerializer,
    }
    client_serializer_classes = {
        'list': OrderNewServiceSerializer,
        'retrieve': ServiceSerializer
    }
    default_serializer_class = serializer_class

    @action(detail=True)
    def start(self, request, pk=None):
        task = start_vm.delay(pk)
        return Response({"task_id": task.id}, status=202)

    @action(detail=True)
    def shutdown(self, request, pk=None):
        task = shutdown_vm.delay(pk)
        return Response({"task_id": task.id}, status=202)

    @action(detail=True)
    def reset(self, request, pk=None):
        task = reset_vm.delay(pk)
        return Response({"task_id": task.id}, status=202)

    @action(detail=True)
    def stop(self, request, pk=None):
        task = stop_vm.delay(pk)
        return Response({"task_id": task.id}, status=202)

    @action(detail=True)
    def reboot(self, request, pk=None):
        task = reboot_vm.delay(pk)
        return Response({"task_id": task.id}, status=202)

    @action(detail=True)
    def provision(self, request, pk=None):
        task = provision_service.delay(pk, password='default')
        return Response({"task_id": task.id}, status=202)

    @action(detail=True)
    def console_cookie(self, request, pk=None):
        try:
            service_id = pk
        except KeyError:
            raise
        else:
            service = Service.objects.get(id=pk)
            proxmox_user = f'inveterate{service.owner_id}'
            password = ''.join(
                random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation) for _ in
                range(10))
            proxmox = ProxmoxAPI(service.node.host, user=service.node.user, token_name='inveterate',
                                 token_value=service.node.key,
                                 verify_ssl=False, port=8006)

            try:
                proxmox.access.users.post(userid=f"{proxmox_user}@pve", password=password)
            except ResourceException as e:
                if "already exists" in str(e):
                    proxmox.access.users(f"{proxmox_user}@pve").delete()
                    proxmox.access.users.post(userid=f"{proxmox_user}@pve", password=password)
            proxmox.access.acl.put(path=f"/vms/{service.machine_id}", roles=["PVEVMConsole"],
                                   users=[f"{proxmox_user}@pve"])

            proxmox = ProxmoxAPI(service.node.host, user=f'{proxmox_user}@pve', password=password, verify_ssl=False,
                                 port=8006)
            tokens = proxmox.get_tokens()
            response = Response(
                {"username": f"{proxmox_user}@pve", "cookie": tokens[0], "token": tokens[1], "type": "kvm", "node": service.node.name,
                 "vmid": service.machine_id})
        return response

    def get_queryset(self):
        if self.request.user.is_staff:
            return Service.objects.all().exclude(status='destroyed').order_by('pk')
        return Service.objects.filter(owner=self.request.user).exclude(status='destroyed').order_by('pk')

    def get_serializer_class(self):
        if self.request.accepted_renderer.format == "form":
            if self.request.user.is_staff:
                serializer_classes = self.admin_serializer_classes
            else:
                serializer_classes = self.client_serializer_classes
            return serializer_classes.get(self.action, self.default_serializer_class)
        else:
            return self.default_serializer_class