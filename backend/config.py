"""
Feature Flags and Configuration for Product Matching Pipeline

This module provides centralized configuration for the furniture product matching
system. Feature flags allow gradual rollout and easy rollback of improvements.
"""

import os


class FeatureFlags:
    """Feature flags for controlling product matching behavior.

    All flags default to values that improve matching quality while maintaining
    backward compatibility. Set environment variables to override defaults.
    """

    # Phase 1: Safe internal improvements (default ON)

    # CLIP Model - Use larger, more accurate model
    # +5-8% matching accuracy, ~2.5x slower (acceptable trade-off)
    USE_CLIP_LARGE = os.getenv("USE_CLIP_LARGE", "true").lower() == "true"

    # Vocabulary expansion - More specific furniture/style/material/color terms
    EXPANDED_VOCABULARY = os.getenv("EXPANDED_VOCABULARY", "true").lower() == "true"

    # Enhanced type guard - Better synonym matching and hard negative filtering
    ENHANCED_TYPE_GUARD = os.getenv("ENHANCED_TYPE_GUARD", "true").lower() == "true"

    # Store trust scores - Weight results by retailer quality
    STORE_TRUST_SCORES = os.getenv("STORE_TRUST_SCORES", "true").lower() == "true"

    # Phase 2: May affect result ordering (default OFF for safety)

    # Multi-signal ranking - Continuous scoring instead of binary drop/boost
    MULTI_SIGNAL_RANKING = os.getenv("MULTI_SIGNAL_RANKING", "false").lower() == "true"


# Store trust scores for ranking quality retailers higher
# Scores reflect retailer reliability for furniture purchases (0.0-1.0)
STORE_TRUST_SCORES = {
    # Premium furniture retailers (high trust)
    "crate & barrel": 0.92,
    "crate and barrel": 0.92,
    "west elm": 0.90,
    "cb2": 0.90,
    "article": 0.90,
    "pottery barn": 0.88,
    "room & board": 0.90,
    "design within reach": 0.90,
    "rejuvenation": 0.88,
    "serena & lily": 0.88,

    # Mid-tier furniture retailers
    "wayfair": 0.85,
    "allmodern": 0.85,
    "joss & main": 0.83,
    "overstock": 0.80,
    "ikea": 0.80,
    "world market": 0.80,
    "anthropologie": 0.82,
    "urban outfitters": 0.78,

    # Big box retailers (moderate trust for furniture)
    "target": 0.75,
    "amazon": 0.70,
    "walmart": 0.65,
    "home depot": 0.72,
    "lowe's": 0.72,

    # Specialty retailers
    "ethan allen": 0.88,
    "arhaus": 0.87,
    "z gallerie": 0.82,
    "ashley furniture": 0.75,
    "rooms to go": 0.73,
    "living spaces": 0.75,
    "bob's discount furniture": 0.68,

    # Default for unknown stores
    "default": 0.70,
}


# Expanded furniture vocabularies for CLIP analysis
FURNITURE_TYPES_EXPANDED = [
    # Seating - comprehensive
    "sofa", "couch", "sectional", "loveseat", "settee",
    "chair", "armchair", "accent chair", "lounge chair", "club chair",
    "recliner", "rocker", "rocking chair", "glider",
    "dining chair", "desk chair", "office chair", "task chair",
    "stool", "bar stool", "counter stool",
    "bench", "ottoman", "pouf", "footstool",

    # Tables - comprehensive
    "table", "coffee table", "cocktail table",
    "dining table", "kitchen table", "breakfast table",
    "side table", "end table", "accent table",
    "console table", "sofa table", "entry table", "hallway table",
    "nightstand", "bedside table", "night table",
    "desk", "writing desk", "computer desk", "secretary desk",
    "vanity", "vanity table", "dressing table",

    # Storage - comprehensive
    "cabinet", "storage cabinet", "media cabinet", "tv stand",
    "dresser", "chest of drawers", "highboy", "lowboy",
    "sideboard", "buffet", "credenza", "hutch",
    "bookcase", "bookshelf", "shelving", "wall shelf", "floating shelf",
    "armoire", "wardrobe", "closet organizer",
    "filing cabinet", "storage bin",

    # Beds - comprehensive
    "bed", "bed frame", "platform bed", "canopy bed", "four poster bed",
    "headboard", "footboard",
    "daybed", "trundle bed", "bunk bed", "loft bed",
    "murphy bed", "sleeper sofa", "sofa bed",

    # Lighting - comprehensive
    "lamp", "table lamp", "desk lamp", "bedside lamp",
    "floor lamp", "arc lamp", "torchiere",
    "pendant light", "chandelier", "ceiling light",
    "wall sconce", "wall lamp",

    # Rugs and textiles
    "rug", "area rug", "runner", "carpet", "mat",
]

