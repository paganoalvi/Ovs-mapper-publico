ML_PREFIX = "ML"
from faker import Faker as FakerReal
fake = FakerReal()

class Faker:
    "Class that anonimyzes data."

    @classmethod
    def anonymize(cls, row: dict, sites) -> dict:
        """Anonimyzes the data in a row."""
        row = row.copy()

        if row.get("listing_id", None):
            row["listing_id"] = cls.id(row["listing_id"])

        row["advertiser_name"]= fake.name()
        row["site"] = cls.site(row["site"], sites)
        row["url"] = None

        return row

    @classmethod
    def site(cls, site: str, sites) -> str:
        "Anonimyzes a site."
        return sites[site.lower()]

    @classmethod
    def id(cls, id: str) -> str | None:
        "Anoniymyzes an id."
        return id[2:] if id.startswith(ML_PREFIX) else id
