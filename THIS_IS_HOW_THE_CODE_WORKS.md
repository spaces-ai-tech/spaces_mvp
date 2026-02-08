# THIS IS HOW THE CODE WORKS - Reference Documentation

## AI Interior Design Agent - Complete Codebase Analysis

---

## 1. PROJECT OVERVIEW

**Project Name**: Spaces AI - AI Interior Design Agent
**Purpose**: An AI-powered interior design platform that helps users upgrade their living spaces through intelligent design recommendations, product search, and space visualization.

**Technology Stack**:
- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: Next.js 15.4+ with React 19, TailwindCSS, Shadcn/ui components
- **Mobile**: Flutter (iOS)
- **Package Managers**: uv (backend), pnpm (frontend)

---

## 2. OVERALL PROJECT STRUCTURE

```
newtest/
├── backend/                          # FastAPI backend application
│   ├── main.py                       # FastAPI application entry point (2000+ lines)
│   ├── models.py                     # Pydantic models for all API requests/responses
│   ├── data_manager.py              # Core business logic (5800+ lines)
│   ├── config.py                     # Feature flags and configuration
│   ├── pyproject.toml                # Python dependencies
│   │
│   ├── [API Clients]
│   ├── openai_client.py              # OpenAI GPT integration
│   ├── gemini_client.py              # Google Gemini (text, vision, image generation)
│   ├── claude_client.py              # Anthropic Claude integration
│   ├── exa_client.py                 # Exa product search API
│   ├── serp_client.py                # SerpAPI for Google Shopping searches
│   ├── affiliate_client.py           # Affiliate link generation
│   ├── clip_client.py                # CLIP model for image similarity
│   │
│   ├── [Utilities]
│   ├── cache_manager.py              # Caching layer for API responses
│   ├── logger_config.py              # Structured logging
│   ├── furniture_detector.py         # YOLO-based furniture detection
│   ├── spatial_utils.py              # Marker positioning utilities
│   ├── search_utils.py               # Product search utilities
│   ├── retailer_identity.py          # Retailer domain matching
│   ├── prompt_manager.py             # Prompt template management
│   ├── prompt_optimizer.py           # VAPO prompt optimization
│   │
│   ├── prompts/                      # AI prompt templates
│   ├── url_normalizer/               # URL resolution system
│   ├── vapo/                         # Vertex AI Prompt Optimizer
│   └── scripts/                      # Utility scripts
│
├── frontend/                         # Next.js React frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Home page (project management)
│   │   │   ├── projects/[id]/page.tsx # Project detail page
│   │   │   ├── affiliate-cart/page.tsx # Affiliate cart page
│   │   │   └── layout.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ProjectsList.tsx
│   │   │   ├── ImageUploadSection.tsx
│   │   │   ├── SpaceTypeSelection.tsx
│   │   │   ├── ImageMarkerInterface.tsx
│   │   │   ├── LabelledImageDisplay.tsx
│   │   │   ├── MarkerRecommendations.tsx
│   │   │   ├── InspirationImageUpload.tsx
│   │   │   ├── InspirationRecommendations.tsx
│   │   │   ├── ProductRecommendations.tsx
│   │   │   ├── ProductSearchResults.tsx
│   │   │   ├── GeneratedImageDisplay.tsx
│   │   │   ├── InspirationRedesignDisplay.tsx
│   │   │   ├── ColorPaletteScreen.tsx
│   │   │   ├── StyleSelectionScreen.tsx
│   │   │   ├── PreferredStoresScreen.tsx
│   │   │   ├── FurnitureIdentificationPanel.tsx
│   │   │   └── [20+ other components]
│   │   │
│   │   └── lib/
│   │       ├── api.ts               # API client with React Query
│   │       └── utils.ts
│   │
│   ├── package.json
│   └── tailwind.config.js
│
├── ios-frontend/                    # Flutter iOS app
├── scripts/                         # Utility scripts
├── README.md                        # Main documentation
├── technical_architecture.md        # Architecture decisions
├── CLAUDE_SETUP.md                 # Claude API setup guide
└── env.example                      # Environment variable template
```

---

## 3. MAIN ENTRY POINTS & APPLICATION FLOW

### Backend Entry Point: `backend/main.py`

