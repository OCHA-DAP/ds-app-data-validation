import ocha_stratus as stratus

from constants import STAGE


def load_codab_from_blob(iso3: str, admin_level: int = 0):
    iso3 = iso3.lower()
    blob_name = f"{iso3.lower()}_shp.zip"
    shapefile = f"{iso3}_adm{admin_level}.shp"
    gdf = stratus.load_shp_from_blob(
        blob_name=blob_name,
        shapefile=shapefile,
        stage=STAGE,
        container_name="polygon",
    )
    return gdf
