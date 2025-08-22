import { getInspirationImageUrl, useUploadInspirationImages } from "@/lib/api";
import Image from "next/image";
import { useRef, useState } from "react";

interface InspirationUploadSectionProps {
  projectId: string;
  status: string;
  context: Record<string, any>;
}

export function InspirationUploadSection({
  projectId,
  status,
  context,
}: InspirationUploadSectionProps) {
  const uploadInspirationMutation = useUploadInspirationImages();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;

    const fileArray = Array.from(files);
    const imageFiles = fileArray.filter((file) =>
      file.type.startsWith("image/")
    );

    if (imageFiles.length > 5) {
      alert("Maximum 5 inspiration images allowed");
      return;
    }

    setSelectedFiles(imageFiles);
  };

  const handleUpload = () => {
    if (selectedFiles.length === 0) return;

    uploadInspirationMutation.mutate({
      projectId,
      files: selectedFiles,
    });

    setSelectedFiles([]);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const inspirationImages = context.inspiration_images || [];

  return (
    <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        Upload Inspiration Images
      </h2>

      {status === "MARKER_RECOMMENDATIONS_READY" &&
        inspirationImages.length === 0 && (
          <div className="space-y-4">
            <p className="text-gray-600 dark:text-gray-300">
              Upload up to 5 inspiration images to help guide the AI design
              recommendations. These images will be analyzed to understand your
              design preferences and style.
            </p>

            <div
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                dragActive
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-gray-300 dark:border-gray-600"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="space-y-4">
                <div className="text-gray-600 dark:text-gray-300">
                  <p className="text-lg font-medium">
                    Drop inspiration images here
                  </p>
                  <p className="text-sm">or</p>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onChange={(e) => handleFiles(e.target.files)}
                />

                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Choose Images
                </button>

                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Maximum 5 images • JPG, PNG, GIF supported
                </p>
              </div>
            </div>

            {selectedFiles.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Selected Files ({selectedFiles.length}/5)
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {selectedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3"
                    >
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {file.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleUpload}
                  disabled={uploadInspirationMutation.isPending}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {uploadInspirationMutation.isPending
                    ? "Uploading..."
                    : "Upload Images"}
                </button>
              </div>
            )}

            {uploadInspirationMutation.isSuccess && (
              <div className="text-green-600 dark:text-green-400 text-sm">
                Inspiration images uploaded successfully!
              </div>
            )}

            {uploadInspirationMutation.isError && (
              <div className="text-red-600 dark:text-red-400 text-sm">
                Error: {uploadInspirationMutation.error?.message}
              </div>
            )}
          </div>
        )}

      {inspirationImages.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-green-600 dark:text-green-400 font-medium">
              {inspirationImages.length} inspiration image
              {inspirationImages.length !== 1 ? "s" : ""} uploaded
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {inspirationImages.map((image: any) => (
              <div
                key={image.id}
                className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3"
              >
                <div className="relative w-full h-32 bg-gray-200 dark:bg-gray-600 rounded-lg overflow-hidden mb-2">
                  <Image
                    src={getInspirationImageUrl(projectId, image.id)}
                    alt={`Inspiration ${image.id}`}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 50vw, (max-width: 1200px) 33vw, 20vw"
                  />
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-300 truncate">
                  {image.filename}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
