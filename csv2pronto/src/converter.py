"""Module to convert dictionaries to RDF graphs."""

import ast
from contextlib import suppress
from datetime import datetime
import pandas as pd
import dateutil.parser as dateparser
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import DC, FOAF, RDF, RDFS, SDO
from . import Node
from .faker.faker import Faker
from .incrementals.incrementals import Incremental
from .null_objects.factory import Boolean, DateTime, Double, Float, Integer, String, Literal
from .null_objects.null_objects import NoneNode
from .null_objects.safe_objects import SafeGraph, SafeNamespace
from .wrappers.wrappers import default_to_incremental, default_to_NoneNode

IO = SafeNamespace("http://www.semanticweb.org/luciana/ontologies/2024/8/inmontology#")
PR = SafeNamespace("https://raw.githubusercontent.com/fdioguardi/pronto/main/ontology/pronto.owl#")
SIOC = SafeNamespace("http://rdfs.org/sioc/ns#")
GR = SafeNamespace("http://purl.org/goodrelations/v1#")
REC = SafeNamespace("https://w3id.org/rec#")
TIME = SafeNamespace("http://www.w3.org/2006/time#")
BRICK = SafeNamespace("https://brickschema.org/schema/Brick#")
GEO= SafeNamespace("http://www.opengis.net/ont/geosparql#")
dic_map= {
        "esquina": "CornerLot",
        "pileta": "SwimmingPool",
        "loteo_ph": "CondominiumUnit",
        "indiviso": "UndividedLot",
        "irregular": "IrregularLot",
        "es_monetizable": "IsMonetizable",
        "a_demoler": "ToDemolish",
        "es_multioferta": "Multioffering",
        "preventa": "PreSale",
        "posesion": "Posession",
        "age": "PropertyAge"

    }
#row, graph, idx, args.destination, args.format, args.sites
def create_graph_from_chunk(df: pd.DataFrame, graph, idx, destination, format,sites,mode : str) -> Graph:
   """
   Writes a partial graph `g` with the info of a chunk of rows.

   Args:
       df (pd.DataFrame): a Pandas Dataframe with the info to add to `g`.
   """

   for i in range(len(df)) :
       if mode == "scraper":
           graph += create_graph_scraper(df.iloc[i].to_dict(),mode,sites)
       elif mode == "ave":
           graph += create_graph_ave(df.iloc[i].to_dict(), mode, sites)
   graph.serialize(destination, format=format, encoding="utf-8")



"""
    El anonymizer lo que hace es alimina los campos vacios y a los sitios les cambia el nombre.
"""
def anonymize(row : dict, sites : dict) -> dict:
   
    row = {k: v for k, v in row.items() if v != ""} 
    row = Faker.anonymize(row)
    return row


def create_graph_scraper(row: dict, mode: str, sites) -> Graph:
    row = anonymize(row)
    g : Graph = SafeGraph()
    g.parse("output.ttl",format="turtle")

    

    agent, account = add_agent(g, row) 
    real_estate = add_real_estate(g, row, mode)


    listing = add_listing(g, row, mode)


    g.add((listing, SIOC.has_creator, account))
    g.add((account, SIOC.creator_of, listing))
    g.add((listing, FOAF.maker, agent))
    g.add((agent, FOAF.made, listing))

    g.add((listing, SIOC.about, real_estate))

    
    return g



def create_graph_ave(row: dict, mode: str,sites) -> Graph:

    row = anonymize(row)
    #Recibir el grafo del scrapper y parsearlo para leerlo
    g: Graph = SafeGraph() 
    g.parse("output.ttl",format="turtle")

        
    real_estate = add_real_estate(g, row, mode)

    #listing = add_listing(g, row, mode)
    
    
    #g.add((listing, SIOC.about, real_estate))
    
    return g