STYLES_EXPANDED = [
    # Core styles
    "modern", "contemporary", "traditional", "transitional",
    "mid-century", "mid-century modern", "mcm",
    "minimalist", "scandinavian", "nordic",

    # Period styles
    "vintage", "retro", "antique",
    "art deco", "art nouveau", "victorian", "georgian",
    "colonial", "french country", "english cottage",

    # Regional/cultural styles
    "bohemian", "boho", "eclectic",
    "coastal", "nautical", "beach house",
    "farmhouse", "rustic", "country", "cottage",
    "industrial", "loft", "urban",
    "japandi", "zen", "asian-inspired", "wabi-sabi",
    "mediterranean", "spanish", "moroccan", "tuscan",
]

MATERIALS_EXPANDED = [
    # Woods - specific types
    "wood", "wooden", "solid wood", "hardwood",
    "oak", "white oak", "red oak",
    "walnut", "black walnut",
    "maple", "cherry", "mahogany", "teak", "acacia",
    "pine", "cedar", "birch", "ash", "elm", "beech",
    "bamboo", "rattan", "wicker", "cane",
    "reclaimed wood", "distressed wood", "weathered wood",

    # Metals
    "metal", "iron", "wrought iron", "cast iron",
    "steel", "stainless steel", "brushed steel",
    "brass", "bronze", "copper", "gold", "chrome", "nickel",
    "aluminum",

    # Upholstery fabrics
    "fabric", "upholstered",
    "velvet", "velour",
    "linen", "cotton", "canvas",
    "leather", "faux leather", "vegan leather", "bonded leather",
    "suede", "microfiber", "chenille",
    "boucle", "bouclé", "sherpa", "teddy",
    "tweed", "herringbone", "performance fabric",

    # Hard surfaces
    "glass", "tempered glass", "frosted glass",
    "marble", "granite", "quartz", "stone", "travertine", "slate",
    "concrete", "cement", "terrazzo",
    "ceramic", "porcelain", "tile",
    "plastic", "acrylic", "lucite", "resin",
    "lacquer", "lacquered",
]

COLORS_EXPANDED = [
    # Neutrals - detailed
    "white", "off-white", "ivory", "cream", "bone", "eggshell",
    "black", "charcoal", "ebony",
    "gray", "grey", "light gray", "dark gray", "slate", "pewter", "graphite",
    "beige", "tan", "taupe", "greige", "sand", "khaki", "camel",
    "brown", "chocolate", "espresso", "mocha", "coffee", "walnut", "chestnut",
    "cognac", "caramel", "amber", "rust", "terracotta", "sienna",

    # Blues
    "blue", "navy", "navy blue", "dark blue", "royal blue",
    "light blue", "sky blue", "baby blue", "powder blue",
    "teal", "turquoise", "aqua", "cyan", "cerulean", "indigo",

    # Greens
    "green", "dark green", "forest green", "hunter green", "emerald",
    "sage", "sage green", "olive", "olive green", "moss", "fern",
    "mint", "seafoam", "eucalyptus",

    # Warm colors
    "red", "burgundy", "wine", "maroon", "crimson", "ruby",
    "orange", "burnt orange", "coral", "peach", "apricot",
    "yellow", "mustard", "gold", "golden", "honey", "ochre",
    "pink", "blush", "rose", "dusty pink", "mauve",

    # Purples
    "purple", "plum", "eggplant", "aubergine", "violet", "lilac", "lavender",

    # Natural tones
    "natural", "nude", "neutral", "earthy", "earth tone",
]

# Texture and pattern descriptors for enhanced matching
TEXTURES = [
    "tufted", "button-tufted", "channel-tufted",
    "quilted", "padded", "cushioned",
    "woven", "braided", "knitted", "crocheted",
    "ribbed", "fluted", "grooved", "paneled",
    "smooth", "polished", "matte", "satin", "glossy",
    "textured", "embossed", "carved", "etched",
    "distressed", "weathered", "aged", "antique finish",
]

PATTERNS = [
    "solid", "plain",
    "striped", "pinstripe", "awning stripe",
    "geometric", "chevron", "herringbone", "zigzag",
    "floral", "botanical", "leaf pattern",
    "abstract", "modern pattern",
    "plaid", "checkered", "gingham",
    "ikat", "suzani", "damask", "paisley",
]


