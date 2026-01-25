"""
SerpAPI Client for product discovery and shopping search
Optimized for furniture and home decor product search with direct product links and images
"""

import os
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

from dotenv import load_dotenv
from serpapi import GoogleSearch
import requests
from PIL import Image

from cache_manager import cache_manager

load_dotenv()


class SerpClient:
    """Client for SerpAPI to find furniture products with direct links and images"""

    def __init__(self, api_key: str = None):
        """Initialize SERP client with API key"""
        if GoogleSearch is None:
            raise ImportError(
                "google-search-results package not installed. Install with: pip install google-search-results"
            )

        self.api_key = api_key or os.getenv("SERP_API_KEY")
        if not self.api_key:
            raise ValueError("SERP_API_KEY not found in environment variables")

        print(f"🔧 SERP Client initialized with API key: {self.api_key[:10]}...")

    def search_products(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Search for furniture products using Google Shopping (with caching)

        Args:
            query: Search query (e.g., "modern gray sectional sofa")
            num_results: Number of results to return

        Returns:
            Search results from SerpAPI Google Shopping
        """
        # Check cache first
        cached = cache_manager.get_product_search("serp", query, num_results)
        if cached is not None:
            print(f"[SERP_API] 💾 Cache HIT for query: '{query[:40]}...'")
            return {"results": cached}

        try:
            print(f"[SERP_API] Query: '{query}' (requesting {num_results} results)")

            # Use Google Shopping search - simple and direct
            search = GoogleSearch(
                {
                    "q": query,
                    "tbm": "shop",
                    "api_key": self.api_key,
                    "num": min(num_results, 20),  # Increased from 10 for better coverage
                    "hl": "en",
                    "gl": "us",
                }
            )

            result = search.get_dict()

            print(f"[SERP_API] Response keys: {list(result.keys())}")

            # Check for API errors first
            if "error" in result:
                print(f"[SERP_API] ERROR: {result['error']}")
                return {"error": result["error"], "results": []}

            # Get shopping results
            shopping_results = result.get("shopping_results", [])
            print(f"[SERP_API] Raw shopping_results count: {len(shopping_results)}")

            # Debug: Show first shopping result structure if available
            if shopping_results:
                first_result = shopping_results[0]
                print(f"📦 First shopping result fields: {list(first_result.keys())}")
                print(
                    f"📦 Sample: {first_result.get('title', 'No title')[:50]}... from {first_result.get('source', 'Unknown')}"
                )

                # Debug link fields to find the correct retailer URL
                print("🔗 Available link fields:")
                print(f"   - product_link: {first_result.get('product_link', 'None')}")
                print(f"   - link: {first_result.get('link', 'None')}")
                if "extensions" in first_result:
                    print(f"   - extensions: {first_result.get('extensions', [])}")
            else:
                print("❌ No shopping_results in SerpAPI response")

            # If no shopping results, try to return other relevant results
            if not shopping_results:
                print("⚠️ No shopping results, checking other result types...")
                organic_results = result.get("organic_results", [])
                images_results = result.get("images_results", [])
                print(
                    f"🔍 Organic results: {len(organic_results)}, Images: {len(images_results)}"
                )

                # Create shopping-format results from organic results as fallback
                if organic_results:
                    shopping_results = [
                        {
                            "title": item.get("title", ""),
                            "product_link": item.get(
                                "link", ""
                            ),  # Use product_link format
                            "source": item.get("displayed_link", ""),
                            "snippet": item.get("snippet", ""),
                            "price": "Check website for price",
                            "extracted_price": 0,
                            "rating": 0,
                            "reviews": 0,
                        }
                        for item in organic_results[:5]
                    ]
                    print(
                        f"🔧 Created {len(shopping_results)} fallback results from organic"
                    )

            # Build results list
            results_list = [
                {
                    # Map SerpAPI fields to our expected format
                    "url": self._extract_retailer_url(
                        item
                    ),  # Extract direct retailer URL
                    "title": item.get("title", ""),
                    "id": item.get("product_id", ""),
                    "score": 1.0,
                    "published_date": None,
                    "author": None,
                    "extract": item.get("snippet", ""),
                    "text": item.get("snippet", ""),
                    "highlights": [],
                    # SerpAPI Google Shopping specific fields
                    "price": item.get("price", ""),
                    "extracted_price": item.get("extracted_price", 0),
                    "source": item.get("source", ""),
                    "source_icon": item.get("source_icon", ""),
                    "thumbnail": item.get("thumbnail", ""),
                    "thumbnails": item.get("thumbnails", []),
                    "rating": item.get("rating", 0),
                    "reviews": item.get("reviews", 0),
                    "delivery": item.get("delivery", ""),
                    "installment": item.get(
                        "installment", {}
                    ),  # Monthly payment info
                }
                for item in shopping_results
            ]

            # Cache successful results
            if results_list:
                cache_manager.set_product_search("serp", query, num_results, results_list)

            return {"results": results_list}

        except Exception as e:
            print(f"Error searching products: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e), "results": []}

    def get_product_details(
        self, search_results: List[Dict[str, Any]], max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract product information from SerpAPI search results

        Args:
            search_results: List of search results from SerpAPI
            max_results: Maximum number of results to process

        Returns:
            List of product details with pricing, availability, etc.
        """
        if not search_results:
            return []

        products = []
        for result in search_results[:max_results]:
            product = self._extract_product_info(result)
            if product:
                products.append(product)

        # Sort by rating and reviews (handle None values)
        products.sort(
            key=lambda x: (x.get("rating") or 0, x.get("reviews") or 0), reverse=True
        )
        return products

    def search_and_analyze_products(
        self, query: str, space_type: str, num_results: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Complete workflow: search for products and analyze them

        Args:
            query: Product search query
            space_type: Room type (bedroom, living room, etc.)
            num_results: Number of initial search results

        Returns:
            List of analyzed products with scores and details
        """
        # Search for products
        search_results = self.search_products(query, num_results)

        if "error" in search_results:
            return []

        # Get product details from search results
        products = self.get_product_details(search_results.get("results", []))

        # Enhance with space type context
        for product in products:
            product["space_type"] = space_type
            product["search_query"] = query

        print(f"✅ Returning {len(products)} real products (no mocks)")
        return products

    # --- Store trust scoring ---
    def _get_store_trust_score(self, product: Dict[str, Any]) -> float:
        """Get trust score for a product based on its retailer.

        Args:
            product: Product dictionary with 'source' or 'store' field

        Returns:
            Trust score between 0.0 and 1.0
        """
        try:
            from config import FeatureFlags, STORE_TRUST_SCORES
            if not FeatureFlags.STORE_TRUST_SCORES:
                return 0.70  # Default neutral score when feature disabled
        except ImportError:
            return 0.70

        # Get store name from product
        store = product.get("source", "") or product.get("store", "")
        store_lower = store.lower().strip()

        # Direct lookup
        if store_lower in STORE_TRUST_SCORES:
            return STORE_TRUST_SCORES[store_lower]

        # Partial match
        for store_key, score in STORE_TRUST_SCORES.items():
            if store_key in store_lower or store_lower in store_key:
                return score

        # Default score for unknown stores
        return STORE_TRUST_SCORES.get("default", 0.70)

    # --- Multi-signal scoring ---
    def _compute_multi_signal_score(
        self,
        product: Dict[str, Any],
        visual_similarity: float,
        query: str = ""
    ) -> float:
        """Compute a weighted multi-signal score for a product.

        Args:
            product: Product dictionary
            visual_similarity: CLIP visual similarity score (0-1)
            query: Optional search query for text relevance

        Returns:
            Combined score between 0.0 and 1.0
        """
        try:
            from config import FeatureFlags
            if not FeatureFlags.MULTI_SIGNAL_RANKING:
                # Return visual similarity only when multi-signal disabled
                return visual_similarity
        except ImportError:
            return visual_similarity

        # Weights for different signals
        weights = {
            "visual_similarity": 0.50,  # CLIP image match
            "text_relevance": 0.20,     # Title matches query
            "store_trust": 0.12,        # Quality retailer
            "rating": 0.08,             # Customer reviews
            "price_available": 0.10,    # Has clear pricing
        }

        scores = {}

        # Visual similarity (already computed)
        scores["visual_similarity"] = visual_similarity

        # Text relevance - check if query terms appear in title
        if query:
            title = product.get("title", "").lower()
            query_terms = query.lower().split()
            matching_terms = sum(1 for term in query_terms if term in title)
            scores["text_relevance"] = min(1.0, matching_terms / max(len(query_terms), 1))
        else:
            scores["text_relevance"] = 0.5  # Neutral when no query

        # Store trust
        scores["store_trust"] = self._get_store_trust_score(product)

        # Rating (normalize to 0-1, assume 5-star scale)
        rating = product.get("rating", 0) or 0
        scores["rating"] = min(1.0, rating / 5.0) if rating > 0 else 0.5

        # Price available (binary signal)
        has_price = bool(product.get("price") or product.get("extracted_price") or product.get("price_str"))
        scores["price_available"] = 1.0 if has_price else 0.3

        # Compute weighted sum
        total_score = sum(scores[key] * weights[key] for key in weights)

        # Store component scores for debugging
        product["_score_components"] = scores

        return total_score

    # --- CLIP-based thumbnail scoring ---
    def score_products_with_clip(
        self,
        products: List[Dict[str, Any]],
        clip_client,
        query_image,
        drop_threshold: float = 0.70,
        boost_threshold: float = 0.85,
        timeout: float = 1.5,
        max_workers: int = 8,
        max_fetch: int = 10,
        search_query: str = "",
    ) -> Dict[str, Any]:
        """Download SERP thumbnails in parallel and re-rank using CLIP similarity.

        Args:
            products: SERP-shaped product dictionaries.
            clip_client: CLIPClient instance (must support encode_image/compute_similarity).
            query_image: PIL image or path for the cropped query region.
            drop_threshold: Similarity below which items are discarded.
            boost_threshold: Similarity above which items are prioritized.
            timeout: Per-thumbnail fetch timeout in seconds.
            max_workers: Thread pool size for concurrent fetches.
            max_fetch: Max number of products to fetch/score (rest keep order).
            search_query: Optional search query for multi-signal text relevance.

        Returns:
            Dict with products (reordered/filtered) and scoring metadata.
        """
        # Check if multi-signal ranking is enabled
        use_multi_signal = False
        try:
            from config import FeatureFlags
            use_multi_signal = FeatureFlags.MULTI_SIGNAL_RANKING
        except ImportError:
            pass

        if not clip_client or not getattr(clip_client, "is_available", lambda: False)():
            return {
                "products": products,
                "meta": {"scoring": "skipped", "reason": "clip_unavailable"},
            }

        try:
            query_embedding = clip_client.encode_image(query_image)
            if query_embedding is None:
                return {
                    "products": products,
                    "meta": {"scoring": "skipped", "reason": "no_query_embedding"},
                }
        except Exception:
            return {
                "products": products,
                "meta": {"scoring": "skipped", "reason": "encode_query_failed"},
            }

        def pick_thumbnail(prod: Dict[str, Any]) -> Optional[str]:
            if prod.get("thumbnail"):
                return prod["thumbnail"]
            if prod.get("thumbnails"):
                # thumbnails may be list of strings or dicts
                first = prod["thumbnails"][0]
                if isinstance(first, str):
                    return first
                if isinstance(first, dict):
                    return first.get("link") or first.get("thumbnail")
            images = prod.get("images") or []
            if images:
                return images[0]
            if prod.get("image"):
                return prod.get("image")
            return None

        def fetch_image(url: str):
            try:
                resp = requests.get(url, timeout=timeout)
                if resp.status_code != 200:
                    return None
                return Image.open(BytesIO(resp.content)).convert("RGB")
            except Exception:
                return None

        # Fetch thumbnails concurrently
        scored: List[Dict[str, Any]] = []
        download_jobs = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx, prod in enumerate(products[:max_fetch]):
                url = pick_thumbnail(prod)
                if not url:
                    continue
                download_jobs[executor.submit(fetch_image, url)] = (idx, prod, url)

            for future in as_completed(download_jobs):
                idx, prod, url = download_jobs[future]
                image = future.result()
                if image is None:
                    prod["similarity_score"] = 0.0
                    prod["filter_reason"] = "thumb_fetch_failed"
                    prod["thumbnail_used"] = url
                    scored.append((idx, prod))
                    continue

                try:
                    thumb_embedding = clip_client.encode_image(image)
                    if thumb_embedding is None:
                        prod["similarity_score"] = 0.0
                        prod["filter_reason"] = "thumb_encode_failed"
                    else:
                        sim = clip_client.compute_similarity(query_embedding, thumb_embedding)
                        prod["similarity_score"] = sim

                        # Apply multi-signal ranking if enabled
                        if use_multi_signal:
                            prod["combined_score"] = self._compute_multi_signal_score(
                                prod, sim, search_query
                            )
                            prod["store_trust"] = self._get_store_trust_score(prod)
                        else:
                            prod["combined_score"] = sim

                        if sim < drop_threshold:
                            prod["filter_reason"] = "dropped_low_similarity"
                        elif sim > boost_threshold:
                            prod["filter_reason"] = "boosted_high_similarity"
                        else:
                            prod["filter_reason"] = "kept_neutral"
                    prod["thumbnail_used"] = url
                except Exception:
                    prod["similarity_score"] = 0.0
                    prod["filter_reason"] = "scoring_failed"
                    prod["thumbnail_used"] = url

                scored.append((idx, prod))

        # Merge scored results with unscored tail (keep original order for tail)
        scored_indices = {idx for idx, _ in scored}
        unscored = [prod for i, prod in enumerate(products) if i not in scored_indices]

        # Apply drop/boost logic
        kept = [p for _, p in scored if p.get("similarity_score", 0) >= drop_threshold]
        dropped = [p for _, p in scored if p.get("similarity_score", 0) < drop_threshold]

        # Sort by combined_score (multi-signal) or similarity_score
        sort_key = "combined_score" if use_multi_signal else "similarity_score"
        kept.sort(key=lambda p: p.get(sort_key, 0), reverse=True)
        boosted = [p for p in kept if p.get("similarity_score", 0) > boost_threshold]

        # Append unscored items after scored ones to preserve some completeness
        final_products = kept + unscored

        meta = {
            "scoring": "completed",
            "multi_signal_ranking": use_multi_signal,
            "thresholds": {"drop": drop_threshold, "boost": boost_threshold},
            "counts": {
                "input": len(products),
                "scored": len(scored),
                "kept": len(kept),
                "dropped": len(dropped),
                "boosted": len(boosted),
            },
        }

        return {"products": final_products, "meta": meta}

    # --- Google Lens reverse image search support ---
    def reverse_image_search_google_lens(self, image_path: str) -> List[Dict[str, Any]]:
        """Perform Google Lens reverse image search via SerpAPI.

        SerpAPI supports Google Lens through engine=google_lens and 'url' pointing to
        a publicly accessible image. For local development we can still send the
        local file by first base64 encoding in a data URL, but many times Lens API
        requires a remote URL. This implementation uses the local path; the backend
        can be extended to upload to a public host if needed.
        """
        try:
            # For development we will reuse Google Shopping product search fallback
            # by creating a quick descriptor based on filename; however SerpAPI's
            # Google Lens generally requires a public URL. We'll attempt calling it
            # directly to allow experimentation.
            params = {
                "engine": "google_lens",
                "url": f"file://{image_path}",  # many providers require public URL; dev fallback
                "api_key": self.api_key,
            }
            search = GoogleSearch(params)
            result = search.get_dict()

            # Extract visual_matches when available
            matches = []
            visual = result.get("visual_matches") or []
            for m in visual:
                matches.append({
                    "title": m.get("title"),
                    "link": m.get("link"),
                    "source": m.get("source"),
                    "thumbnail": m.get("thumbnail"),
                    "product_link": m.get("product_link") or m.get("link"),
                })

            # Fallback to inline_images / image_results if present
            if not matches:
                for m in result.get("inline_images", [])[:10]:
                    matches.append({
                        "title": m.get("title"),
                        "link": m.get("link"),
                        "source": m.get("source"),
                        "thumbnail": m.get("thumbnail"),
                    })

            return matches

        except Exception as e:
            print(f"Error in reverse_image_search_google_lens: {e}")
            return []

    def reverse_image_search_google_lens_url(self, image_url: str) -> List[Dict[str, Any]]:
        """Enhanced Google Lens search using all result types for better matching.

        Args:
            image_url: Publicly accessible image URL

        Returns:
            List of match dicts with priority: exact_matches > visual_matches > knowledge_graph
        """
        try:
            params = {
                "engine": "google_lens",
                "url": image_url,
                "api_key": self.api_key,
            }
            search = GoogleSearch(params)
            result = search.get_dict()

            matches: List[Dict[str, Any]] = []
            seen_urls = set()

            # Priority 1: exact_matches (identical/near-identical products - highest value)
            exact_count = 0
            for m in result.get("exact_matches", []) or []:
                url = m.get("link", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    matches.append({
                        "title": m.get("title"),
                        "link": url,
                        "product_link": m.get("product_link") or url,
                        "source": m.get("source"),
                        "thumbnail": m.get("thumbnail"),
                        "price": m.get("price"),
                        "match_type": "exact",
                    })
                    exact_count += 1
            if exact_count > 0:
                print(f"[LENS] Found {exact_count} exact matches")

            # Priority 2: visual_matches (visually similar products)
            visual_count = 0
            for m in result.get("visual_matches", []) or []:
                url = m.get("link", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    matches.append({
                        "title": m.get("title"),
                        "link": url,
                        "product_link": m.get("product_link") or url,
                        "source": m.get("source"),
                        "thumbnail": m.get("thumbnail"),
                        "price": m.get("price"),
                        "match_type": "visual",
                    })
                    visual_count += 1
            if visual_count > 0:
                print(f"[LENS] Found {visual_count} visual matches")

            # Priority 3: knowledge_graph products (product metadata)
            kg = result.get("knowledge_graph", {})
            kg_count = 0
            for item in kg.get("products", []) or []:
                url = item.get("link", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    matches.append({
                        "title": item.get("title") or kg.get("title"),
                        "link": url,
                        "product_link": url,
                        "source": item.get("source"),
                        "thumbnail": item.get("thumbnail"),
                        "price": item.get("price"),
                        "match_type": "knowledge_graph",
                    })
                    kg_count += 1
            if kg_count > 0:
                print(f"[LENS] Found {kg_count} knowledge graph products")

            # Fallback to inline_images if no other matches found
            if not matches:
                for m in result.get("inline_images", [])[:10]:
                    url = m.get("link", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        matches.append({
                            "title": m.get("title"),
                            "link": url,
                            "source": m.get("source"),
                            "thumbnail": m.get("thumbnail"),
                            "match_type": "inline",
                        })

            print(f"[LENS] Total matches: {len(matches)}")
            return matches
        except Exception as e:
            print(f"Error in reverse_image_search_google_lens_url: {e}")
            return []

    def _extract_retailer_url(self, shopping_result: Dict[str, Any]) -> str:
        """Extract the direct retailer URL instead of Google Shopping intermediate page"""

        # Check for direct retailer link in extensions (preferred)
        extensions = shopping_result.get("extensions", [])
        for ext in extensions:
            if isinstance(ext, str) and ("Shop at" in ext or "Buy from" in ext):
                # Sometimes extensions contain direct retailer links
                continue

        # Try the 'link' field first (direct retailer link)
        direct_link = shopping_result.get("link")
        if direct_link and not direct_link.startswith(
            "https://www.google.com/shopping"
        ):
            return direct_link

        # Fall back to product_link (Google Shopping page)
        product_link = shopping_result.get("product_link", "")

        # If we only have Google Shopping link, try to construct direct retailer URL
        # This is a fallback - the user will still get working links to Google Shopping
        source = shopping_result.get("source", "").lower()
        if product_link and source:
            print(
                f"⚠️ Using Google Shopping link for {source} - may redirect to retailer"
            )

        return product_link

    def _extract_product_info(
        self, search_result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract structured product information from SerpAPI search result"""
        try:
            url = search_result.get("url", "")
            title = search_result.get("title", "")
            # Basic shopping signals: price or rating or source
            has_price = bool(search_result.get("price"))
            has_source = bool(search_result.get("source"))
            has_thumb = bool(search_result.get("thumbnail"))

            if not url or not title or not (has_price or has_source or has_thumb):
                return None

            # SerpAPI provides store name directly in 'source' field
            store_name = search_result.get("source", "Unknown Store")

            # SerpAPI provides thumbnail and thumbnails array
            images = []
            if search_result.get("thumbnail"):
                images.append(search_result["thumbnail"])
            # Add additional thumbnails if available
            if search_result.get("thumbnails"):
                images.extend(search_result["thumbnails"])

            # SerpAPI provides both price string and extracted numeric price
            price_str = search_result.get("price", "")
            price_value = search_result.get("extracted_price", 0)

            # Build product info matching frontend expectations
            product_info = {
                "title": title,
                "url": url,
                "store": store_name,
                "price": float(price_value) if price_value else None,
                "price_str": price_str,
                "availability": "Available" if price_str else "Check availability",
                "images": images,
                "description": search_result.get("extract", ""),
                "rating": search_result.get("rating", 0),
                "reviews": search_result.get("reviews", 0),
                "delivery": search_result.get("delivery", "Standard shipping"),
                "relevance_score": 1.0,
                "materials": [],
                "colors": [],
                "dimensions": "",
                # Additional SerpAPI fields
                "source_icon": search_result.get("source_icon", ""),
                "installment": search_result.get("installment", {}),
            }

            return product_info

        except Exception as e:
            print(f"❌ Error extracting product info: {e}")
            return None

    def _extract_store_name(self, source: str, url: str) -> str:
        """Extract store name from source or URL"""
        if source:
            return source

        # Extract from URL if source not available
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc.lower()

            store_mapping = {
                "wayfair.com": "Wayfair",
                "westelm.com": "West Elm",
                "cb2.com": "CB2",
                "crateandbarrel.com": "Crate & Barrel",
                "potterybarn.com": "Pottery Barn",
                "article.com": "Article",
                "ikea.com": "IKEA",
                "amazon.com": "Amazon",
                "target.com": "Target",
                "homedepot.com": "Home Depot",
                "walmart.com": "Walmart",
                "overstock.com": "Overstock",
                "allmodern.com": "AllModern",
                "ashleyfurniture.com": "Ashley Furniture",
                "roomstogo.com": "Rooms To Go",
                "livingspaces.com": "Living Spaces",
                "homegoods.com": "HomeGoods",
            }

            for domain_key, store_name in store_mapping.items():
                if domain_key in domain:
                    return store_name

            # Default to capitalized domain
            return domain.replace("www.", "").replace(".com", "").title()

        except Exception:
            return "Unknown Store"

    def _extract_price(self, price_str: str) -> Optional[float]:
        """Extract numeric price from price string"""
        if not price_str:
            return None

        try:
            import re

            # Remove currency symbols and extract numbers
            price_match = re.search(r"[\d,]+\.?\d*", price_str.replace(",", ""))
            if price_match:
                return float(price_match.group())
        except Exception:
            pass

        return None