def add_listing(g: Graph, row: dict, mode : str) -> Node:
    """Add listing to the graph `g` and return the listing's `Node`."""

    @default_to_incremental(PR, Incremental.LISTING)
    def _create_listing():
        return IO[f"listing_{row['site']}_{row['listing_id']}"]

    listing: Node = _create_listing()
    g.add((listing, RDF.type, PR.RealEstateListing))

    if row.get("url"):
        g.add((listing, SIOC.link, URIRef(row["url"])))
    g.add((listing, RDFS.label, String(row.get("title"))))
    # g.add((listing, IO.descripcion, String(row.get("description")))) #TODO: cambiar comment

    ###

    if row.get("transaction"):
        buisness_func = (
            GR.Sell if row["transaction"].lower() == "venta" else GR.LeaseOut
        )
        g.add((listing, GR.hasBusinessFunction, buisness_func))

    site: Node = PR[row["site"]]
    g.add((site, RDF.type, SIOC.Site))
    g.add((listing, SIOC.has_space, site)) #TODO: cambiar has_space
    g.add((site, SIOC.space_of, listing)) #TODO: cambiar space_of

    g.add((listing, SIOC.id, String(row.get("listing_id"))))

    if row.get("date_extracted"):
        date = dateparser.parse(row["date_extracted"])
        g.add((listing, SIOC.read_at, DateTime(date)))

    if row.get("date_published"):
        date = dateparser.parse(row["date_published"])
        g.add((listing, DC.date, DateTime(date)))
        

    if row.get("price") and row.get("currency"):
        price: Node = add_price(g, listing, row["price"], row["currency"], "BASE", dateparser.parse(row["date_extracted"]))
        g.add((listing, IO.hasFeature, price))

    if row.get("maintenance_fee") and row.get("maintenance_fee_currency"):
        expenses: Node = add_price(
            g,
            listing,
            row.get("maintenance_fee", ""),
            row.get("maintenance_fee_currency", ""),
            "MAINTENANCE FEE",
            dateparser.parse(row["date_extracted"])
        )

        g.add((listing, IO.hasFeature, expenses))

    ###

    return listing


def add_price(g: Graph, listing:Node, value: float, currency: str, p_type: str, date: datetime|None) -> Node:
    """Add price to the graph `g` and return the price's `Node`."""

    priceValue: Node = BNode()
    featurePrice: Node = create_feature(listing, "price")
    dateNode: Node = BNode()
    
    g.add((priceValue, RDF.type, GR.UnitPriceSpecification))
    g.add((priceValue, GR.hasCurrency, String(currency)))
    g.add((priceValue, GR.hasCurrencyValue, Float(value)))
    g.add((priceValue, GR.priceType, String(p_type)))
    g.add((featurePrice, IO.hasValue, priceValue))
    
    g.add((featurePrice, RDF.type, IO.Price))
    g.add((featurePrice, IO.hasOrigin, IO.Scraper))

    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((featurePrice, TIME.hasTime, dateNode))
    


    return featurePrice



def add_agent(g: Graph, row: dict) -> tuple[Node, Node]:
    """
    Add real estate agent to the graph `g` and return a tuple with the
    `Node`s of the agent and its user account.
    """

    @default_to_NoneNode
    def _create_agent():
        return IO[f"agent_{row['advertiser_name']}"]

    @default_to_NoneNode
    def _create_account():
        return IO[f"account_{row['site']}_{row['advertiser_id']}"]

    agent: Node = _create_agent()
    account: Node = _create_account()

    g.add((agent, RDF.type, FOAF.Agent))
    g.add((account, RDF.type, SIOC.UserAccount))

    g.add((account, SIOC.id, String(row.get("advertiser_id"))))
    g.add((account, SIOC.name, String(row.get("advertiser_name"))))
    g.add((agent, FOAF.account, account))
    g.add((account, SIOC.account_of, agent))

    return agent, account


def add_real_estate_type(g: Graph, real_estate: Node, row: dict, mode : str) -> None:
    if (str(row.get("property_type"))== "Casa"):
        g.add((real_estate, RDF.type, IO.House))
    elif (str(row.get("property_type"))== "Departamento"):
        g.add((real_estate, RDF.type, IO.Apartment))
    elif (str(row.get("property_type"))== "Terreno"):
        g.add((real_estate, RDF.type, IO.Land))
    elif (str(row.get("property_type"))== "Galpon"):
        g.add((real_estate, RDF.type, IO.Warehouse))
    elif (str(row.get("property_type"))== "Fondo de comercio") or (str(row.get("property_type"))== "Local"):
        g.add((real_estate, RDF.type, IO.Store))
    elif (str(row.get("property_type"))== "Ph"):
        g.add((real_estate, RDF.type, IO.CondominiumUnit))
    elif (str(row.get("property_type"))== "Cochera"):
        g.add((real_estate, RDF.type, IO.ParkingLot))
    else:
        g.add((real_estate, RDF.type, IO.RealEstate))
                

