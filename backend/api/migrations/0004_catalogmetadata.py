from django.db import migrations, models
from django.utils import timezone


def seed_catalog_metadata(apps, schema_editor):
    catalog_metadata = apps.get_model("api", "CatalogMetadata")
    product = apps.get_model("api", "Product")
    catalog_metadata.objects.get_or_create(
        key="total_products",
        defaults={"value": product.objects.count()},
    )
    catalog_metadata.objects.get_or_create(
        key="last_fetched",
        defaults={"value": timezone.now().isoformat()},
    )


def remove_catalog_metadata(apps, schema_editor):
    catalog_metadata = apps.get_model("api", "CatalogMetadata")
    catalog_metadata.objects.filter(key__in=["total_products", "last_fetched"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_product_api_product_price_b6b1d7_idx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CatalogMetadata",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=100, unique=True)),
                ("value", models.JSONField(blank=True, default=None, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(seed_catalog_metadata, remove_catalog_metadata),
    ]
