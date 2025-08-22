import { useAnalyzeInspirations, useGetInspirationAnalysis } from "@/lib/api";

interface InspirationAnalysisProps {
  projectId: string;
  status: string;
  context: Record<string, any>;
}

export function InspirationAnalysis({
  projectId,
  status,
  context,
}: InspirationAnalysisProps) {
  const analyzeInspirationsMutation = useAnalyzeInspirations();
  const analysisQuery = useGetInspirationAnalysis(projectId);

  const inspirationImages = context.inspiration_images || [];
  const hasInspirationImages = inspirationImages.length > 0;
  const isReadyForAnalysis = status === "INSPIRATIONS_UPLOADED";
  const hasAnalysis =
    context.inspiration_analysis && context.inspiration_analysis.length > 0;

  const handleAnalyze = () => {
    analyzeInspirationsMutation.mutate({ projectId });
  };

  if (!hasInspirationImages) {
    return null;
  }

  return (
    <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        Inspiration Analysis
      </h2>

      {isReadyForAnalysis && !hasAnalysis && (
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-300">
            Ready to analyze your inspiration images! Click the button below to
            generate AI-powered design insights based on your uploaded
            inspiration images.
          </p>

          <button
            onClick={handleAnalyze}
            disabled={analyzeInspirationsMutation.isPending}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {analyzeInspirationsMutation.isPending ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Analyzing Inspirations...</span>
              </div>
            ) : (
              "Generate Design Analysis"
            )}
          </button>

          {analyzeInspirationsMutation.isError && (
            <div className="text-red-600 dark:text-red-400 text-sm">
              Error: {analyzeInspirationsMutation.error?.message}
            </div>
          )}
        </div>
      )}

      {hasAnalysis && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-green-600 dark:text-green-400 font-medium">
              Analysis complete
            </span>
          </div>

          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Design Insights from {inspirationImages.length} Inspiration Image
              {inspirationImages.length !== 1 ? "s" : ""}
            </h3>

            {analysisQuery.isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : analysisQuery.isError ? (
              <div className="text-red-600 dark:text-red-400">
                Error loading analysis: {analysisQuery.error?.message}
              </div>
            ) : (
              <div className="space-y-3">
                {context.inspiration_analysis.map(
                  (insight: string, index: number) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600"
                    >
                      <div className="flex-shrink-0 w-6 h-6 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full flex items-center justify-center text-sm font-medium">
                        {index + 1}
                      </div>
                      <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                        {insight}
                      </p>
                    </div>
                  )
                )}
              </div>
            )}
          </div>

          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p>
              These insights are based on AI analysis of your inspiration images
              and can help guide your design decisions for the project.
            </p>
          </div>
        </div>
      )}

      {status === "INSPIRATION_ANALYSIS_READY" && (
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
              <svg
                className="w-3 h-3 text-white"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <span className="text-blue-800 dark:text-blue-200 font-medium">
              Inspiration analysis complete! Your project is ready for the next
              step.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