def add_real_estate(g: Graph, row: dict) -> Node:
    """
    Add real estate to the graph `g` and return the real estate's
    `Node`.
    """   

    @default_to_incremental(PR, Incremental.REAL_ESTATE)
    def _create_real_estate():
        return IO[f"real_estate_{row['site']}_{row['listing_id']}"]

    @default_to_incremental(PR, Incremental.SPACE)
    def _create_space(s_type: str):
        return IO[f"space_{s_type}_{row['site']}_{row['listing_id']}"]

    real_estate: Node = _create_real_estate()
    land: Node = _create_space("land")  
    building: Node = _create_space("building")  
    
    add_real_estate_type(g, real_estate, row)

    if (row.get("age") and row.get("age") != "0"):
        add_feature(g, real_estate, "age", row.get("age"), dateparser.parse(row.get("date_extracted")))
    g.add((real_estate, REC.includes, land))
    building=None
    if (str(row.get("property_type"))!= "Terreno"):
        building: Node = _create_space("building")  
        g.add((building, RDF.type, REC.Building))
        g.add((real_estate, REC.includes, building))
        g.add((land, BRICK.hasPart, building))
         # add amount of rooms
        g.add((building, PR.has_number_of_rooms, Integer(row.get("room_amnt"))))
        rooms: dict[str, Node] = {
            "bath": REC.Bathroom,
            "garage": REC.Garage,
            "bed": REC.Bedroom,
            "toilette": REC.Toilet,
        }
        for room, room_class in rooms.items():
            add_room(g, building, row, room, room_class)

        #add features to BUILDING
        for s in ["es_monetizable", "a_demoler"]:
            with suppress(KeyError):
                if row[s] == "True":
                    value = row[s] == "True"
                else:
                    value = row[s]
    
                if value:
                    add_feature(g, building, s, value, dateparser.parse("2025-03-01"))
    g.add((land, RDF.type, REC.Site))
    

    #-----
    point: Node = BNode()
    g.add((point, RDF.type, GEO.Geometry))
    # wkt_literal = RDFS.Literal(f"POINT({row.get('latitude')} {row.get('longitude')})", datatype=GEO.wktLiteral)
    g.add((point, GEO.asWKT, Literal(f"<http://www.opengis.net/def/crs/EPSG/0/4326> POINT({row.get('longitude')} {row.get('latitude')})", datatype=GEO.wktLiteral)))

    # g.add((point, REC.coordinates, String(f"[{row.get('latitude')},{row.get('longitude')}]")))
    g.add((land, GEO.hasGeometry, point)) 
    #-----


    district: Node = _create_district(row["district"], row["province"])
    province: Node = _create_province(row["province"])
    
    barrio= None
    neighborhood = NoneNode()
    if row.get("neighborhood"):
        barrio= str(row["neighborhood"])
    elif row.get("barrio"):
        barrio= str(row["barrio"])
    if barrio:
        neighborhood : Node = _create_neighborhood(province, district, barrio)
    
        g.add((neighborhood, RDF.type, IO.Neighborhood))
        g.add((neighborhood, RDFS.label, String(barrio)))

    g.add((district, RDF.type, IO.City))
    g.add((district, RDFS.label, String(row.get("district"))))
    
    g.add((province, RDF.type, IO.Province))
    g.add((province, RDFS.label, String(row.get("province"))))

    if row.get("address"):
        add_address(g, real_estate, IO.Scraper, str(row.get("address")), neighborhood, district, province, dateparser.parse(row.get("date_extracted")))
    if row.get("direccion"):
        add_address(g, real_estate, IO.AVE, str(row.get("direccion")), neighborhood, district, province, dateparser.parse("2025-03-01"))

    # if row.get("neighborhood"):
    #     add_neighborhood(g, real_estate, IO.hasScraperValue, IO.hasScraperTime, str(row["neighborhood"]), district, province, dateparser.parse(row.get("date_extracted")))
    # if row.get("barrio"):
    #     add_neighborhood(g, real_estate, IO.hasAVEValue, IO.hasAVETime, str(row["barrio"]), district, province, dateparser.parse("2025-03-01"))




    # g.add((real_estate, REC.locatedIn, district))
    # g.add((real_estate, REC.locatedIn, province))
    g.add((neighborhood, REC.locatedIn, district))

    g.add((district, REC.locatedIn, province))
    #---

    # if row.get("year_built"):
    #     g.add((space, SDO.yearBuilt, Integer(int(float(row.get("year_built", 0))))))

    # property_mapping = {
    #     "is_new_property": PR.is_brand_new,
    #     "is_finished": PR.is_finished,
    #     "is_studio_apartment": PR.is_studio_apartment,
    # }

    # for name, p in property_mapping.items():
    #     g.add((space, p, Boolean(None if row.get(name) == "" else row.get(name))))

    # g.add((space, PR.luminosity, String(row.get("luminosity"))))
    # g.add((space, PR.orientation, String(row.get("orientation"))))
    # g.add((space, PR.disposition, String(row.get("disposition"))))

    
        

    # add features to LAND
    for s in ["esquina", "pileta", "loteo_ph",  "indiviso", "irregular"]:
        with suppress(KeyError):
            if row[s] == "True":
                value = row[s] == "True"
            else:
                value = row[s]

            if value:
                add_feature(g, land, s, value, dateparser.parse("2025-03-01"))
    if (row.get("medidas")):
        add_dimensiones(g, land, str(row.get("medidas")), dateparser.parse("2025-03-01"))

    

    #add features to REAL ESTATE
    for s in ["es_multioferta", "preventa", "posesion"]:
        with suppress(KeyError):
            if row[s] == "True":
                value = row[s] == "True"
            else:
                value = row[s]

            if value:
                add_feature(g, real_estate, s, value, dateparser.parse("2025-03-01"))

        

    # features: dict = ast.literal_eval(row.get("features") or "{}")
    # for feature, value in features.items():
    #     add_feature(g, real_estate, feature, value, dateparser.parse(row.get("date_extracted")))
    
    # add surfaces
    for s in ["total", "covered", "uncovered", "land"]:
        with suppress(KeyError):
            value = row[f"{s}_surface"] or row[f"reconstructed_{s}_surface"]
            unit = row[f"{s}_surface_unit"] or row[f"reconstructed_{s}_surface_unit"]

            if value and unit:
                add_surface(g, land, value, unit, s, dateparser.parse(row.get("date_extracted")))

   
   
    return real_estate

