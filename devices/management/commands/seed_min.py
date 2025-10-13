from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random

from devices.models import Organization, Zone, Category, Device, Measurement
# Si tienes Alert, puedes importarlo y sembrar algunas también:
# from devices.models import Alert

class Command(BaseCommand):
    help = "Crea datos mínimos de ejemplo para probar la app (orgs, zones, categories, devices, measurements)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("⏳ Sembrando datos de ejemplo..."))

        # --- 1) Organizations ---
        org_a, _ = Organization.objects.get_or_create(name="Org Alpha")
        org_b, _ = Organization.objects.get_or_create(name="Org Beta")

        # --- 2) Zones (por org) ---
        zonas_a = [
            Zone.objects.get_or_create(name="Planta 1", organization=org_a)[0],
            Zone.objects.get_or_create(name="Planta 2", organization=org_a)[0],
        ]
        zonas_b = [
            Zone.objects.get_or_create(name="Edificio A", organization=org_b)[0],
            Zone.objects.get_or_create(name="Edificio B", organization=org_b)[0],
        ]

        # --- 3) Categories (por org) ---
        cat_luz_a   = Category.objects.get_or_create(name="Iluminación",   organization=org_a)[0]
        cat_clima_a  = Category.objects.get_or_create(name="Climatización", organization=org_a)[0]
        cat_luz_b   = Category.objects.get_or_create(name="Iluminación",   organization=org_b)[0]
        cat_clima_b  = Category.objects.get_or_create(name="Climatización", organization=org_b)[0]

        # --- 4) Devices ---
        def mk_device(name, org, zone, category, max_cons=100):
            dev, _ = Device.objects.get_or_create(
                name=name,
                defaults={
                    "organization": org,
                    "zone": zone,
                    "category": category,
                    "maximum_consumption": Decimal(max_cons),
                    # Ajusta si en tu modelo 'status' es otra cosa (ej. booleano)
                    "status": "ACTIVE",
                },
            )
            # sincroniza por si ya existía
            dev.organization = org
            dev.zone = zone
            dev.category = category
            dev.maximum_consumption = Decimal(max_cons)
            dev.status = getattr(dev, "status", "ACTIVE")
            dev.save()
            return dev

        devs_a = [
            mk_device("Lampara-001", org_a, zonas_a[0], cat_luz_a,   80),
            mk_device("Aire-001",    org_a, zonas_a[1], cat_clima_a, 300),
            mk_device("Lampara-002", org_a, zonas_a[0], cat_luz_a,   80),
        ]
        devs_b = [
            mk_device("Lampara-101", org_b, zonas_b[0], cat_luz_b,   80),
            mk_device("Aire-101",    org_b, zonas_b[1], cat_clima_b, 300),
        ]

        # --- 5) Measurements ---
        # Detecta dinámicamente cómo se llama el campo de fecha/tiempo
        m_fields = [f.name for f in Measurement._meta.get_fields()]
        ts_field = None
        for cand in ("date", "created_at", "timestamp"):
            if cand in m_fields:
                ts_field = cand
                break

        def mk_measurements(devs, org, n=12):
            for _ in range(n):
                d = random.choice(devs)
                # consumo aleatorio (hasta 90% del máximo)
                val = round(random.uniform(1.0, float(d.maximum_consumption) * 0.9), 2)
                extra = {}
                if ts_field:
                    extra[ts_field] = timezone.now() - timezone.timedelta(hours=random.randint(0, 72))
                Measurement.objects.create(
                    device=d,
                    organization=org,
                    consumption=Decimal(str(val)),
                    **extra
                )

        mk_measurements(devs_a, org_a, n=16)
        mk_measurements(devs_b, org_b, n=12)

        # --- 6) (Opcional) Alerts ---
        # if 'Alert' in globals():
        #     for d in devs_a + devs_b:
        #         Alert.objects.get_or_create(
        #             device=d, organization=d.organization,
        #             message=f"Alerta de prueba en {d.name}",
        #             severity=random.choice(["LOW","MEDIUM","HIGH"])
        #         )

        self.stdout.write(self.style.SUCCESS("✅ Seed mínima creada con éxito."))