**FastAPI Application Setup**:
- Application instantiated with title "AI Interior Design Agent" and version "1.0.0"
- Root path set to `/api` (all routes prefixed with `/api`)
- CORS middleware configured for localhost:3000, 3001, 3002

### Key Endpoints (70+ total):

#### Project Management:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects` | POST | Create new project |
| `/api/projects` | GET | List all projects |
| `/api/projects/{project_id}` | GET | Get project details |
| `/api/projects/{project_id}` | DELETE | Delete project |
| `/api/projects/{project_id}/health` | GET | Health check |

#### Image Processing:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/{project_id}/upload-image` | POST | Upload base room image |
| `/api/projects/{project_id}/base-image` | GET | Retrieve base image |
| `/api/projects/{project_id}/inspiration-image` | POST | Upload inspiration image |
| `/api/projects/{project_id}/inspiration-images-batch` | POST | Batch upload inspiration images |
| `/api/projects/{project_id}/inspiration-image/{index}` | GET | Get inspiration image |
| `/api/projects/{project_id}/labelled-image` | GET | Get image with improvement markers |

#### Design Analysis:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/{project_id}/space-type` | POST | Select room type |
| `/api/projects/{project_id}/improvement-mode` | POST | Set mode (iterative/complete_revamp) |
| `/api/projects/{project_id}/improvement-markers` | POST | Save improvement markers |
| `/api/projects/{project_id}/marker-recommendations` | GET | Get marker-based recommendations |
| `/api/projects/{project_id}/apply-color-scheme` | POST | Apply color analysis (Color Agent) |
| `/api/projects/{project_id}/apply-style` | POST | Apply style analysis (Style Agent) |

#### Product Recommendations & Search:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/{project_id}/inspiration-recommendations` | POST | Generate inspiration-based recommendations |
| `/api/projects/{project_id}/product-recommendations` | POST | Generate product recommendations |
| `/api/projects/{project_id}/product-recommendation-selection` | POST | Select recommendation |
| `/api/projects/{project_id}/product-search` | POST | Search products using Exa |
| `/api/projects/{project_id}/auto-select-product` | POST | Auto-select best product |

#### Image Generation:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/{project_id}/product-selection` | POST | Select product for generation |
| `/api/projects/{project_id}/generate-image` | POST | Generate visualization with Gemini |
| `/api/projects/{project_id}/generated-image` | GET | Get generated image |
| `/api/projects/{project_id}/inspiration-redesign` | POST | Generate inspiration-based redesign |

#### Advanced Features:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/{project_id}/clip-search` | POST | CLIP-based product search on generated image |
| `/api/projects/{project_id}/analyze-furniture-batch` | POST | Batch furniture analysis |
| `/api/projects/{project_id}/reverse-search-batch` | POST | Google Lens reverse search |
| `/api/projects/{project_id}/process-furniture-selection` | POST | Process selected furniture with URL resolution |

#### Affiliate & Commerce:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/affiliate/generate-cart` | POST | Generate affiliate carts (retailer-grouped) |
| `/api/normalize-urls` | POST | Universal product URL normalizer |

### Frontend Entry Point: `frontend/src/app/page.tsx`

**Home Page Features**:
- API health check display
- Backend connection status verification
- Create new project button
- Projects list with project cards

**Project Workflow Navigation**:
```
Home (page.tsx)
└── Projects List (ProjectsList.tsx)
    └── Project Detail (projects/[id]/page.tsx)
        ├── ImageUploadSection
        ├── SpaceTypeSelection
        ├── ImprovementModeSelector
        ├── ImageMarkerInterface
        ├── MarkerRecommendations
        ├── InspirationImageUpload
        ├── InspirationRecommendations
        ├── ColorPaletteScreen
        ├── StyleSelectionScreen
        ├── PreferredStoresScreen
        ├── ProductRecommendations
        ├── ProductSearchResults
        ├── GeneratedImageDisplay
        └── InspirationRedesignDisplay
```

---

## 4. EXTERNAL APIs & SERVICES

### AI/LLM Services:

#### 1. OpenAI (GPT-5/GPT-5-mini/GPT-5-nano)
- **Location**: `openai_client.py`
- **Usage**: Text completions, structured output, prompt processing
- **Methods**: `get_completion()`, `get_structured_completion()`, `analyze_image_with_vision()`

