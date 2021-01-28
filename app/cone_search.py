import math
from functools import singledispatch
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table
from catsHTM import cone_search
from extcats.catquery_utils import get_closest, get_distances
from fastapi import APIRouter

from .models import (
    CatalogItem,
    CatsHTMQueryItem,
    ConeSearchRequest,
    ExtcatsQueryItem,
)
from .mongo import get_catq
from .settings import settings

if TYPE_CHECKING:
    from astropy.table.row import Row


@singledispatch
def search_any_item(item, coord: SkyCoord) -> bool:
    raise NotImplementedError
    return False


@search_any_item.register  # type: ignore[no-redef]
def _(item: ExtcatsQueryItem, coord: SkyCoord) -> bool:
    # sic
    return get_catq(item.name).binaryserach(coord.ra.deg, coord.dec.deg, item.rs_arcsec)


@search_any_item.register  # type: ignore[no-redef]
def _(item: CatsHTMQueryItem, coord: SkyCoord) -> bool:
    srcs, colnames, colunits = cone_search(
        item.name,
        coord.ra.rad,
        coord.dec.rad,
        item.rs_arcsec,
        catalogs_dir=str(settings.catshtm_dir),
    )
    return len(srcs) > 0


def sanitize_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, (tuple, list)):
        return [sanitize_json(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj


def table_to_json(table: Optional["Table"]) -> Optional[List[Dict[str, Any]]]:
    if table is None:
        return None
    keys = table.keys()
    return [
        {k: sanitize_json(v) for k, v in zip(keys, np.asarray(row).tolist())}
        for row in table.iterrows()
    ]


def row_to_json(row: Optional["Row"]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    keys = row.table.keys()
    return {k: sanitize_json(v) for k, v in zip(keys, np.asarray(row).tolist())}


@singledispatch
def search_nearest_item(item, coord: SkyCoord) -> Optional[CatalogItem]:
    raise NotImplementedError
    return False


@search_nearest_item.register  # type: ignore[no-redef]
def _(item: ExtcatsQueryItem, coord: SkyCoord) -> Optional[CatalogItem]:  # type: ignore[no-redef]
    projection = {"_id": 0, "pos": 0}
    if item.keys_to_append:
        projection.update({k: 1 for k in item.keys_to_append})
    item, dist = get_catq(item.name).findclosest(
        coord.ra.deg, coord.dec.deg, item.rs_arcsec, projection=projection,
    )
    if item:
        return CatalogItem(body=row_to_json(item), dist_arcsec=dist)
    else:
        return None


@search_nearest_item.register  # type: ignore[no-redef]
def _(item: CatsHTMQueryItem, coord: SkyCoord) -> Optional[CatalogItem]:  # type: ignore[no-redef]
    srcs, colnames, colunits = cone_search(
        item.name,
        coord.ra.rad,
        coord.dec.rad,
        item.rs_arcsec,
        catalogs_dir=str(settings.catshtm_dir),
    )
    if not len(srcs):
        return None
    srcs_tab = Table(np.asarray(srcs), names=colnames)
    srcs_tab["ra"] = np.degrees(srcs_tab[colnames[0]])
    srcs_tab["dec"] = np.degrees(srcs_tab[colnames[1]])
    row, dist = get_closest(coord.ra.degree, coord.dec.degree, srcs_tab, "ra", "dec",)
    keys = set(item.keys_to_append or [])
    return CatalogItem(body=row_to_json(row), dist_arcsec=dist)


@singledispatch
def search_all_item(item, coord: SkyCoord) -> Optional[List[CatalogItem]]:
    raise NotImplementedError
    return None


@search_all_item.register  # type: ignore[no-redef]
def _(item: ExtcatsQueryItem, coord: SkyCoord) -> Optional[List[CatalogItem]]:
    projection = {"_id": 0, "pos": 0}
    if item.keys_to_append:
        projection = {k: 1 for k in item.keys_to_append}
    srcs_tab = get_catq(item.name).findwithin(
        coord.ra.deg, coord.dec.deg, item.rs_arcsec, projection=projection
    )
    if srcs_tab:
        dists = get_distances(coord.ra.degree, coord.dec.degree, srcs_tab, "ra", "dec",)
        rows = table_to_json(srcs_tab)
        return [
            CatalogItem(body=row, dist_arcsec=dist) for row, dist in zip(rows, dists)
        ]
    else:
        return None


@search_all_item.register  # type: ignore[no-redef]
def _(item: CatsHTMQueryItem, coord: SkyCoord) -> Optional[List[CatalogItem]]:
    srcs, colnames, colunits = cone_search(
        item.name,
        coord.ra.rad,
        coord.dec.rad,
        item.rs_arcsec,
        catalogs_dir=str(settings.catshtm_dir),
    )
    if not len(srcs):
        return None
    srcs_tab = Table(np.asarray(srcs), names=colnames)
    srcs_tab["ra"] = np.degrees(srcs_tab[colnames[0]])
    srcs_tab["dec"] = np.degrees(srcs_tab[colnames[1]])
    dists = get_distances(coord.ra.degree, coord.dec.degree, srcs_tab, "ra", "dec",)
    rows = table_to_json(srcs_tab)
    return [CatalogItem(body=row, dist_arcsec=dist,) for row, dist in zip(rows, dists)]


router = APIRouter()


@router.post("/any", response_model=List[bool])
def search_any(request: ConeSearchRequest) -> List[bool]:
    """
    Are there sources in the search radius?
    """
    coord = SkyCoord(request.ra_deg, request.dec_deg, unit="deg")
    return [search_any_item(item, coord) for item in request.catalogs]


@router.post("/nearest", response_model=List[Optional[CatalogItem]])
def search_nearest(request: ConeSearchRequest) -> List[Optional[CatalogItem]]:
    """
    Find nearest source in search radius
    """
    coord = SkyCoord(request.ra_deg, request.dec_deg, unit="deg")
    return [search_nearest_item(item, coord) for item in request.catalogs]


@router.post("/all", response_model=List[Optional[List[CatalogItem]]])
def search_all(request: ConeSearchRequest) -> List[Optional[List[CatalogItem]]]:
    """
    Find all sources in the search radius
    """
    coord = SkyCoord(request.ra_deg, request.dec_deg, unit="deg")
    return [search_all_item(item, coord) for item in request.catalogs]