# Furniture synonym mapping for type guard
FURNITURE_SYNONYMS = {
    "sofa": ["couch", "loveseat", "settee", "sectional", "sleeper", "sofa bed"],
    "couch": ["sofa", "loveseat", "settee", "sectional"],
    "chair": ["armchair", "accent chair", "lounge chair", "club chair", "recliner", "rocker"],
    "armchair": ["chair", "accent chair", "lounge chair", "club chair"],
    "table": ["desk", "stand", "console"],
    "coffee table": ["cocktail table", "tea table"],
    "side table": ["end table", "accent table", "lamp table"],
    "nightstand": ["bedside table", "night table", "bedside stand"],
    "console table": ["sofa table", "entry table", "hallway table", "entryway table"],
    "shelf": ["bookcase", "shelving", "bookshelf", "etagere", "étagère", "wall shelf"],
    "bookcase": ["bookshelf", "shelf", "shelving", "etagere"],
    "bed": ["bedframe", "bed frame", "headboard", "platform bed", "sleigh bed"],
    "dresser": ["chest of drawers", "bureau", "chest", "highboy"],
    "cabinet": ["cupboard", "sideboard", "buffet", "credenza", "hutch", "armoire"],
    "lamp": ["light", "lighting", "fixture"],
    "floor lamp": ["standing lamp", "torchiere", "arc lamp"],
    "table lamp": ["desk lamp", "bedside lamp"],
    "rug": ["carpet", "area rug", "runner", "mat"],
    "ottoman": ["footstool", "pouf", "hassock", "footrest"],
    "bench": ["settee", "banquette", "entry bench"],
    "stool": ["bar stool", "counter stool", "barstool"],
    "desk": ["writing desk", "work desk", "computer desk", "secretary"],
    "tv stand": ["media console", "entertainment center", "media cabinet", "tv console"],
}

# Hard negative keywords that indicate non-product pages
HARD_NEGATIVES = [
    # Content/editorial
    "decor", "how to", "ideas", "tutorial", "guide", "inspiration",
    "tips", "tricks", "diy", "blog", "article", "review", "reviews",
    "best of", "top 10", "roundup", "collection of",

    # Non-furniture items (keep "only" variants to exclude covers without products)
    "poster", "print", "canvas", "wall art", "artwork", "painting",
    "pillow cover only", "cushion cover only", "slipcover only",
    "curtain", "drape",
    # Note: "pillow", "blanket", "throw" are allowed for bed component searches

    # Service-related
    "assembly", "installation", "repair", "cleaning",
    "rental", "rent", "lease",

    # Generic/non-specific
    "accessories", "misc", "lot of", "bundle",
]


# Bed component configuration for composite furniture detection
# When a bed is detected, search for these additional components
BED_COMPONENTS = {
    "bed_frame": {
        "search_terms": ["bed frame", "platform bed", "bed", "headboard"],
        "synonyms": ["bedframe", "bed frame", "platform bed", "sleigh bed", "panel bed"],
    },
    "bedding": {
        "search_terms": ["comforter", "duvet", "quilt", "bedding set"],
        "synonyms": ["comforter", "duvet", "duvet cover", "quilt", "bedspread", "bed cover"],
    },
    "throw": {
        "search_terms": ["throw blanket", "bed throw", "blanket"],
        "synonyms": ["throw", "throw blanket", "blanket", "bed blanket", "knit throw"],
    },
    "pillows": {
        "search_terms": ["bed pillow", "decorative pillow", "pillow set"],
        "synonyms": ["pillow", "pillows", "throw pillow", "accent pillow", "bed pillow", "decorative pillow"],
    },
}


# ============================================================
# Bed Detection Configuration
# Two-stage filtering to distinguish actual beds from bedroom accessories
# Only actual sleeping furniture should trigger bed component search
# ============================================================

# Primary bed indicators - terms that definitively indicate sleeping furniture
# These are checked AFTER exclusions, so multi-word terms are preferred
BED_PRIMARY_INDICATORS = [
    "bed frame", "platform bed", "sleigh bed", "canopy bed",
    "four poster", "poster bed", "panel bed", "upholstered bed",
    "storage bed", "captain's bed", "trundle bed", "bunk bed",
    "murphy bed", "daybed", "sleeper sofa", "sofa bed",
    "headboard", "footboard", "mattress", "loft bed",
    "king bed", "queen bed", "twin bed", "full bed",
]

# Exclusion terms - if these appear in the label, it's NOT a bed
# Even if "bed" appears elsewhere in the string
# Comprehensive list of all non-bed furniture types
BED_EXCLUSION_TERMS = [
    # Lighting
    "lamp", "light", "chandelier", "sconce", "pendant", "fixture",
    # Tables
    "table", "desk", "console", "coffee", "side", "end", "dining",
    # Seating (non-bed)
    "chair", "sofa", "couch", "loveseat", "sectional", "recliner",
    "bench", "stool", "ottoman", "pouf", "armchair", "rocker",
    # Storage
    "dresser", "cabinet", "shelf", "bookcase", "wardrobe", "armoire",
    "credenza", "sideboard", "buffet", "hutch", "chest",
    # Decor
    "rug", "carpet", "curtain", "drape", "mirror", "clock", "art",
    "plant", "vase", "picture", "painting", "sculpture", "frame",
    # Bedroom accessories (not the bed itself)
    "beside", "bedside", "side", "night", "reading", "accent",
    # Bedding items (accessories, not furniture)
    "pillow", "cushion", "throw", "blanket", "duvet", "comforter",
    "sheet", "coverlet", "quilt", "linens", "bedspread", "bedding",
    # Other furniture
    "vanity", "stand", "rack", "cart", "tv", "media", "entertainment",
]