#### 2. Google Gemini
- **Location**: `gemini_client.py`
- **Usage**: Vision API analysis, image generation, text completions
- **Models**: `gemini-2.0-flash`, `gemini-3.0-flash`, `gemini-2.0-flash-exp`
- **Methods**: `analyze_image_with_vision()`, `generate_image()`, `get_structured_completion()`

#### 3. Anthropic Claude
- **Location**: `claude_client.py`
- **Usage**: Text completions, vision analysis
- **Models**: `claude-opus-4-20250514`, `claude-sonnet-4-20250514`, `claude-3-5-haiku-20241022`
- **Interface**: Interchangeable with OpenAI/Gemini clients

### Product Search Services:

#### 1. Exa API
- **Location**: `exa_client.py`
- **Usage**: Semantic product search, web search
- **Methods**: `search()`, `find_products()`, `analyze_search_results()`

#### 2. SerpAPI (Google Shopping, Google Lens)
- **Location**: `serp_client.py`
- **Usage**: Google Shopping product discovery, reverse image search, Google Lens
- **Methods**: `search_products()`, `reverse_image_search()`, `resolve_google_shopping_url()`

### Image Processing Services:

#### 1. CLIP (Contrastive Language-Image Pre-training)
- **Location**: `clip_client.py`
- **Usage**: Image similarity matching, semantic image search
- **Models**: `ViT-L/14`, `ViT-B/32` (configurable)
- **Methods**: `encode_image()`, `encode_text()`, `find_similar_products()`

#### 2. YOLO (Object Detection)
- **Location**: `furniture_detector.py`
- **Usage**: Detect furniture objects in images
- **Model**: YOLOv8
- **Methods**: `detect_furniture()`, `segment_furniture()`

### Affiliate & Commerce:

#### 1. Affiliate Client
- **Location**: `affiliate_client.py`
- **Usage**: URL validation, affiliate link generation, retailer cart generation
- **Supported retailers**: Amazon, IKEA, Wayfair, Target, Walmart, West Elm, CB2, etc.

#### 2. URL Normalizer
- **Location**: `url_normalizer/`
- **Usage**: Resolve Google Shopping URLs to direct retailer PDPs
- **Methods**: URL redirect following, canonical extraction, classification

### AI Optimization:

#### Vertex AI Prompt Optimizer (VAPO)
- **Location**: `vapo/`
- **Usage**: A/B testing and zero-shot prompt optimization
- **Features**: Structured metrics collection, automatic suggestions

---

## 5. KEY DATA MODELS & STRUCTURES

### Project Context (in `models.py`):
```python
class ProjectContext(BaseModel):
    # Core image data
    base_image: Optional[str]
    is_base_image_empty_room: Optional[bool]
    improvement_mode: Optional[str]  # 'iterative' or 'complete_revamp'
    space_type: Optional[str]

    # Markers & recommendations
    improvement_markers: List[ImprovementMarker]
    labelled_base_image: Optional[str]
    marker_recommendations: List[str]

    # Inspiration flow
    inspiration_images: List[str]
    inspiration_recommendations: List[str]
    inspiration_generated_image_base64: Optional[str]

    # Product recommendations & selection
    product_recommendations: List[str]
    selected_product_recommendations: List[str]
    product_search_results: List[Dict]
    selected_products: List[Dict]
    generated_image_base64: Optional[str]

    # AI Analysis
    color_analysis: Optional[ColorAnalysis]  # Color Agent results
    style_analysis: Optional[StyleAnalysis]  # Style Agent results

    # User preferences
    preferred_stores: List[str]
    pre_searched_categories: Dict[str, PreSearchedCategory]
    favorite_products: List[FavoriteProduct]
    selected_trending_products: List[SelectedTrendingProduct]
```

### Color Analysis (Agent output):
```python
class ColorAnalysis(BaseModel):
    space_summary: str
    primary_colors: List[ColorSwatch]        # 60% rule
    secondary_colors: List[ColorSwatch]      # 30% rule
    accent_colors: List[ColorSwatch]         # 10% rule
    color_theory_approach: str               # Monochromatic/Analogous/Complementary/Triadic
    color_assignments: List[ColorAssignment] # Per-element color mapping
    lighting_notes: str
    cohesion_tips: str
    personalization_suggestions: str
```

