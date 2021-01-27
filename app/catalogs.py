import io
import re

from fastapi import APIRouter, Depends

from .mongo import get_mongo, MongoClient
from .settings import settings
from .models import CatalogDescription
from typing import List


def catshtm_catalog_descriptions():
    """
    Parse metadata from catsHTM README and MATLAB files
    """
    from catsHTM import params
    from catsHTM.script import get_CatDir
    from scipy.io import loadmat

    catalogs = []
    if settings.catshtm_dir is None:
        return catalogs

    for line in io.StringIO(
        """
        2MASS (input name: TMASS)
        2MASSxsc (input name: TMASSxsc) - 2MASS extended source catalog
        AKARI (input name: AKARI)
        APASS (input name: APASS) - AAVSO All Sky Photometric Sky Survey (~5.5x10^7 sources)
        Cosmos (input name: Cosmos) - Sources in the Cosmos field
        DECaLS (input name: DECaLS) - DECaLS DR5 release
        FIRST (input name: FIRST) - (~9.5x10^5 sources)
        GAIA/DR1 (input name: GAIADR1) - (~1.1x10^9 sources).
        GAIA/DR2 (input name: GAIADR2) - NEW! (~1.6x10^9 sources)
        GALEX (input name: GALEX) - GALAEX/GR6Plus7 (~1.7x10^8 sources).
        HSC/v2 (input name: HSCv2)- Hubble source catalog
        IPHAS/DR2 (input name: IPHAS)
        NED redshifts (input name: NEDz)
        NVSS (input name: NVSS) - (~1.8x10^6 sources)
        PS1 (input name: PS1) - Pan-STARRS (~2.6x10^9 sources; A cleaned version of the PS1 stack catalog; some missing tiles below declination of zero [being corrected])
        PTFpc (input name: PTFpc) - PTF photometric catalog
        ROSATfsc (input name: ROSATfsc) - ROSAT faint source catalog
        SDSS/DR10 (input name: SDSSDR10)- Primary sources from SDSS/DR10 (last photometric release)
        Skymapper - will be added soon.
        SpecSDSS/DR14 (input name: SpecSDSS) - SDSS spectroscopic catalog
        Spitzer/SAGE (input name SAGE)
        Spitzer/IRAC (input name IRACgc) - Spitzer IRAC galactic center survey
        UCAC4 (input name: UCAC4) - (~1.1x10^8 sources)
        UKIDSS/DR10 (input name: UKIDSS)
        USNOB1 (not yet available)
        VISTA/Viking/DR3 (not yet available)
        VST/ATLAS/DR3 (input name: VSTatlas)
        VST/KiDS/DR3 (input name: VSTkids)
        WISE (input name: WISE) - ~5.6x10^8 sources
        XMM (input name: XMM)- 7.3x10^5 sources 3XMM-DR7 (Rosen et al. 2016; A&A 26, 590)
        """.strip()
    ).readlines():
        if (
            match := re.match(
                r"(?P<name>[\w/]+) \(input name: (?P<key>\w+)\)(\s*-\s*(?P<description>.*))?",
                line.strip(),
            )
        ) :
            name = match.group("key")
            try:
                meta = loadmat(
                    str(
                        settings.catshtm_dir
                        / get_CatDir(name)
                        / (params.ColCelFile % name)
                    )
                )
            except FileNotFoundError:
                continue
            catalogs.append(
                {
                    "name": name,
                    "use": "catsHTM",
                    "description": " -- ".join(
                        [
                            s
                            for s in (match.group("name"), match.group("description"))
                            if s
                        ]
                    ),
                    "columns": [
                        {"name": str(k[0]), "unit": str(u[0]) if len(u) else None}
                        for k, u in zip(
                            meta["ColCell"].flatten(), meta["ColUnits"].flatten()
                        )
                    ],
                }
            )
    return catalogs


def extcats_catalog_descriptions(mongo: MongoClient):
    catalogs = []
    for db in mongo.list_database_names():
        if (
            meta := mongo[db]
            .get_collection("meta")
            .find_one({"_id": "science"}, {"_id": 0})
        ) :
            # use first entry as an example
            src = mongo[db].get_collection("srcs").find_one({}, {"_id": 0, "pos": 0})
            catalogs.append(
                {
                    "name": db,
                    "use": "extcats",
                    "columns": [{"name": k, "unit": None} for k in src.keys()],
                    **meta,
                }
            )
    return catalogs


router = APIRouter()


@router.get("/", response_model=List[CatalogDescription])
def list_catalogs(mongo=Depends(get_mongo)) -> List[CatalogDescription]:
    return extcats_catalog_descriptions(mongo) + catshtm_catalog_descriptions()