# Compound terms that are definitively NOT beds (checked first for speed)
NOT_BED_COMPOUND_TERMS = [
    # Bedroom furniture (not beds)
    "bedside lamp", "bedside table", "bedside cabinet", "bedside stand",
    "bedroom lamp", "bedroom dresser", "bedroom rug", "bedroom chair",
    "bedroom curtain", "bedroom mirror", "bedroom plant", "bedroom bench",
    "bedroom vanity", "bedroom cabinet", "bedroom shelf", "bedroom art",
    "nightstand", "night stand", "night table",
    # Lamps
    "reading lamp", "table lamp", "floor lamp", "desk lamp", "wall lamp",
    "pendant lamp", "ceiling lamp", "arc lamp",
    # Living room furniture
    "coffee table", "side table", "end table", "console table",
    "tv stand", "media console", "entertainment center",
    # Bedding accessories
    "throw pillow", "bed pillow", "decorative pillow", "accent pillow",
    "throw blanket", "bed throw", "bed blanket",
    # Other
    "picture frame", "photo frame", "wall art", "wall mirror",
]


# ============================================================
# Quality Retailer Domains for Trending Products
# These are retailers known for curated, aesthetic products
# Priority is visual quality and unique designs, not just brand prestige
# ============================================================

QUALITY_RETAILER_DOMAINS = [
    # Art & Wall Decor Specialists
    "drool.com",
    "olivergal.com", 
    "art.com",
    "minted.com",
    "society6.com",
    "icanvas.com",
    "artfinder.com",
    "saatchiart.com",
    
    # Curated Home Decor
    "anthropologie.com",
    "urbanoutfitters.com",
    "cb2.com",
    "westelm.com",
    "article.com",
    "crateandbarrel.com",
    "roomandboard.com",
    "designwithinreach.com",
    "serenaandlily.com",
    "burkedecor.com",
    
    # Specialty Decor
    "etsy.com",
    "1stdibs.com",
    "chairish.com",
    "worldmarket.com",
    "zgallerie.com",
    "potterybarn.com",
    "rejuvenation.com",
    "lumens.com",
    
    # General with good curation
    "wayfair.com",
    "allmodern.com",
    "houzz.com",
    "target.com",
    "amazon.com",
]

# Store quality scores for ranking (0.0-1.0)
# Higher = better visual curation and product quality
QUALITY_RETAILER_SCORES = {
    # Art specialists (highest)
    "drool": 0.95,
    "oliver gal": 0.93,
    "olivergal": 0.93,
    "minted": 0.92,
    "art.com": 0.90,
    "saatchi art": 0.90,
    "society6": 0.88,
    "icanvas": 0.87,
    
    # Premium curated
    "anthropologie": 0.92,
    "cb2": 0.91,
    "west elm": 0.90,
    "article": 0.90,
    "room & board": 0.90,
    "design within reach": 0.89,
    "serena & lily": 0.88,
    "rejuvenation": 0.88,
    
    # Quality specialty
    "1stdibs": 0.93,
    "chairish": 0.88,
    "burke decor": 0.87,
    "z gallerie": 0.85,
    "etsy": 0.80,  # Variable quality
    
    # Good mid-tier
    "crate & barrel": 0.87,
    "pottery barn": 0.85,
    "world market": 0.82,
    "urban outfitters": 0.80,
    "lumens": 0.85,
    
    # General retailers
    "wayfair": 0.78,
    "allmodern": 0.80,
    "target": 0.75,
    "amazon": 0.65,  # Very variable quality
    
    "default": 0.70,
}


# ============================================================
# AI Product Curation Settings
# Controls how Gemini Vision evaluates product quality
# ============================================================

AI_PRODUCT_CURATION = {
    # Enable/disable AI curation (can be overridden by env var)
    "enabled": True,
    
    # Minimum quality score to include product (0.0-1.0)
    "min_quality_score": 0.5,
    
    # Maximum products to evaluate per category (cost control)
    "max_products_to_evaluate": 16,
    
    # Products per Gemini batch request
    "batch_size": 8,
    
    # Score weighting (must sum to 1.0)
    "score_weights": {
        "visual_quality": 0.35,     # Image clarity, professional photography
        "design_aesthetic": 0.35,   # Modern, premium look vs generic
        "style_match": 0.30,        # Fits requested style/room
    },
    
    # Minimum image dimensions to consider (pixels)
    "min_image_dimension": 200,
}