### Style Analysis (Agent output):
```python
class StyleAnalysis(BaseModel):
    style_name: str
    style_overview: str
    materials: List[str]
    color_palette: List[str]
    furniture_characteristics: str
    patterns_textures: str
    lighting_style: str
    decor_accessories: str
    layout_principles: str
    styling_tips: List[str]
    common_mistakes: List[str]
    furniture_recommendations: List[FurnitureRecommendation]
    anchor_pieces: List[str]
    statement_accessory: str
    room_transformation: str
    related_styles: List[str]
```

### Improvement Marker:
```python
class ImprovementMarker(BaseModel):
    id: str
    position: MarkerPosition      # Normalized (0-1) X, Y coordinates
    description: str              # User's improvement description
    color: str                    # Visual color (red, green, blue, purple, orange)
```

### Project Status Flow:
```
NEW
→ BASE_IMAGE_UPLOADED
→ SPACE_TYPE_SELECTED
→ IMPROVEMENT_MARKERS_SAVED (if non-empty room)
→ MARKER_RECOMMENDATIONS_READY
→ INSPIRATION_IMAGES_UPLOADED (optional)
→ INSPIRATION_RECOMMENDATIONS_READY (optional)
→ PRODUCT_RECOMMENDATIONS_READY
→ PRODUCT_RECOMMENDATION_SELECTED
→ PRODUCT_SEARCH_COMPLETE
→ PRODUCT_SELECTED
→ IMAGE_GENERATED
→ INSPIRATION_REDESIGN_COMPLETE
```

---

## 6. MAIN FEATURES & FUNCTIONALITY

### Core Workflow:

#### 1. Project Creation
- Each project gets a unique UUID
- Projects stored as JSON in `/backend/data/projects.json`
- Images stored in `/backend/data/images/{project_id}/`

#### 2. Image Upload & Analysis
- Base room image upload with AI emptiness detection
- Gemini Vision API analyzes if room is furnished
- Improvement markers can be placed only on non-empty rooms

#### 3. Space Type Selection
- User selects room type (bedroom, living room, office, custom)
- Provides context for all downstream recommendations

#### 4. Improvement Mode Selection
- `iterative`: Enhancing existing setup
- `complete_revamp`: Full redesign

#### 5. Interactive Marker System
- Click-to-place markers on base image (up to 5)
- Normalized coordinates (0-1 range)
- Color-coded (red, green, blue, purple, orange)
- User describes improvement at each marker
- System generates labelled image with markers overlaid

#### 6. AI Recommendation Generation (Three Paths):

**Path 1: Marker-Based Recommendations**
- Triggered after saving improvement markers
- Uses base image + labelled image + marker descriptions
- Generates exactly 6 actionable recommendations
- Constraints: 2-4 words for product recommendations

**Path 2: Inspiration-Based Recommendations**
- User uploads inspiration images (1-5)
- Vision API analyzes style differences
- Generates 6 recommendations comparing current vs. desired look

**Path 3: Product Recommendations Synthesis**
- Combines all project context
- Synthesizes marker + inspiration recommendations
- Final unified list of 6 product recommendations

#### 7. Color & Style Analysis (Agent-Based):

**Color Agent**: Analyzes room and generates comprehensive color scheme
- 60-30-10 color rule application
- Color theory approach (Monochromatic/Analogous/Complementary/Triadic)
- Per-element color assignments
- Lighting considerations

**Style Agent**: Analyzes room and generates design style guide
- Materials and furniture characteristics
- Layout principles and spatial organization
- Styling tips and common mistakes
- Furniture recommendations specific to space

#### 8. Product Search & Selection
- Exa semantic search for product recommendations
- SerpAPI for Google Shopping product discovery
- CLIP-based image similarity matching
- Auto-selection based on:
  - CLIP similarity score
  - Image quality/availability
  - Store trust rating

#### 9. Image Generation
- Gemini 2.0 Flash generates visualized room with selected product
- Custom prompt synthesis combining:
  - Room description
  - Product details
  - Color scheme
  - Design style
- Output: Base64 encoded PNG visualization

#### 10. Inspiration Redesign
- Generates completely redesigned room based on inspiration images
- Gemini creates vision of desired look
- Parallel to product-based generation

#### 11. Advanced Features:
- **CLIP Search**: Search products by clipping region of generated image
- **Furniture Batch Analysis**: Analyze multiple furniture items with CLIP
- **Reverse Image Search**: Google Lens searches on selected regions
- **URL Normalization**: Resolve Google Shopping URLs to direct retailer URLs
- **Affiliate Cart Generation**: Group products by retailer with affiliate links

