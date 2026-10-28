import os
import requests

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
TARGETS = [
    "Google Pixel 10 256Go",
    "Samsung Galaxy S25 256Go",
]


def clean_price(price_str):
  """Convertit '749,00 €' en float (749.0) pour pouvoir trier les offres."""
  if not price_str:
    return 99999.0
  try:
    cleaned = (
        price_str.replace("€", "")
        .replace("\xa0", "")
        .strip()
        .replace(" ", "")
        .replace(",", ".")
    )
    return float(cleaned)
  except ValueError:
    return 99999.0


def fetch_offers_for_query(query):
  """Interroge l'API Google Shopping (via SerpAPI) pour des résultats propres."""
  if not SERPAPI_KEY:
    print("Erreur : La clé SERPAPI_KEY n'est pas définie dans l'environnement.")
    return []

  url = "https://serpapi.com/search"
  params = {
      "engine": "google_shopping",
      "q": query,
      "hl": "fr",
      "gl": "fr",
      "api_key": SERPAPI_KEY,
  }

  try:
    response = requests.get(url, params=params)
    data = response.json()

    if "shopping_results" not in data:
      print(f"Aucun résultat trouvé pour : {query}")
      return []

    offers = []
    for item in data["shopping_results"]:
      title = item.get("title", "")
      price_str = item.get("price", "")
      link = item.get("link", "")
      source = item.get("source", "Marchand inconnu")

      title_lower = title.lower()

      # Filtrage strict : 256 Go minimum et exclusion des états trop dégradés
      has_256gb = (
          "256" in title_lower and "go" in title_lower
      ) or "256gb" in title_lower
      is_bad_condition = "état correct" in title_lower or "bon état" in title_lower

      if has_256gb and not is_bad_condition:
        offers.append({
            "title": title,
            "price_raw": price_str,
            "price_value": clean_price(price_str),
            "source": source,
            "link": link,
        })

    # Tri de la moins chère à la plus chère
    offers.sort(key=lambda x: x["price_value"])
    return offers

  except Exception as e:
    print(f"Erreur lors de la requête API pour {query} : {e}")
    return []


if __name__ == "__main__":
  print("=== LANCEMENT DU COMPARATEUR DE PRIX AUTOMATISÉ ===")

  for target in TARGETS:
    print(f"\n🔍 Analyse des offres pour : {target} (256Go min, Neuf/Reco)")
    results = fetch_offers_for_query(target)

    if not results:
      print("   -> Aucune offre valide trouvée.")
    else:
      for i, r in enumerate(results[:3], 1):
        print(f"   #{i} | {r['price_raw']} chez {r['source']}")
        print(f"        Produit : {r['title']}")
        print(f"        Lien : {r['link']}")