@default_to_NoneNode
def _create_district(province:str, district:str):
    return IO[f'district_{district.replace(" ", "_")}_{province.replace(" ", "_")}']

@default_to_NoneNode
def _create_province(province:str):
    return IO[f'province_{province.replace(" ", "_")}']

@default_to_NoneNode
def _create_neighborhood(province:URIRef, district:URIRef, neighborhood:str):
    return IO[
        f'neighborhood_{neighborhood.replace(" ", "_")}_{district.fragment}_{province.fragment}'
    ]


def add_dimensiones(g: Graph, land: Node, value: str, date: datetime|None) -> Node:
    """Add dimensions to the graph g and return the surface's Node."""
    dimensionsValue: Node = BNode()
    featureDimensions: Node = create_feature(land, "dimensions")
    dateNode: Node = BNode() 
    
    g.add((dimensionsValue, RDF.type, PR.SizeSpecification))
    g.add((dimensionsValue, GR.hasValue, String(value)))
    g.add((dimensionsValue, GR.hasUnitOfMeasurement, String("metros")))
    g.add((dimensionsValue, PR.size_type, String("lot dimensions")))
    
    g.add((featureDimensions, RDF.type, IO.Dimensions))
    g.add((featureDimensions, IO.hasOrigin, IO.AVE))
    g.add((featureDimensions, IO.hasValue, dimensionsValue))

    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((featureDimensions, TIME.hasTime, dateNode))

    g.add((land, IO.hasFeature, featureDimensions))

    return dimensionsValue

