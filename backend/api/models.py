from pydantic import BaseModel
from typing import Optional


class Location(BaseModel):
    name: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class Contribution(BaseModel):
    id: str
    albumId: str
    contributor: str
    date: str
    location: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    pageNumber: Optional[int] = None
    scanUrl: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    sourceUrl: Optional[str] = None


class AlbumSummary(BaseModel):
    id: str
    title: str
    owner: str
    year: int
    location: Location
    country: str


class AlbumDetail(AlbumSummary):
    description: Optional[str] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    dimension: Optional[str] = None
    scans: list[str] = []
    contributions: list[Contribution] = []
