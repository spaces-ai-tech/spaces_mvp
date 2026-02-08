from pathlib import Path
from typing import List, Optional

from data_manager import data_manager
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from logger_config import setup_logging
from models import (
    AutoSelectProductResponse,
    ImageGenerationResponse,
    ImageUploadResponse,
    ImprovementMarkersRequest,
    ImprovementMarkersResponse,
    ImprovementModeRequest,
    ImprovementModeResponse,
    MarkerRecommendationsResponse,
    InspirationImageGenerationResponse,
    RetryRedesignRequest,
    InspirationImagesBatchUploadResponse,
    InspirationImageUploadResponse,
    InspirationRecommendationsResponse,
    ProductRecommendationSelectionRequest,
    ProductRecommendationSelectionResponse,
    ProductRecommendationsResponse,
    ProductSearchResponse,
    ProductSelectionRequest,
    ProductSelectionResponse,
    ProjectContext,
    ProjectCreateResponse,
    ProjectResponse,
    ProjectsListResponse,
    ProjectSummary,
    SpaceTypeRequest,
    SpaceTypeResponse,
    ClipSearchRequest,
    ClipSearchResponse,
    ClipAnalysisInfo,
    BatchFurnitureAnalysisRequest,
    BatchFurnitureAnalysisResponse,
    FurnitureAnalysisItem,
    ReverseSearchBatchRequest,
    ReverseSearchBatchResponse,
    SkipStepResponse,
    AffiliateCartRequest,
    AffiliateCartResponse,
    AffiliateProduct,
    AffiliateProductItem,
    RetailerCart,
    ApplyColorRequest,
    ApplyColorResponse,
    ApplyStyleRequest,
    ApplyStyleResponse,
    PreferredStoresRequest,
    PreferredStoresResponse,
    # "Like These?" Product Suggestions Feature
    PreSearchedCategory,
    FavoriteProduct,
    SearchRecommendationsRequest,
    SearchRecommendationsResponse,
    ProductSuggestionsResponse,
    FavoriteProductsRequest,
    FavoriteProductsResponse,
    # Selected Trending Products for image generation
    SelectedTrendingProduct,
    SelectedTrendingProductsRequest,
    SelectedTrendingProductsResponse,
    # Flutter API Response Models
    ColorAnalysisResponse,
    StyleAnalysisResponse,
    TrendingProductsResponse,
    ColorAnalysis,
    StyleAnalysis,
    # Process Furniture Selection Models
    SelectedFurnitureProduct,
    ResolvedProduct,
    ProcessFurnitureSelectionRequest,
    ProcessFurnitureSelectionResponse,
    # URL Normalizer Models
    NormalizeURLsRequest,
)

load_dotenv()

# Initialize logging
logger = setup_logging()

app = FastAPI(title="AI Interior Design Agent", version="1.0.0", root_path="/api")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "message": "AI Interior Design Agent is running"}


@app.get("/")
async def root():
    """Root API endpoint"""
    return {"message": "Welcome to AI Interior Design Agent API"}


@app.post("/projects", response_model=ProjectCreateResponse)
async def create_project():
    """Create a new project"""
    logger.info("Received request to create new project")
    project_id = data_manager.create_project()
    project = data_manager.get_project(project_id)

    return ProjectCreateResponse(project_id=project_id, status=project["status"])


@app.get("/projects", response_model=ProjectsListResponse)
async def get_all_projects():
    """Get all projects"""
    projects_dict = data_manager.get_all_projects()

    # Convert each project to use ProjectContext and ProjectSummary
    projects = {}
    for project_id, project_data in projects_dict.items():
        context = ProjectContext.model_validate(project_data["context"])
        projects[project_id] = ProjectSummary(
            status=project_data["status"],
            created_at=project_data["created_at"],
            context=context,
        )

    return ProjectsListResponse(projects=projects, total_count=len(projects))


@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get a project by ID"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Parse the context from dict to ProjectContext object
    context = ProjectContext.model_validate(project["context"])

    return ProjectResponse(
        project_id=project_id,
        status=project["status"],
        created_at=project["created_at"],
        context=context,
    )


@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    if not data_manager.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"status": "success", "message": f"Project {project_id} deleted successfully"}