---

## 7. CONFIGURATION & ENVIRONMENT SETUP

### Environment Variables (from `env.example`):
```bash
# Claude / Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI (optional, for fallback)
OPENAI_API_KEY=...

# Google (Gemini + Cloud)
GOOGLE_API_KEY=...
GOOGLE_CLOUD_PROJECT=...

# SerpAPI
SERP_API_KEY=...

# Exa
EXA_API_KEY=...
```

### Feature Flags (in `config.py`):
```python
USE_CLIP_LARGE = True              # Use larger CLIP model
EXPANDED_VOCABULARY = True          # Enhanced furniture/style/material terms
ENHANCED_TYPE_GUARD = True          # Better synonym matching
STORE_TRUST_SCORES = True           # Weight results by retailer quality
MULTI_SIGNAL_RANKING = False        # Continuous scoring (off for safety)
```

### Store Trust Scores:
| Tier | Score Range | Retailers |
|------|-------------|-----------|
| Premium | 0.90+ | West Elm, CB2, Article, Room & Board |
| Mid-tier | 0.80+ | Wayfair, AllModern, IKEA |
| Big box | 0.65-0.75 | Target, Amazon, Walmart |
| Specialty | 0.68-0.88 | Ethan Allen, Arhaus, Z Gallerie |

### Quality Retailer Domains:
Prioritized for trending products: DroolCom, OliverGal, Anthropologie, West Elm, CB2, Crate & Barrel, Article, Etsy, 1stDibs, Chairish

### Python Dependencies (from `pyproject.toml`):
- **Core**: fastapi[standard], anthropic, openai, google-genai, google-generativeai
- **Search**: exa-py, google-search-results, requests
- **AI**: torch, transformers, ultralytics (YOLO)
- **Utilities**: pillow, python-dotenv, numpy

---

## 8. FRONTEND-BACKEND COMMUNICATION

### API Client (`frontend/src/lib/api.ts`):
- Base URL: `http://localhost:8000/api`
- React Query (TanStack Query) for all API calls
- Methods: GET, POST, DELETE with proper error handling
- File upload with FormData
- Automatic JSON serialization

### CORS Configuration:
- Allowed origins: localhost:3000, 3001, 3002
- Credentials enabled
- All HTTP methods allowed

### React Query Hooks (in `api.ts`):
- `useCreateProject()` - POST /projects
- `useGetProject(projectId)` - GET /projects/{id}
- `useGetAllProjects()` - GET /projects
- `useDeleteProject()` - DELETE /projects/{id}
- `useUploadImage()` - POST /upload-image
- `useSelectSpaceType()` - POST /space-type
- And 50+ other hooks for all endpoints

### Key UI Patterns:
- Direct component imports (no barrel exports)
- React Query for data fetching state management
- Shadcn/ui components for consistency
- TailwindCSS for styling
- TypeScript for type safety

---

## 9. DATA PERSISTENCE

### File Storage:
- **Projects Database**: `/backend/data/projects.json`
  - JSON file with all projects and their context
  - Flat structure: `{ project_id: { status, created_at, context } }`

- **Images**: `/backend/data/images/{project_id}/`
  - Base images: `base_image.jpg`
  - Labelled images: `labelled_base_image.jpg`
  - Generated images: `generated_{timestamp}.png`
  - Inspiration images: `inspiration_{index}.jpg`

### Caching:
- Response caching via `cache_manager.py`
- TTLs for different data types (colors, search results, etc.)
- Reduces API calls to expensive services

### Data Manager (`data_manager.py`):
- Core business logic for all operations (5800+ lines)
- Handles:
  - Project CRUD operations
  - Image processing workflows
  - AI recommendation generation
  - Product search coordination
  - URL normalization
  - Affiliate cart generation

---

## 10. UNIQUE ARCHITECTURAL PATTERNS

### 1. Agentic Architecture
- Color Agent: Specialized for color analysis
- Style Agent: Specialized for style analysis
- Each returns structured output (Pydantic models)
- Can switch LLM providers (OpenAI, Gemini, Claude)

### 2. Dual Recommendation Paths
- Marker-based (incremental improvements)
- Inspiration-based (vision transformation)
- Both feed into unified product recommendations