def add_address(g: Graph, real_estate: Node, origin: URIRef, address: str, neighborhood: Node, district: Node, province: Node, date: datetime | None) -> Node:
    """Add address to the graph g and return the address's Node."""
    addressValue: Node = BNode()
    featureAddress: Node = create_feature(real_estate, "address")
    dateNode: Node = BNode()

    
    g.add((addressValue, RDF.type, IO.PostalAddress))
    g.add((addressValue, IO.address, String(address)))
    g.add((addressValue, IO.neighborhood, neighborhood))
    g.add((addressValue, IO.city, district))
    g.add((addressValue, IO.province, province))
    g.add((featureAddress, IO.hasValue, addressValue))

    g.add((featureAddress, RDF.type, IO.Address))
    g.add((featureAddress, IO.hasOrigin, origin))

    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((featureAddress, TIME.hasTime, dateNode))

    g.add((real_estate, IO.hasFeature, featureAddress))

    return addressValue

@default_to_incremental(IO, Incremental.FEATURE)
def create_feature(subject: Node, feature: str) -> Node:
    return IO[f"feature_{feature}_{subject.fragment}"]


def add_feature(g: Graph, space: Node, featureName :str, value, date: datetime|None) -> Node: 
    featureValue: Node = BNode()
    feature: Node = create_feature(space, featureName)
    dateNode: Node = BNode() 
    
    # g.add((featureValue, RDF.type, RDFS.Literal)) # ⸘Literal‽
    if (type(value)==int):
        g.add((feature, IO.hasValue, Integer(value)))
    if (type(value)==float):
        g.add((feature, IO.hasValue, Double(value)))
    if (type(value)==str):
        g.add((feature, IO.hasValue, String(value)))
    if (type(value)==bool):
        g.add((feature, IO.hasValue, Boolean(value)))
    
    g.add((feature, RDF.type, IO[dic_map[featureName]]))
    # g.add((feature, IO.hasValue, value))
    g.add((feature, IO.hasOrigin, IO.AVE))
    
    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((feature, TIME.hasTime, dateNode))
    

    if not (IO[dic_map[featureName]], RDFS.subClassOf, IO.Feature) in g:
        g.add((IO[dic_map[featureName]], RDFS.subClassOf, IO.Feature))


    g.add((space, IO.hasFeature, feature))

    return featureValue

def add_surface(g: Graph, space: Node, value: float, unit: str, s_type: str, date: datetime|None) -> Node:
    """Add surface to the graph g and return the surface's Node."""
    surfaceValue: Node = BNode()
    featureSurface: Node = create_feature(space, s_type)
    dateNode: Node = BNode() 
    
    g.add((surfaceValue, RDF.type, PR.SizeSpecification))
    g.add((surfaceValue, GR.hasValue, Float(value)))
    g.add((surfaceValue, GR.hasUnitOfMeasurement, String(unit)))
    g.add((surfaceValue, PR.size_type, String(s_type)))
    
    g.add((featureSurface, RDF.type, IO.Surface))
    g.add((featureSurface, IO.hasOrigin, IO.Scraper))
    g.add((featureSurface, IO.hasValue, surfaceValue))

    g.add((dateNode, RDF.type, TIME.Instant))
    g.add((dateNode, TIME.inXSDDateTimeStamp, DateTime(date)))
    g.add((featureSurface, TIME.hasTime, dateNode))

    g.add((space, IO.hasFeature, featureSurface))

    return surfaceValue

def add_room(g: Graph, space: Node, row: dict, room: str, room_class: Node) -> None:
    """Add rooms to the graph `g`."""

    amnt = row.get(f"{room}_amnt")
    if not amnt:
        return

    if not amnt.isdigit():
        return
    amnt = int(amnt)

    def _create_room() -> Node:
        fragment = getattr(space, "fragment", None)
        if not fragment:
            return BNode()
        return IO[f"{fragment}_{room}_{i}"]

    for i in range(amnt):
        r: Node = _create_room()
        g.add((r, RDF.type, room_class))
        g.add((space, BRICK.hasPart, r))
