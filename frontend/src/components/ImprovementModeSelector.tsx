"use client";

import { RefreshCw, Sparkles } from "lucide-react";

interface ImprovementModeSelectorProps {
  onSelect: (mode: "iterative" | "complete_revamp") => void;
}

export function ImprovementModeSelector({
  onSelect,
}: ImprovementModeSelectorProps) {
  return (
    <div className="flex flex-col items-center gap-6 p-6">
      <h2 className="text-xl font-semibold text-gray-800">
        How would you like to design your space?
      </h2>

      <div className="flex gap-4">
        {/* Iterative Button */}
        <button
          onClick={() => onSelect("iterative")}
          className="flex flex-col items-center gap-2 p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all"
        >
          <RefreshCw className="w-8 h-8 text-blue-600" />
          <span className="font-medium">Iterative Improvements</span>
          <span className="text-sm text-gray-500">Enhance existing setup</span>
        </button>

        {/* Complete Revamp Button */}
        <button
          onClick={() => onSelect("complete_revamp")}
          className="flex flex-col items-center gap-2 p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition-all"
        >
          <Sparkles className="w-8 h-8 text-purple-600" />
          <span className="font-medium">Complete Revamp</span>
          <span className="text-sm text-gray-500">Redesign from scratch</span>
        </button>
      </div>
    </div>
  );
}
