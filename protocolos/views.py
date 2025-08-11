from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Protocolo, Cliente, Atualizacao
from .forms import ProtocoloForm
import csv
from django.http import HttpResponse

@login_required
def dashboard(request):
    total_protocolos = Protocolo.objects.count()
    protocolos_abertos = Protocolo.objects.filter(status="aberto").count()
    protocolos_em_andamento = Protocolo.objects.filter(status="em_andamento").count()
    protocolos_finalizados = Protocolo.objects.filter(status="finalizado").count()

    ultimos_protocolos = Protocolo.objects.order_by("-data_criacao")[:5]

    context = {
        "total_protocolos": total_protocolos,
        "protocolos_abertos": protocolos_abertos,
        "protocolos_em_andamento": protocolos_em_andamento,
        "protocolos_finalizados": protocolos_finalizados,
        "ultimos_protocolos": ultimos_protocolos,
    }
    return render(request, "protocolos/dashboard.html", context)

@login_required
def novo_protocolo(request):
    if request.method == "POST":
        form = ProtocoloForm(request.POST)
        if form.is_valid():
            protocolo = form.save(commit=False)
            protocolo.usuario_criador = request.user
            protocolo.save()
            form.save_m2m()  # Salva o relacionamento ManyToMany para clientes

            # Adiciona a primeira atualização se houver
            descricao_primeira_atualizacao = request.POST.get("primeira_atualizacao")
            if descricao_primeira_atualizacao:
                Atualizacao.objects.create(
                    protocolo=protocolo,
                    descricao=descricao_primeira_atualizacao,
                    usuario=request.user
                )
            return redirect("dashboard")
    else:
        form = ProtocoloForm()
    return render(request, "protocolos/novo_protocolo.html", {"form": form})

@login_required
def busca_global(request):
    query = request.GET.get("q")
    resultados = []
    if query:
        # Busca em Protocolos
        protocolos_resultados = Protocolo.objects.filter(
            Q(numero__icontains=query) |
            Q(buic_dispositivo__icontains=query) |
            Q(descricao_problema__icontains=query) |
            Q(clientes__nome__icontains=query) |
            Q(clientes__email__icontains=query)
        ).distinct()
        resultados.append({
            "tipo": "Protocolos",
            "itens": protocolos_resultados
        })

        # Busca em Clientes
        clientes_resultados = Cliente.objects.filter(
            Q(nome__icontains=query) |
            Q(email__icontains=query)
        ).distinct()
        resultados.append({
            "tipo": "Clientes",
            "itens": clientes_resultados
        })

    context = {
        "query": query,
        "resultados": resultados
    }
    return render(request, "protocolos/busca_global.html", context)

@login_required
def exportar_protocolos_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=\"protocolos.csv\""

    writer = csv.writer(response)
    writer.writerow(["Número", "Status", "BUIC Dispositivo", "Descrição do Problema", "Usuário Criador", "Data de Criação", "Data de Finalização"])

    protocolos = Protocolo.objects.all().order_by("numero")
    for protocolo in protocolos:
        writer.writerow([
            protocolo.numero,
            protocolo.get_status_display(),
            protocolo.buic_dispositivo,
            protocolo.descricao_problema,
            protocolo.usuario_criador.username,
            protocolo.data_criacao.strftime("%d/%m/%Y %H:%M"),
            protocolo.data_finalizacao.strftime("%d/%m/%Y %H:%M") if protocolo.data_finalizacao else "",
        ])

    return response