### 3. URL Normalization Layer
- Resolves Google Shopping redirects to direct retailer URLs
- Preserves retailer intent (when user selects "Quince", returns quince.com)
- Strict mode option for retailer validation

### 4. Multi-Signal Ranking
- CLIP similarity (visual match)
- Store trust scores (retailer quality)
- Image quality (photo clarity)
- Style match (design fit)

### 5. Prompt Optimization (VAPO)
- Zero-shot optimization suggestions
- Data-driven A/B testing capability
- Metrics collection for continuous improvement

### 6. Component-Based Product Discovery
- Special handling for beds (searches frame, bedding, throw, pillows separately)
- Composite furniture detection
- Bed component synthesis

---

## 11. ADDITIONAL MODULES

### Prompt System:
- `/backend/prompts/` - Stored prompt templates
- Prompt manager for version control
- Prompt optimizer for A/B testing

### URL Normalizer:
- `/backend/url_normalizer/`
- Handles Google Shopping URL resolution
- Redirect chain following
- Product page classification
- Caching layer for performance

### VAPO (Vertex AI Prompt Optimizer):
- `/backend/vapo/`
- Integrates with Google Cloud Vertex AI
- Automated prompt optimization
- Zero-shot suggestions

### Scripts:
- `/backend/scripts/` - Utility scripts for maintenance
- `/scripts/` - Root-level utility scripts

---

## 12. TESTING & DEVELOPMENT

### CLI Test Script:
- `cli.py` - Command-line interface for testing
- Tests structured output validation
- Tests vision API functionality
- Run with: `uv run python cli.py`

### Test Files:
| File | Purpose |
|------|---------|
| `test_clip.py` | CLIP integration tests |
| `test_furniture_detection.py` | YOLO detection tests |
| `test_furniture_pipeline.py` | End-to-end workflow tests |
| `test_pipeline_e2e.py` | Full workflow testing |
| `test_gemini_gen.py` | Gemini image generation tests |

---

## 13. COMPLETE USER JOURNEY

```
1. Home Page (Health check + Create Project)
   ↓
2. Upload Room Image
   ├─ AI detects if room is empty
   ├─ If empty: Skip to recommendations
   └─ If furnished: Continue to markers
   ↓
3. Select Space Type (bedroom, living room, office, custom)
   ↓
4. Select Improvement Mode (iterative or complete_revamp)
   ↓
5A. If Furnished Room → Place Improvement Markers (up to 5)
   ↓
5B. Save Markers → Generate Labelled Image + AI Recommendations
   ↓
6. (Optional) Upload Inspiration Images
   ├─ Generate Inspiration Recommendations
   └─ Compare with marker-based recommendations
   ↓
7. Apply Color Scheme (Color Agent Analysis)
   ↓
8. Apply Design Style (Style Agent Analysis)
   ↓
9. Set Preferred Retail Stores
   ↓
10. Generate Product Recommendations (synthesized from all inputs)
    ↓
11. Select Recommendation to search
    ↓
12. Search Products (Exa + SerpAPI)
    ↓
13. Auto-Select Best Product or manually select
    ↓
14. Generate Visualization (Gemini with product)
    ↓
15. (Optional) CLIP Search for additional products
    ↓
16. (Optional) Furniture Detection & Reverse Search
    ↓
17. Process Furniture Selection → Generate Affiliate Cart
    ↓
18. View Cart → Add to Retailer
```

---

## 14. QUICK REFERENCE - API CLIENT FILES

| Client File | Service | Key Methods |
|-------------|---------|-------------|
| `openai_client.py` | OpenAI GPT | `get_completion()`, `get_structured_completion()`, `analyze_image_with_vision()` |
| `gemini_client.py` | Google Gemini | `analyze_image_with_vision()`, `generate_image()`, `get_structured_completion()` |
| `claude_client.py` | Anthropic Claude | `get_completion()`, `get_structured_completion()`, `analyze_image_with_vision()` |
| `exa_client.py` | Exa Search | `search()`, `find_products()`, `analyze_search_results()` |
| `serp_client.py` | SerpAPI | `search_products()`, `reverse_image_search()`, `resolve_google_shopping_url()` |
| `clip_client.py` | CLIP Model | `encode_image()`, `encode_text()`, `find_similar_products()` |
| `affiliate_client.py` | Affiliate Links | URL validation, link generation, cart grouping |