@app.post("/projects/{project_id}/upload-image", response_model=ImageUploadResponse)
async def upload_project_image(project_id: str, image: UploadFile = File(...)):
    """Upload an image for a project"""
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        data_manager.upload_image(project_id, image, image.filename)
        project = data_manager.get_project(project_id)

        return ImageUploadResponse(project_id=project_id, status=project["status"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@app.get("/projects/{project_id}/base-image")
async def get_project_base_image(project_id: str):
    """Get the base image for a project"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])

    if context.base_image is None:
        raise HTTPException(
            status_code=404, detail="No base image found for this project"
        )

    image_path = context.base_image

    if not Path(image_path).exists():
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(image_path)


@app.get("/projects/{project_id}/labelled-image")
async def get_project_labelled_image(project_id: str):
    """Get the labelled image for a project"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])

    if context.labelled_base_image is None:
        raise HTTPException(
            status_code=404, detail="No labelled image found for this project"
        )

    image_path = context.labelled_base_image

    if not Path(image_path).exists():
        raise HTTPException(status_code=404, detail="Labelled image file not found")

    return FileResponse(image_path)


@app.post("/projects/{project_id}/space-type", response_model=SpaceTypeResponse)
async def select_project_space_type(
    project_id: str, space_type_request: SpaceTypeRequest
):
    """Select space type for a project"""
    try:
        space_type = data_manager.select_space_type(
            project_id, space_type_request.space_type
        )
        project = data_manager.get_project(project_id)

        return SpaceTypeResponse(
            project_id=project_id, space_type=space_type, status=project["status"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to select space type: {str(e)}"
        )


@app.post("/projects/{project_id}/improvement-mode", response_model=ImprovementModeResponse)
async def set_improvement_mode(project_id: str, request: ImprovementModeRequest):
    """Set the improvement mode for a project (iterative or complete_revamp)"""
    try:
        mode = data_manager.set_improvement_mode(project_id, request.mode)
        project = data_manager.get_project(project_id)

        return ImprovementModeResponse(
            project_id=project_id, mode=mode, status=project["status"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to set improvement mode: {str(e)}"
        )


@app.post(
    "/projects/{project_id}/improvement-markers",
    response_model=ImprovementMarkersResponse,
)
async def save_improvement_markers(
    project_id: str, markers_request: ImprovementMarkersRequest
):
    """Save improvement markers for a project"""
    try:
        labelled_image_path = data_manager.save_improvement_markers(
            project_id, markers_request.markers
        )
        project = data_manager.get_project(project_id)

        return ImprovementMarkersResponse(
            project_id=project_id,
            markers=markers_request.markers,
            labelled_image_path=labelled_image_path,
            status=project["status"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save improvement markers: {str(e)}"
        )


@app.get(
    "/projects/{project_id}/marker-recommendations",
    response_model=MarkerRecommendationsResponse,
)
async def get_marker_recommendations(project_id: str):
    """Get AI-generated recommendations for improvement markers"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["status"] != "MARKER_RECOMMENDATIONS_READY":
        raise HTTPException(
            status_code=400, detail="Project is not ready for recommendations"
        )

    context = ProjectContext.model_validate(project["context"])

    if not context.marker_recommendations:
        raise HTTPException(
            status_code=404, detail="No marker recommendations found for this project"
        )

    return MarkerRecommendationsResponse(
        project_id=project_id,
        space_type=context.space_type or "unknown",
        recommendations=context.marker_recommendations,
        status=project["status"],
    )


@app.post(
    "/projects/{project_id}/marker-recommendations",
    response_model=MarkerRecommendationsResponse,
)
async def generate_marker_recommendations(project_id: str):
    """Generate marker-based AI recommendations when the project is ready (color/style/stores set)."""
    try:
        recs = data_manager.trigger_marker_recommendations(project_id)
        project = data_manager.get_project(project_id)
        context = ProjectContext.model_validate(project["context"])
        return MarkerRecommendationsResponse(
            project_id=project_id,
            space_type=context.space_type or "unknown",
            recommendations=recs,
            status=project["status"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate marker recommendations: {str(e)}")


@app.post(
    "/projects/{project_id}/inspiration-image",
    response_model=InspirationImageUploadResponse,
)
async def upload_inspiration_image(project_id: str, image: UploadFile = File(...)):
    """Upload an inspiration image for a project"""
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_path = data_manager.upload_inspiration_image(
            project_id, image, image.filename
        )
        project = data_manager.get_project(project_id)

        return InspirationImageUploadResponse(
            project_id=project_id, image_path=image_path, status=project["status"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload inspiration image: {str(e)}"
        )


@app.post(
    "/projects/{project_id}/inspiration-images-batch",
    response_model=InspirationImagesBatchUploadResponse,
)
async def upload_inspiration_images_batch(
    project_id: str, images: List[UploadFile] = File(...)
):
    """Upload multiple inspiration images for a project in one batch"""
    # Validate all files are images
    for image in images:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail=f"File {image.filename} is not an image"
            )

    try:
        image_paths = data_manager.upload_inspiration_images_batch(project_id, images)
        project = data_manager.get_project(project_id)

        return InspirationImagesBatchUploadResponse(
            project_id=project_id,
            image_paths=image_paths,
            uploaded_count=len(image_paths),
            status=project["status"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload inspiration images: {str(e)}"
        )


@app.get("/projects/{project_id}/inspiration-image/{image_index}")
async def get_inspiration_image(project_id: str, image_index: int):
    """Get an inspiration image for a project by index"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])

    if not context.inspiration_images:
        raise HTTPException(
            status_code=404, detail="No inspiration images found for this project"
        )

    if image_index >= len(context.inspiration_images):
        raise HTTPException(
            status_code=404, detail="Inspiration image index out of range"
        )

    image_path = context.inspiration_images[image_index]

    if not Path(image_path).exists():
        raise HTTPException(status_code=404, detail="Inspiration image file not found")

    return FileResponse(image_path)


@app.post(
    "/projects/{project_id}/inspiration-recommendations",
    response_model=InspirationRecommendationsResponse,
)
async def generate_inspiration_recommendations(project_id: str):
    """Generate AI recommendations based on inspiration images"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["status"] not in [
        "INSPIRATION_IMAGES_UPLOADED",
        "INSPIRATION_RECOMMENDATIONS_READY",
    ]:
        raise HTTPException(
            status_code=400,
            detail="Project is not ready for inspiration recommendations",
        )

    try:
        recommendations = data_manager.generate_inspiration_recommendations(project_id)
        project = data_manager.get_project(project_id)
        context = ProjectContext.model_validate(project["context"])

        return InspirationRecommendationsResponse(
            project_id=project_id,
            space_type=context.space_type or "unknown",
            recommendations=recommendations,
            status=project["status"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate inspiration recommendations: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/inspiration-redesign",
    response_model=InspirationImageGenerationResponse,
)
async def generate_inspiration_redesign(project_id: str):
    """Generate a redesigned room image based on inspiration recommendations"""
    logger.info(
        "API request: generate inspiration redesign",
        extra={"project_id": project_id},
    )
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if project has inspiration recommendations OR product recommendations
    context = ProjectContext.model_validate(project["context"])
    has_inspiration_recs = (
        context.inspiration_recommendations 
        and len(context.inspiration_recommendations) > 0
    )
    has_product_recs = (
        context.product_recommendations
        and len(context.product_recommendations) > 0
    )
    
    if not has_inspiration_recs and not has_product_recs:
        logger.warning(
            "Project has no inspiration or product recommendations",
            extra={
                "project_id": project_id,
                "current_status": project["status"],
                "has_inspiration_recs": False,
                "has_product_recs": False,
            },
        )
        raise HTTPException(
            status_code=400,
            detail="Project must have either inspiration or product recommendations first.",
        )

    try:
        logger.info(
            "Starting inspiration redesign",
            extra={
                "project_id": project_id,
                "current_status": project["status"],
            },
        )
        result = data_manager.generate_inspiration_redesign(project_id)

        logger.info(
            "Inspiration redesign generated successfully",
            extra={
                "project_id": project_id,
                "image_len": len(result.get("generated_image_base64", "")),
            },
        )
        return InspirationImageGenerationResponse(
            project_id=project_id,
            generated_image_base64=result["generated_image_base64"],
            inspiration_prompt=result["inspiration_prompt"],
            inspiration_recommendations=result["inspiration_recommendations"],
            status=result["status"],
            message=result["message"],
            model_used=result.get("model_used"),
        )
    except ValueError as e:
        logger.error(
            "Inspiration redesign failed: ValueError",
            extra={"project_id": project_id, "error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(
            "Inspiration redesign failed: Unexpected error",
            extra={
                "project_id": project_id,
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate inspiration redesign: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/retry-redesign",
    response_model=InspirationImageGenerationResponse,
)
async def retry_redesign(project_id: str, request: RetryRedesignRequest):
    """
    Apply user-directed modifications to the existing generated image.

    This is a SURGICAL EDIT operation - takes the last generated image
    and applies only the specific changes the user requested.

    Examples:
        - "remove the lamp on the nightstand"
        - "add a plant in the corner"
        - "replace the blue sofa with a grey one"
    """
    logger.info(
        "API request: retry redesign",
        extra={"project_id": project_id, "feedback": request.feedback[:100]},
    )
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if project has a generated image to edit
    context = ProjectContext.model_validate(project["context"])
    if not context.inspiration_generated_image_base64:
        raise HTTPException(
            status_code=400,
            detail="No generated image available to edit. Please generate an image first.",
        )

    try:
        logger.info(
            "Starting retry redesign",
            extra={
                "project_id": project_id,
                "feedback": request.feedback[:100],
            },
        )
        result = data_manager.retry_inspiration_redesign(project_id, request.feedback)

        logger.info(
            "Retry redesign completed successfully",
            extra={
                "project_id": project_id,
                "image_len": len(result.get("generated_image_base64", "")),
            },
        )
        return InspirationImageGenerationResponse(
            project_id=project_id,
            generated_image_base64=result["generated_image_base64"],
            inspiration_prompt=result["inspiration_prompt"],
            inspiration_recommendations=result["inspiration_recommendations"],
            status=result["status"],
            message=result["message"],
            model_used=result.get("model_used"),
        )
    except ValueError as e:
        logger.error(
            "Retry redesign failed: ValueError",
            extra={"project_id": project_id, "error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(
            "Retry redesign failed: Unexpected error",
            extra={
                "project_id": project_id,
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit image: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/apply-color-scheme",
    response_model=ApplyColorResponse,
)
async def apply_color_scheme(project_id: str, color_request: ApplyColorRequest):
    """Apply a color scheme to the project using the Color Agent for analysis"""
    logger.info(
        "API request: apply color scheme",
        extra={
            "project_id": project_id,
            "palette_name": color_request.palette_name,
            "let_ai_decide": color_request.let_ai_decide,
        },
    )
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])

    # Need at least a base image and space type
    if not context.base_image or not context.space_type:
        raise HTTPException(
            status_code=400,
            detail="Project must have a base image and space type selected first",
        )

    try:
        logger.info(
            "Starting Color Agent analysis",
            extra={
                "project_id": project_id,
                "palette_name": color_request.palette_name,
            },
        )
        
        color_analysis = data_manager.apply_color_scheme(
            project_id,
            color_request.palette_name,
            color_request.colors,
            color_request.let_ai_decide,
        )

        logger.info(
            "Color Agent analysis complete",
            extra={"project_id": project_id},
        )

        from models import ColorAnalysis
        return ApplyColorResponse(
            project_id=project_id,
            palette_name=color_request.palette_name,
            color_analysis=ColorAnalysis.model_validate(color_analysis),
            status="success",
        )
    except ValueError as e:
        logger.error(
            "Color scheme application failed: ValueError",
            extra={"project_id": project_id, "error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(
            "Color scheme application failed: Unexpected error",
            extra={
                "project_id": project_id,
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply color scheme: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/apply-style",
    response_model=ApplyStyleResponse,
)
async def apply_style(project_id: str, style_request: ApplyStyleRequest):
    """Apply an interior design style to the project using the Style Agent for analysis"""
    logger.info(
        "API request: apply style",
        extra={
            "project_id": project_id,
            "style_name": style_request.style_name,
            "let_ai_decide": style_request.let_ai_decide,
        },
    )
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])

    # Need at least a base image and space type
    if not context.base_image or not context.space_type:
        raise HTTPException(
            status_code=400,
            detail="Project must have a base image and space type selected first",
        )

    try:
        logger.info(
            "Starting Style Agent analysis",
            extra={
                "project_id": project_id,
                "style_name": style_request.style_name,
            },
        )
        
        style_analysis = data_manager.apply_style(
            project_id,
            style_request.style_name,
            style_request.let_ai_decide,
        )

        logger.info(
            "Style Agent analysis complete",
            extra={"project_id": project_id},
        )

        from models import StyleAnalysis
        return ApplyStyleResponse(
            project_id=project_id,
            style_name=style_request.style_name,
            style_analysis=StyleAnalysis.model_validate(style_analysis),
            status="success",
        )
    except ValueError as e:
        logger.error(
            "Style application failed: ValueError",
            extra={"project_id": project_id, "error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(
            "Style application failed: Unexpected error",
            extra={
                "project_id": project_id,
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply style: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/skip-color-analysis",
    response_model=SkipStepResponse,
)
async def skip_color_analysis(project_id: str):
    """Skip color analysis to unblock downstream steps."""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])
    if not context.base_image or not context.space_type:
        raise HTTPException(
            status_code=400,
            detail="Project must have a base image and space type selected first",
        )

    try:
        data_manager.skip_color_analysis(project_id)
        project = data_manager.get_project(project_id)
        return SkipStepResponse(
            project_id=project_id,
            status=project["status"],
            skipped_step="color_analysis",
            message="Color analysis skipped",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to skip color analysis: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/skip-style-analysis",
    response_model=SkipStepResponse,
)
async def skip_style_analysis(project_id: str):
    """Skip style analysis to unblock downstream steps."""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])
    if not context.base_image or not context.space_type:
        raise HTTPException(
            status_code=400,
            detail="Project must have a base image and space type selected first",
        )

    try:
        data_manager.skip_style_analysis(project_id)
        project = data_manager.get_project(project_id)
        return SkipStepResponse(
            project_id=project_id,
            status=project["status"],
            skipped_step="style_analysis",
            message="Style analysis skipped",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to skip style analysis: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/skip-inspiration-images",
    response_model=SkipStepResponse,
)
async def skip_inspiration_images(project_id: str):
    """Skip inspiration images to unblock downstream steps."""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])
    if not context.base_image or not context.space_type:
        raise HTTPException(
            status_code=400,
            detail="Project must have a base image and space type selected first",
        )

    try:
        data_manager.skip_inspiration_images(project_id)
        project = data_manager.get_project(project_id)
        return SkipStepResponse(
            project_id=project_id,
            status=project["status"],
            skipped_step="inspiration_images",
            message="Inspiration images skipped",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to skip inspiration images: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/preferred-stores",
    response_model=PreferredStoresResponse,
)
async def update_preferred_stores(
    project_id: str, store_request: PreferredStoresRequest
):
    """Update user's preferred retail stores in the project context"""
    logger.info(
        "API request: update preferred stores",
        extra={
            "project_id": project_id,
            "stores": store_request.stores,
        },
    )
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        updated_stores = data_manager.update_preferred_stores(
            project_id, store_request.stores
        )

        return PreferredStoresResponse(
            project_id=project_id,
            stores=updated_stores,
            status="success",
        )
    except Exception as e:
        import traceback
        logger.error(
            "Update preferred stores failed: Unexpected error",
            extra={
                "project_id": project_id,
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferred stores: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/product-recommendations",
    response_model=ProductRecommendationsResponse,
)
async def generate_product_recommendations(project_id: str):
    """Generate AI product recommendations based on project context"""
    logger.info(
        "API request: generate product recommendations",
        extra={"project_id": project_id},
    )
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        logger.info(
            "Generating product recommendations",
            extra={"project_id": project_id, "current_status": project["status"]},
        )

        recommendations = data_manager.generate_product_recommendations(project_id)
        project = data_manager.get_project(project_id)
        context = ProjectContext.model_validate(project["context"])

        logger.info(
            "Product recommendations generated successfully",
            extra={
                "project_id": project_id,
                "recommendations_count": len(recommendations),
                "new_status": project["status"],
            },
        )

        return ProductRecommendationsResponse(
            project_id=project_id,
            space_type=context.space_type or "unknown",
            recommendations=recommendations,
            status=project["status"],
        )
    except ValueError as e:
        logger.error(
            "Product recommendations generation failed: ValueError",
            extra={"project_id": project_id, "error": str(e)},
        )
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            "Product recommendations generation failed: Unexpected error",
            extra={
                "project_id": project_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate product recommendations: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/product-recommendation-selection",
    response_model=ProductRecommendationSelectionResponse,
)
async def select_product_recommendation(
    project_id: str, selection_request: ProductRecommendationSelectionRequest
):
    """Select a product recommendation option"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_statuses = [
        "PRODUCT_RECOMMENDATIONS_READY",
        "INSPIRATION_RECOMMENDATIONS_READY",
        "PRODUCT_RECOMMENDATION_SELECTED",
        "PRODUCT_SEARCH_COMPLETE",
        "PRODUCT_SELECTED",
        "IMAGE_GENERATED",
        "INSPIRATION_REDESIGN_COMPLETE"
    ]
    
    if project["status"] not in allowed_statuses:
        # Fallback: check if we actually have recommendations in context, if so, we might allow it (legacy projects/weird states)
        context = ProjectContext.model_validate(project["context"])
        has_recs = (context.product_recommendations and len(context.product_recommendations) > 0) or \
                   (context.inspiration_recommendations and len(context.inspiration_recommendations) > 0)
        
        if not has_recs:
             raise HTTPException(
                status_code=400,
                detail="Project must have product or inspiration recommendations ready first",
            )

    try:
        selected = data_manager.select_product_recommendation(
            project_id, selection_request.selected_recommendation
        )
        project = data_manager.get_project(project_id)

        return ProductRecommendationSelectionResponse(
            project_id=project_id,
            selected_recommendations=selected,
            status=project["status"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to select product recommendation: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/product-search",
    response_model=ProductSearchResponse,
)
async def search_products(project_id: str):
    """Search for products based on selected recommendation using AI and Exa"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["status"] != "PRODUCT_RECOMMENDATION_SELECTED":
        raise HTTPException(
            status_code=400,
            detail="Project must have a selected product recommendation first",
        )

    try:
        search_result = data_manager.search_products(project_id)
        project = data_manager.get_project(project_id)
        context = ProjectContext.model_validate(project["context"])

        return ProductSearchResponse(
            project_id=project_id,
            selected_recommendations=context.selected_product_recommendations,
            search_query=search_result["search_query"],
            products=search_result["products"],
            total_found=search_result["total_found"],
            status=project["status"],
            message=f"Found {search_result['total_found']} products for your selections",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search for products: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/auto-select-product",
    response_model=AutoSelectProductResponse,
)
async def auto_select_product(project_id: str):
    """
    Auto-select the best product from search results based on:
    - CLIP similarity score (visual match)
    - Image quality/availability
    - Store trust rating
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])
    products = context.product_search_results or []

    if not products:
        raise HTTPException(
            status_code=400,
            detail="No products available. Run product search first.",
        )

    try:
        result = data_manager.auto_select_best_product(project_id, products)
        return AutoSelectProductResponse(
            project_id=project_id,
            selected_product=result["selected_product"],
            selection_reason=result["selection_reason"],
            alternatives=result["alternatives"],
            status="PRODUCT_AUTO_SELECTED",
            message=f"Auto-selected: {result['selected_product'].get('title', 'Unknown')}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to auto-select product: {str(e)}",
        )


# ============================================================================
# "Like These?" Product Suggestions Feature
# ============================================================================

@app.post(
    "/projects/{project_id}/search-recommendations",
    response_model=SearchRecommendationsResponse,
)
async def search_products_for_recommendations(
    project_id: str,
    request: SearchRecommendationsRequest
):
    """
    Search for real products matching selected recommendations.
    Called when user proceeds from Product Recommendations screen to 'Like These?' view.
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = data_manager.search_products_for_recommendations(
            project_id,
            request.recommendations
        )

        return SearchRecommendationsResponse(
            project_id=project_id,
            categories=[PreSearchedCategory(**cat) for cat in result["categories"]],
            total_products=result["total_products"],
            status=result["status"],
            message=result["message"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search products for recommendations: {str(e)}",
        )


@app.get(
    "/projects/{project_id}/product-suggestions",
    response_model=ProductSuggestionsResponse,
)
async def get_product_suggestions(project_id: str):
    """
    Get pre-searched products organized by recommendation category.
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = data_manager.get_pre_searched_suggestions(project_id)

        return ProductSuggestionsResponse(
            project_id=project_id,
            categories=[PreSearchedCategory(**cat) for cat in result["categories"]],
            total_products=result["total_products"],
            overall_status=result["overall_status"],
            message=result["message"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product suggestions: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/favorite-products",
    response_model=FavoriteProductsResponse,
)
async def set_favorite_products(
    project_id: str,
    request: FavoriteProductsRequest
):
    """
    Save user's favorite product selections from the 'Like These?' screen.
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = data_manager.set_favorite_products(
            project_id,
            [fav.model_dump() for fav in request.favorites]
        )

        return FavoriteProductsResponse(
            project_id=project_id,
            favorites_count=result["favorites_count"],
            favorites_by_category=result["favorites_by_category"],
            status=result["status"],
            message=result["message"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save favorite products: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/selected-trending-products",
    response_model=SelectedTrendingProductsResponse,
)
async def set_selected_trending_products(
    project_id: str,
    request: SelectedTrendingProductsRequest
):
    """
    Save user's selected trending products for image generation.
    These product images will be passed to Gemini for visual representation.
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = data_manager.set_selected_trending_products(
            project_id,
            [prod.model_dump() for prod in request.products]
        )

        return SelectedTrendingProductsResponse(
            project_id=project_id,
            products_count=result["products_count"],
            products_by_category=result["products_by_category"],
            status=result["status"],
            message=result["message"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save selected trending products: {str(e)}",
        )


# ============================================================================
# Flutter API GET Endpoints
# ============================================================================

@app.get(
    "/projects/{project_id}/color-analysis",
    response_model=ColorAnalysisResponse,
)
async def get_color_analysis(project_id: str):
    """
    Get color analysis results for Flutter app.
    Returns the ColorAnalysis object with palettes, assignments, and tips.
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        context = ProjectContext.model_validate(project["context"])

        color_analysis = None
        if context.color_analysis:
            color_analysis = ColorAnalysis.model_validate(context.color_analysis)

        status = "success"
        message = "Color analysis retrieved successfully"
        if context.color_analysis_skipped:
            status = "skipped"
            message = "Color analysis was skipped by user"
        elif not color_analysis:
            status = "not_available"
            message = "Color analysis has not been performed yet"

        return ColorAnalysisResponse(
            project_id=project_id,
            color_analysis=color_analysis,
            skipped=context.color_analysis_skipped,
            status=status,
            message=message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get color analysis: {str(e)}",
        )


@app.get(
    "/projects/{project_id}/style-analysis",
    response_model=StyleAnalysisResponse,
)
async def get_style_analysis(project_id: str):
    """
    Get style analysis results for Flutter app.
    Returns the StyleAnalysis object with materials, furniture recommendations, and styling tips.
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        context = ProjectContext.model_validate(project["context"])

        style_analysis = None
        if context.style_analysis:
            style_analysis = StyleAnalysis.model_validate(context.style_analysis)

        status = "success"
        message = "Style analysis retrieved successfully"
        if context.style_analysis_skipped:
            status = "skipped"
            message = "Style analysis was skipped by user"
        elif not style_analysis:
            status = "not_available"
            message = "Style analysis has not been performed yet"

        return StyleAnalysisResponse(
            project_id=project_id,
            style_analysis=style_analysis,
            skipped=context.style_analysis_skipped,
            status=status,
            message=message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get style analysis: {str(e)}",
        )


@app.get(
    "/projects/{project_id}/trending-products",
    response_model=TrendingProductsResponse,
)
async def get_trending_products(project_id: str):
    """
    Get trending products data for Flutter app.
    Returns pre-searched categories, selected trending products, and favorite products.
    """
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        context = ProjectContext.model_validate(project["context"])

        # Convert pre_searched_categories dict to list
        categories = []
        if context.pre_searched_categories:
            for cat_data in context.pre_searched_categories.values():
                categories.append(PreSearchedCategory.model_validate(cat_data))

        # Convert selected_trending_products
        selected_products = []
        if context.selected_trending_products:
            for prod in context.selected_trending_products:
                selected_products.append(SelectedTrendingProduct.model_validate(prod))

        # Convert favorite_products
        favorite_products = []
        if context.favorite_products:
            for prod in context.favorite_products:
                favorite_products.append(FavoriteProduct.model_validate(prod))

        return TrendingProductsResponse(
            project_id=project_id,
            categories=categories,
            selected_products=selected_products,
            favorite_products=favorite_products,
            status="success",
            message="Trending products retrieved successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trending products: {str(e)}",
        )


@app.post(
    "/projects/{project_id}/product-selection",
    response_model=ProductSelectionResponse,
)
async def select_product_for_generation(
    project_id: str, selection_request: ProductSelectionRequest
):
    """Select a product for Gemini image generation"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Do not hard-block on project status here; the data manager will validate
    # that the context is ready for product selection (has search results, etc.).

    try:
        selected = data_manager.select_product_for_generation(
            project_id,
            selection_request.product_url,
            selection_request.product_title,
            selection_request.product_image_url,
            selection_request.generation_prompt,
            selection_request.color_scheme,
            selection_request.design_style,
        )

        return ProductSelectionResponse(
            project_id=project_id,
            selected_products=selected["selected_products"],
            status="success",
            message=selected["message"],
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"❌ PRODUCT SELECTION ERROR: {str(e)}")
        print(f"❌ FULL TRACEBACK:\n{error_details}")
        logger.error(f"Product selection failed for project {project_id}: {str(e)}")
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=500, detail=f"Failed to select product: {str(e)}"
        )


@app.post(
    "/projects/{project_id}/generate-image",
    response_model=ImageGenerationResponse,
)
async def generate_product_visualization(project_id: str):
    """Generate a new image visualization using Gemini with the selected product"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["status"] != "PRODUCT_SELECTED":
        raise HTTPException(
            status_code=400,
            detail="Project must have a selected product first",
        )

    try:
        generation_result = data_manager.generate_product_visualization(project_id)

        return ImageGenerationResponse(
            project_id=project_id,
            selected_products=generation_result["selected_products"],
            generated_image_base64=generation_result["generated_image_base64"],
            generation_prompt=generation_result["generation_prompt"],
            status="success",
            message=generation_result["message"],
            model_used=generation_result.get("model_used"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate image: {str(e)}"
        )


@app.get("/projects/{project_id}/generated-image")
async def get_generated_image(project_id: str):
    """Serve the generated image for a project"""
    project = data_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = ProjectContext.model_validate(project["context"])

    if not context.generated_image_path:
        raise HTTPException(
            status_code=404, detail="No generated image found for this project"
        )

    image_path = Path(context.generated_image_path)

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Generated image file not found")

    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        filename=f"generated_visualization_{project_id}.png",
    )


@app.post(
    "/projects/{project_id}/clip-search",
    response_model=ClipSearchResponse,
)
async def clip_search_products(project_id: str, req: ClipSearchRequest):
    """Perform a product search based on a clipped region of the generated image."""
    project = data_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        search_result = data_manager.clip_search_products(
            project_id, 
            req.rect,
            use_inspiration_image=req.use_inspiration_image or False
        )
        
        # Construct CLIP analysis info if available
        clip_analysis_info = None
        if "clip_analysis" in search_result and search_result["clip_analysis"]:
            clip_analysis_info = ClipAnalysisInfo(**search_result["clip_analysis"])
        
        return ClipSearchResponse(
            project_id=project_id,
            rect=req.rect,
            search_query=search_result["search_query"],
            products=search_result["products"],
            total_found=search_result["total_found"],
            status="success",
            message=f"Found {search_result['total_found']} products for clipped region",
            analysis_method=search_result.get("analysis_method", "vision"),
            clip_analysis=clip_analysis_info,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed clip-search: {str(e)}")


@app.post(
    "/projects/{project_id}/analyze-furniture-batch",
    response_model=BatchFurnitureAnalysisResponse,
)
async def analyze_furniture_batch(project_id: str, req: BatchFurnitureAnalysisRequest):
    """Analyze multiple furniture items in a batch using CLIP and AI."""
    project = data_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Call data manager to analyze all selections
        analysis_results = data_manager.analyze_furniture_batch(
            project_id,
            req.selections,
            image_type=req.image_type
        )
        
        return BatchFurnitureAnalysisResponse(
            project_id=project_id,
            selections=analysis_results["selections"],
            overall_analysis=analysis_results.get("overall_analysis", ""),
            total_items=len(analysis_results["selections"]),
            status="success",
            message=f"Analyzed {len(analysis_results['selections'])} furniture items"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to analyze furniture batch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze furniture: {str(e)}")


@app.post(
    "/projects/{project_id}/process-furniture-selection",
    response_model=ProcessFurnitureSelectionResponse,
)
async def process_furniture_selection(
    project_id: str,
    request: ProcessFurnitureSelectionRequest
):
    """
    Process selected furniture products:
    - Resolve Google Shopping URLs to direct retailer URLs using Exa
    - Group products by retailer
    - Generate affiliate links and cart URLs

    This endpoint is called after furniture analysis when user selects products
    and clicks "Process Selected".
    """
    project = data_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = data_manager.process_furniture_selection(
            project_id,
            [p.model_dump() for p in request.selected_products]
        )

        return ProcessFurnitureSelectionResponse(
            project_id=project_id,
            resolved_products=[ResolvedProduct(**p) for p in result["resolved_products"]],
            retailer_carts=[RetailerCart(**c) for c in result["retailer_carts"]],
            total_products=result["total_products"],
            resolved_count=result["resolved_count"],
            unresolved_count=result["unresolved_count"],
            status="success",
            message=f"Processed {result['total_products']} products into {len(result['retailer_carts'])} retailer cart(s)"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process furniture selection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process furniture selection: {str(e)}"
        )


@app.post(
    "/projects/{project_id}/reverse-search-batch",
    response_model=ReverseSearchBatchResponse,
)
async def reverse_search_batch(project_id: str, req: ReverseSearchBatchRequest):
    """Perform Google Lens reverse image search on multiple selections."""
    project = data_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = data_manager.reverse_search_batch(
            project_id,
            req.selections,
            image_type=req.image_type,
        )
        return ReverseSearchBatchResponse(
            project_id=project_id,
            results=result["results"],
            total_items=len(result["results"]),
            status="success",
            message=f"Reverse searched {len(result['results'])} items",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed reverse-search-batch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed reverse-search: {str(e)}")


@app.get("/projects/{project_id}/auto-detect")
async def auto_detect(project_id: str, image_type: str = "product"):
    """Auto-detect furniture objects (YOLO if available)."""
    project = data_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = data_manager.auto_detect_furniture(project_id, image_type=image_type)
        return {"project_id": project_id, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Auto-detect failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Auto-detect failed: {str(e)}")


@app.get("/projects/{project_id}/replicate-segment")
async def replicate_segment(project_id: str, image_type: str = "product", image_url: Optional[str] = None):
    """Segment with Replicate (Mask2Former). If image_url is None, fallback to YOLO."""
    try:
        result = data_manager.replicate_segment(project_id, image_type=image_type, public_image_url=image_url)
        return {"project_id": project_id, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Replicate segment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Replicate segment failed: {str(e)}")


# ============================================================================
# Affiliate Cart Endpoints
# ============================================================================


@app.post("/affiliate/generate-cart", response_model=AffiliateCartResponse)
async def generate_affiliate_cart(request: AffiliateCartRequest):
    """
    Generate affiliate cart from product URLs with RETAILER-PRESERVING resolution.

    KEY BEHAVIOR:
    - When user selects a "Quince" product, we return quince.com PDP (not Walmart/Target)
    - Uses retailer identity scoring to select best candidate
    - In strict_mode (default), fails instead of returning wrong retailer

    API Options:
    1. NEW (recommended): Use 'items' with retailer_hint for retailer-preserving resolution
    2. LEGACY: Use 'product_urls' for backward compatibility (non-strict resolution)
    """
    from urllib.parse import urlparse

    try:
        from affiliate_client import AffiliateClient
        from serp_client import SerpClient

        affiliate_client = AffiliateClient()
        serp_client = None

        # Try to load retailer identity service
        try:
            from retailer_identity import retailer_identity_service
        except ImportError:
            retailer_identity_service = None
            logger.warning("[AFFILIATE] RetailerIdentityService not available")

        # ============================================================
        # Determine input mode: new 'items' API vs legacy 'product_urls'
        # ============================================================
        use_items_api = request.items and len(request.items) > 0
        strict_mode = request.strict_mode

        if use_items_api:
            items = request.items
            logger.info(f"[AFFILIATE] Using items API with {len(items)} items (strict_mode={strict_mode})")
        else:
            # Legacy mode: convert product_urls to items without retailer hints
            product_urls = request.product_urls or []
            items = [
                type('obj', (object,), {
                    'shopping_url': url,
                    'retailer_hint': None,
                    'expected_domain': None,
                    'title': None,
                })()
                for url in product_urls
            ]
            # Legacy mode uses non-strict by default
            strict_mode = False
            logger.info(f"[AFFILIATE] Using legacy product_urls API with {len(items)} URLs (strict_mode=False)")

        # ============================================================
        # STEP 1: Resolve URLs with retailer-preserving logic
        # ============================================================
        resolved_products = []  # List of {original_url, resolved_url, expected_retailer, actual_retailer, ...}
        resolution_stats = {
            "total": len(items),
            "google_shopping_count": 0,
            "resolved_count": 0,
            "retailer_matched_count": 0,
            "failed_count": 0,
        }

        for item in items:
            url = item.shopping_url.strip() if hasattr(item, 'shopping_url') else str(item).strip()
            if not url:
                continue

            retailer_hint = getattr(item, 'retailer_hint', None)
            expected_domain = getattr(item, 'expected_domain', None)
            product_title = getattr(item, 'title', None)

            # Resolve domain from retailer hint if not provided
            if retailer_hint and not expected_domain and retailer_identity_service:
                expected_domain = retailer_identity_service.resolve_brand_to_domain(retailer_hint)

            logger.info(f"[AFFILIATE] Processing: {url[:60]}... (expected: {retailer_hint or expected_domain or 'any'})")

            # Check if it's a Google Shopping URL
            is_google_shopping = (
                "ibp=oshop" in url.lower() or
                ("google.com/search" in url.lower() and "tbm=shop" in url.lower()) or
                "google.com/shopping" in url.lower()
            )

            if is_google_shopping:
                resolution_stats["google_shopping_count"] += 1

                # Initialize SerpClient lazily
                if serp_client is None:
                    try:
                        serp_client = SerpClient()
                    except Exception as e:
                        logger.error(f"[AFFILIATE] Failed to initialize SerpClient: {e}")
                        resolution_stats["failed_count"] += 1
                        continue

                try:
                    # Use retailer-preserving resolution
                    products = serp_client.resolve_google_shopping_url(
                        google_url=url,
                        max_products=1,  # One PDP per input URL
                        expected_retailer=retailer_hint,
                        expected_domain=expected_domain,
                        strict_mode=strict_mode,
                    )

                    if products and len(products) > 0:
                        resolved = products[0]
                        resolved_url = resolved.get("url")
                        actual_store = resolved.get("store", "")

                        # Check if retailer matched
                        retailer_matched = False
                        if retailer_hint and retailer_identity_service:
                            try:
                                domain = urlparse(resolved_url).netloc.lower().replace("www.", "")
                                retailer_matched = retailer_identity_service.domain_matches_brand(domain, retailer_hint)
                            except Exception:
                                pass

                        if retailer_matched:
                            resolution_stats["retailer_matched_count"] += 1
                            logger.info(f"[AFFILIATE] ✅ Retailer MATCHED: {retailer_hint} -> {resolved_url[:60]}...")
                        else:
                            logger.info(f"[AFFILIATE] ⚠️ Retailer not matched: expected {retailer_hint}, got {actual_store}")

                        resolved_products.append({
                            "original_url": url,
                            "resolved_url": resolved_url,
                            "expected_retailer": retailer_hint,
                            "actual_retailer": actual_store,
                            "retailer_matched": retailer_matched,
                            "title": resolved.get("title", product_title),
                            "resolution_source": resolved.get("source_api", "serpapi"),
                        })
                        resolution_stats["resolved_count"] += 1
                    else:
                        logger.warning(f"[AFFILIATE] No PDP resolved for: {url[:60]}...")
                        resolution_stats["failed_count"] += 1

                except Exception as e:
                    logger.error(f"[AFFILIATE] Resolution failed: {e}")
                    resolution_stats["failed_count"] += 1

            else:
                # Direct retailer URL - just validate and use
                resolved_products.append({
                    "original_url": url,
                    "resolved_url": url,
                    "expected_retailer": retailer_hint,
                    "actual_retailer": None,  # Will be determined from URL
                    "retailer_matched": None,
                    "title": product_title,
                    "resolution_source": "direct",
                })
                resolution_stats["resolved_count"] += 1

        logger.info(
            f"[AFFILIATE] Resolution complete: {resolution_stats['resolved_count']}/{resolution_stats['total']} resolved, "
            f"{resolution_stats['retailer_matched_count']} retailer-matched, "
            f"{resolution_stats['failed_count']} failed"
        )

        # ============================================================
        # STEP 2: Validate resolved URLs
        # ============================================================
        urls_to_validate = [p["resolved_url"] for p in resolved_products if p.get("resolved_url")]
        logger.info(f"[AFFILIATE] Validating {len(urls_to_validate)} URLs...")

        validation_results = affiliate_client.validate_urls(urls_to_validate)

        # Filter to valid products
        valid_products = []
        for product in resolved_products:
            resolved_url = product.get("resolved_url")
            if resolved_url and validation_results.get(resolved_url, {}).get("valid", False):
                valid_products.append(product)
            else:
                logger.warning(f"[AFFILIATE] URL failed validation: {resolved_url[:60] if resolved_url else 'None'}...")

        invalid_count = len(resolved_products) - len(valid_products)

        # ============================================================
        # STEP 3: Process valid URLs and group by retailer
        # ============================================================
        valid_urls = [p["resolved_url"] for p in valid_products]
        grouped_products = affiliate_client.process_urls(valid_urls)

        # Build mapping from resolved_url back to product metadata
        url_to_product = {p["resolved_url"]: p for p in valid_products}

        # Build response with retailer carts
        carts = []
        total_products = 0

        for retailer, products in grouped_products.items():
            affiliate_products = []

            for p in products:
                original_meta = url_to_product.get(p["original_url"], {})

                affiliate_products.append(
                    AffiliateProduct(
                        original_url=original_meta.get("original_url", p["original_url"]),
                        resolved_url=p["original_url"],  # This is actually the resolved URL
                        affiliate_url=p["affiliate_url"],
                        product_id=p["product_id"],
                        product_name=original_meta.get("title"),
                        expected_retailer=original_meta.get("expected_retailer"),
                        actual_retailer=retailer,
                        retailer_matched=original_meta.get("retailer_matched"),
                        resolution_source=original_meta.get("resolution_source"),
                    )
                )

            # Generate cart URL
            product_ids = [p["product_id"] for p in products if p["product_id"] != "unknown"]

            # For Amazon, preserve regional domain
            cart_domain = None
            if retailer == "amazon":
                try:
                    first_url = products[0]["original_url"]
                    parsed = urlparse(first_url)
                    if parsed.netloc and "amazon." in parsed.netloc:
                        cart_domain = parsed.netloc
                except Exception:
                    pass

            cart_url = affiliate_client.generate_cart_url(retailer, product_ids, domain=cart_domain)

            retailer_cart = RetailerCart(
                retailer=retailer,
                retailer_display_name=affiliate_client.get_retailer_display_name(retailer),
                products=affiliate_products,
                cart_url=cart_url,
                product_count=len(affiliate_products),
            )

            carts.append(retailer_cart)
            total_products += len(affiliate_products)

        logger.info(f"[AFFILIATE] Generated {len(carts)} retailer carts with {total_products} products")

        return AffiliateCartResponse(
            carts=carts,
            total_products=total_products,
            total_retailers=len(carts),
            status="success",
            message=f"Generated {len(carts)} affiliate cart(s) with {total_products} product(s). "
                    f"Retailer match rate: {resolution_stats['retailer_matched_count']}/{resolution_stats['google_shopping_count']} Google Shopping URLs.",
            urls_processed=resolution_stats["total"],
            urls_resolved=resolution_stats["resolved_count"],
            urls_validated=len(valid_products),
            urls_failed=invalid_count + resolution_stats["failed_count"],
        )

    except Exception as e:
        logger.error(f"Failed to generate affiliate cart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to generate affiliate cart: {str(e)}"
        )


# =============================================================================
# Universal Product Link Normalizer
# =============================================================================

@app.post("/normalize-urls")
async def normalize_urls(request: NormalizeURLsRequest):
    """
    Normalize product URLs to canonical retailer PDPs.

    Handles:
    - Google Shopping URLs (extracts retailer links via SerpAPI)
    - Affiliate/tracking redirect URLs (follows redirect chain)
    - Direct retailer URLs (validates and extracts canonical)

    Returns normalized URLs grouped by retailer with validation and classification.
    """
    try:
        # Import url_normalizer module (lazy import to avoid startup issues)
        from url_normalizer.client import URLNormalizerClient
        from url_normalizer.models import (
            URLResolution,
            RetailerGroup,
            NormalizationTelemetry,
        )

        # Initialize client with optional SerpClient
        serp_client = None
        if request.google_shopping_mode == "serpapi":
            try:
                from serp_client import SerpClient
                serp_client = SerpClient()
            except Exception as e:
                logger.warning(f"SerpClient not available for URL normalizer: {e}")

        # Create client
        client = URLNormalizerClient(
            serp_client=serp_client,
            max_concurrent=request.max_concurrent,
            max_per_domain=request.max_per_domain,
            timeout_ms=request.timeout_ms,
        )

        # Normalize URLs
        resolutions, groups, telemetry = await client.normalize_urls(
            urls=request.urls,
            region=request.region,
            language=request.language,
            prefer_domains=request.prefer_domains,
            block_domains=request.block_domains,
            google_shopping_mode=request.google_shopping_mode,
            include_classification=request.include_classification,
            max_candidates_per_url=request.max_candidates_per_url,
        )

        return {
            "results": [r.model_dump() for r in resolutions],
            "groups": [g.model_dump() for g in groups],
            "telemetry": telemetry.model_dump(),
            "status": "success",
            "message": f"Normalized {len(resolutions)} URLs into {len(groups)} retailer groups",
        }

    except ImportError as e:
        logger.error(f"URL Normalizer module not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="URL Normalizer service not available. Check dependencies."
        )
    except Exception as e:
        logger.error(f"Failed to normalize URLs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to normalize URLs: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
