from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from protocolos.models import Cliente, Protocolo, Atualizacao
from django.utils import timezone

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo para Cliente, Protocolo e Atualizacao.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando a população de dados de exemplo...'))

        # Criar usuários de exemplo
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
            self.stdout.write(self.style.SUCCESS('Usuário admin criado.'))

        try:
            user1 = User.objects.get(username='usuario1')
        except User.DoesNotExist:
            user1 = User.objects.create_user('usuario1', 'usuario1@example.com', 'testpassword')
            self.stdout.write(self.style.SUCCESS('Usuário usuario1 criado.'))

        # Criar clientes de exemplo
        clientes_data = [
            {'nome': 'Empresa A', 'email': 'empresaA@example.com', 'senha': 'senha123'},
            {'nome': 'Cliente B', 'email': 'clienteB@example.com', 'senha': 'senha456'},
            {'nome': 'Organização C', 'email': 'organizacaoC@example.com', 'senha': 'senha789'},
        ]
        clientes = []
        for data in clientes_data:
            cliente, created = Cliente.objects.get_or_create(email=data['email'], defaults=data)
            clientes.append(cliente)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Cliente {cliente.nome} criado.'))
            else:
                self.stdout.write(self.style.WARNING(f'Cliente {cliente.nome} já existe.'))

        # Criar protocolos de exemplo
        protocolos_data = [
            {
                'clientes': [clientes[0]],
                'buic_dispositivo': 'BUIC-001',
                'descricao_problema': 'Problema de conexão com a internet.',
                'usuario_criador': admin_user,
                'status': 'aberto'
            },
            {
                'clientes': [clientes[0], clientes[1]],
                'buic_dispositivo': 'BUIC-002',
                'descricao_problema': 'Falha no sistema de login.',
                'usuario_criador': user1,
                'status': 'em_andamento'
            },
            {
                'clientes': [clientes[2]],
                'buic_dispositivo': 'BUIC-003',
                'descricao_problema': 'Solicitação de nova funcionalidade.',
                'usuario_criador': admin_user,
                'status': 'finalizado',
                'data_finalizacao': timezone.now()
            },
        ]

        for data in protocolos_data:
            # Remover 'status' e 'data_finalizacao' para que o save() do model cuide disso
            status = data.pop('status')
            data_finalizacao = data.pop('data_finalizacao', None)

            clientes_para_protocolo = data.pop("clientes")
            protocolo = Protocolo.objects.create(**data)
            protocolo.clientes.set(clientes_para_protocolo)
            protocolo.status = status
            protocolo.data_finalizacao = data_finalizacao
            protocolo.save()
            self.stdout.write(self.style.SUCCESS(f'Protocolo #{protocolo.numero} criado.'))

        # Criar atualizações de exemplo
        protocolo1 = Protocolo.objects.get(buic_dispositivo='BUIC-001')
        protocolo2 = Protocolo.objects.get(buic_dispositivo='BUIC-002')

        Atualizacao.objects.get_or_create(
            protocolo=protocolo2,
            descricao='Análise inicial do problema.',
            usuario=user1
        )
        Atualizacao.objects.get_or_create(
            protocolo=protocolo2,
            descricao='Identificado a causa raiz do problema.',
            usuario=admin_user
        )
        self.stdout.write(self.style.SUCCESS('Atualizações de exemplo criadas.'))

        self.stdout.write(self.style.SUCCESS('População de dados de exemplo concluída com sucesso!'))


