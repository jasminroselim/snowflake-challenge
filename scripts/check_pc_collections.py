import pystac_client
import planetary_computer as pc

client = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=pc.sign_inplace,
)

keys = ["viirs", "night", "population", "gpw", "ghsl", "wealth", "income", "worldpop"]
collections = list(client.get_collections())
entries = [(c.id.lower(), (c.description or "").lower()) for c in collections]

for key in keys:
    matched = [collection_id for collection_id, desc in entries if key in collection_id or key in desc]
    print(f"{key} => {matched[:20]}")