---

## 15. SUMMARY

This is a sophisticated, production-ready AI interior design platform featuring:

- **Multi-LLM support** for resilience and cost optimization (OpenAI, Gemini, Claude)
- **Advanced AI agents** for specialized design analysis (Color Agent, Style Agent)
- **Comprehensive product search** across multiple APIs (Exa, SerpAPI, Google Lens)
- **Affiliate commerce integration** with retailer-aware URL resolution
- **Image-based ML** (CLIP for similarity, YOLO for detection)
- **Structured data flow** with Pydantic validation throughout
- **Flexible recommendation system** supporting multiple paths
- **Modern tech stack** (FastAPI, Next.js 15, React 19, React Query, TypeScript)
- **Scalable architecture** with feature flags and configuration management

---

## 16. CHANGELOG

### 2026-02-07: Retailer Links & Object Detection Fixes

#### Problem 1: Broken Google Shopping URLs
**Issue**: Product search was returning Google Shopping redirect URLs (`google.com/shopping/product/...`) instead of direct retailer links. These URLs were broken/semi-discontinued by Google.

**Solution**:
- Switched from `tbm=shop` engine to `google_shopping_light` engine in SerpAPI
- The `google_shopping_light` engine returns direct retailer URLs in the `link` field
- Updated `_extract_retailer_url()` to prioritize the `link` field

**Files Modified**:
- `backend/config.py` - Added `USE_SHOPPING_LIGHT_API` feature flag
- `backend/serp_client.py` - Switched search engine, updated URL extraction

#### Problem 2: Marker Clicking Wrong Object (Lamp → Nightstand)
**Issue**: When user clicked on a lamp sitting on a nightstand, the system incorrectly identified it as "nightstand" instead of "table lamp". Smaller items on larger furniture were being missed.

**Solution**:
- Enhanced Gemini prompt with "CLICK PROXIMITY RULE" that prioritizes the actual clicked object
- Added `_validate_click_on_primary()` method that scores items by:
  - Click containment (is click inside bbox?)
  - Smaller area preference (more specific items like lamps)
  - Distance from click to item center
- Enhanced smart selection with weighted scoring (70% area, 30% distance)

**Files Modified**:
- `backend/spatial_utils.py` - Updated Gemini prompt with click-proximity rules
- `backend/data_manager.py` - Added validation method, enhanced smart selection

**Rollback**:
- Retailer Links: Set `USE_SHOPPING_LIGHT_API=false` in environment
- Object Detection: Comment out `_validate_click_on_primary()` call

### 2026-02-07: Enhanced "Let AI Decide" for Colors and Styles

#### Problem
When users selected "Let AI Decide" for colors or styles, the AI was defaulting to safe/common choices instead of being creative.

#### Solution
Enhanced AI prompts in `backend/gemini_client.py` to encourage more creativity:

