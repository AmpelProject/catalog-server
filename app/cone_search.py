from functools import singledispatch
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table
from catsHTM import cone_search
from extcats.catquery_utils import get_closest, get_distances
from fastapi import APIRouter

from .extcats import get_catq
from .models import (
    CatalogItem,
    CatsHTMQueryItem,
    ConeSearchRequest,
    ExtcatsQueryItem,
)
from .settings import settings

if TYPE_CHECKING:
    from astropy.table.row import Row

@singledispatch
def search_any_item(item, coord: SkyCoord) -> bool:
    raise NotImplementedError
    return False


@search_any_item.register
def _(item: ExtcatsQueryItem, coord: SkyCoord) -> bool:
    # sic
    return get_catq(item.name).binaryserach(coord.ra.deg, coord.dec.deg, item.rs_arcsec)


@search_any_item.register
def _(item: CatsHTMQueryItem, coord: SkyCoord) -> bool:
    srcs, colnames, colunits = cone_search(
        item.name,
        coord.ra.rad,
        coord.dec.rad,
        item.rs_arcsec,
        catalogs_dir=str(settings.catshtm_dir),
    )
    return len(srcs) > 0


def table_to_json(table: Optional["Table"]) -> Optional[List[Dict[str, Any]]]:
    if table is None:
        return None
    keys = table.keys()
    return [{k: v for k, v in zip(keys, row) if k != "_id"} for row in table.iterrows()]


def row_to_json(row: Optional["Row"]) -> Dict[str, Any]:
    if row is None:
        return None
    keys = row.table.keys()
    return {k: v for k, v in zip(keys, row) if k != "_id"}


@singledispatch
def search_nearest_item(item, coord: SkyCoord) -> Optional[CatalogItem]:
    raise NotImplementedError
    return False


@search_nearest_item.register
def _(item: ExtcatsQueryItem, coord: SkyCoord) -> Optional[CatalogItem]:
    # FIXME: add projection
    # sic
    item, dist = get_catq(item.name).findclosest(
        coord.ra.deg, coord.dec.deg, item.rs_arcsec
    )
    if item:
        return CatalogItem(body=row_to_json(item), dist_arcsec=dist)
    else:
        return None


@search_nearest_item.register
def _(item: CatsHTMQueryItem, coord: SkyCoord) -> Optional[CatalogItem]:
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
    return CatalogItem(
        body={k: v for k, v in zip(srcs_tab.keys(), row) if k in keys}, dist_arcsec=dist
    )


@singledispatch
def search_all_item(item, coord: SkyCoord) -> Optional[List[CatalogItem]]:
    raise NotImplementedError
    return None


@search_all_item.register
def _(item: ExtcatsQueryItem, coord: SkyCoord) -> Optional[List[CatalogItem]]:
    # FIXME: add projection here
    
    projection = {"_id": 0, "pos": 0}
    if item.keys_to_append:
        projection.update({k: 1 for k in item.keys_to_append})
    srcs_tab = get_catq(item.name).findwithin(
        coord.ra.deg, coord.dec.deg, item.rs_arcsec, projection=projection
    )
    if srcs_tab:
        dists = get_distances(coord.ra.degree, coord.dec.degree, srcs_tab, "ra", "dec",)
        return [
            CatalogItem(
                body={k: v for k, v in zip(srcs_tab.keys(), row)}, dist_arcsec=dist
            )
            for row, dist in zip(srcs_tab.iterrows(), dists)
        ]
    else:
        return None


@search_all_item.register
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
    keys = set(item.keys_to_append or [])
    return [
        CatalogItem(
            body={k: v for k, v in zip(srcs_tab.keys(), row) if k in keys},
            dist_arcsec=dist,
        )
        for row, dist in zip(srcs_tab.iterrows(), dists)
    ]

router = APIRouter()

@router.post("/any")
def search_any(request: ConeSearchRequest) -> List[bool]:
    """
    Are there sources in the search radius?
    """
    coord = SkyCoord(request.ra_deg, request.dec_deg, unit="deg")
    return [search_any_item(item, coord) for item in request.catalogs]


@router.post("/nearest")
def search_nearest(request: ConeSearchRequest) -> Optional[CatalogItem]:
    """
    Find nearest source in search radius
    """
    coord = SkyCoord(request.ra_deg, request.dec_deg, unit="deg")
    return [search_nearest_item(item, coord) for item in request.catalogs]


@router.post("/all")
def search_all(request: ConeSearchRequest) -> List[Optional[List[CatalogItem]]]:
    """
    Find all sources in the search radius
    """
    coord = SkyCoord(request.ra_deg, request.dec_deg, unit="deg")
    return [search_all_item(item, coord) for item in request.catalogs]