**Color Agent Enhancements**:
- Instructed AI to choose from millions of colors with specific hex codes
- Explicitly told AI NOT to default to basic colors (white, black, beige)
- Added examples of unique hex codes (soft terracotta #E8A87C, sage green #85CDCA)
- Required EXACTLY 5 distinct colors

**Style Agent Enhancements**:
- Added trending 2025-2026 styles: "Quiet Luxury", "Dopamine Decor", "Soft Brutalism", "Organic Modern"
- Added fusion styles: "Japandi", "Modern Bohemian", "Coastal Grandmother"
- Added regional styles: "Mediterranean Revival", "Desert Modern", "Pacific Northwest"
- Encouraged creating unique style fusions tailored to specific spaces

**Files Modified**:
- `backend/gemini_client.py` - Enhanced Color Agent prompt (lines ~262-280) and Style Agent prompt (lines ~683-697)

**Note**: These prompts were further optimized using VAPO (see next entry).

### 2026-02-07: VAPO-Optimized Color and Style Agent Prompts

#### Problem
Manual prompt enhancements were good but could benefit from Vertex AI Prompt Optimizer's zero-shot optimization for industry best practices.

#### Solution
Used VAPO (Vertex AI Prompt Optimizer) zero-shot mode to optimize both "Let AI Decide" prompts:

**Color Agent Optimization** (lines ~262-280):
- Guidelines applied: `Underspecified`, `RedundancyInstructions`, `Reasoning`, `Structure`
- Removed redundant creativity instructions ("BE BOLD" repeated twice)
- Added clear structure with `### TASK`, `### INSTRUCTIONS`, `### OUTPUT FORMAT` sections
- Added rationale requirement for color choices
- Removed "voodoo" words like "COMPLETE CREATIVE FREEDOM", "PERFECT"

**Style Agent Optimization** (lines ~683-697):
- Guidelines applied: `Voodoo`, `Context`, `Schema`, `FewShot`
- Removed subjective language ("world-class", "STUNNING")
- Added structured format with numbered instructions
- Added few-shot example (Wabi-Sabi Cottage for attic bedroom)
- Clearer output format specification

**Files Modified**:
- `backend/gemini_client.py` - Lines ~262-280 (Color Agent) and ~683-697 (Style Agent)

**Optimization Tool**:
- Vertex AI Prompt Optimizer (zero-shot mode)
- GCP Project: evchargingstation-451401
- SDK: `vertexai._genai.prompt_optimizer.PromptOptimizer`

**Verification**:
1. Run the app and select "Let AI Decide" for colors
2. Verify AI returns 5 creative colors with hex codes and rationale
3. Select "Let AI Decide" for styles
4. Verify AI returns a creative style recommendation with justification

### 2026-02-07: Retry Button for User-Directed Image Edits

#### Problem
Users wanted to make small adjustments to generated room images without regenerating from scratch. For example, "remove the lamp" or "add a plant in the corner."

#### Solution
Added a "Retry" button that allows users to edit the existing generated image:

**Frontend Changes** (`frontend/src/components/InspirationRedesignDisplay.tsx`):
- Added "Retry" button next to "Regenerate"
- Inline text input for user feedback (e.g., "remove the lamp")
- Uses `useRetryRedesign` hook

**Backend Changes**:
- New endpoint: `POST /projects/{project_id}/retry-redesign`
- Request body: `{ "feedback": "user's modification request" }`
- Takes existing generated image and applies surgical edits

**New Files/Methods**:
- `backend/models.py`: Added `RetryRedesignRequest` model
- `backend/main.py`: Added `/retry-redesign` endpoint
- `backend/data_manager.py`: Added `retry_inspiration_redesign()` method
- `backend/gemini_client.py`: Added `edit_room_with_feedback()` method
- `frontend/src/lib/api.ts`: Added `useRetryRedesign` hook

**VAPO-Optimized Edit Prompt**:
- Guidelines applied: `Capabilities`, `FewShot`, `Underspecified`, `RedundancyInstructions`
- Key constraints:
  - Preserve camera angle, lighting, and structure
  - Only modify what user explicitly requests
  - Photorealistic output

**Edit Operations Supported**:
- REMOVE: Delete an item, fill with background
- ADD: Insert new item where specified
- REPLACE: Swap items of similar size
- REPOSITION: Move items slightly

**Verification**:
1. Generate an initial room redesign
2. Click "Retry" button
3. Enter feedback (e.g., "remove the lamp on the nightstand")
4. Verify the edited image preserves everything except the requested change

### 2026-02-07: Enhanced Edit Prompt with Interior Design Principles

#### Problem
The edit prompt was producing results where:
- Plants were floating/elevated instead of properly grounded on the floor
- Lamp positioning was unnatural
- Missing professional interior design considerations

#### Solution
Enhanced the edit prompt with interior design expertise using VAPO optimization:

**VAPO Guidelines Applied**: `Structure`, `Underspecified`, `Reasoning`, `FewShot`

**New Interior Design Principles Added**:
1. **PROPER GROUNDING**: Objects must sit realistically on floor (gravity/physics)
2. **SCALE & PROPORTION**: Items sized appropriately (plants 4-6ft, lamps 5-6ft)
3. **PLACEMENT & BALANCE**: Corner positions, sight lines, visual balance
4. **STYLE COHESION**: Match existing color palette and design style

**Design Planning Step**: Prompt now includes chain-of-thought reasoning before editing

**UI Enhancement**: Full prompt now displayed for debugging (instead of just `[EDIT] feedback`)

**Files Modified**:
- `backend/gemini_client.py` - Updated `edit_room_with_feedback()` prompt
- `backend/data_manager.py` - Returns full prompt for UI display

---

*Last updated: February 2026*
