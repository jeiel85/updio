"use client";

import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { Upload, Video, Settings, Play, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface ProgressPayload {
  current: number;
  total: number;
  percentage: number;
  message: string;
}

export default function Home() {
  const [inputPath, setInputPath] = useState<string>("");
  const [outputPath, setOutputPath] = useState<string>("");
  const [scale, setScale] = useState<number>(2);
  const [model, setModel] = useState<string>("realesrgan-x4plus");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [progress, setProgress] = useState<ProgressPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFinished, setIsFinished] = useState<boolean>(false);

  useEffect(() => {
    const unlistenProgress = listen<ProgressPayload>("upscale-progress", (event) => {
      setProgress(event.payload);
    });

    const unlistenError = listen<{ message: string }>("upscale-error", (event) => {
      setError(event.payload.message);
      setIsProcessing(false);
    });

    const unlistenFinished = listen<number | null>("upscale-finished", (event) => {
      setIsProcessing(false);
      setIsFinished(true);
      setProgress({ current: 100, total: 100, percentage: 100, message: "Completed!" });
    });

    return () => {
      unlistenProgress.then((f) => f());
      unlistenError.then((f) => f());
      unlistenFinished.then((f) => f());
    };
  }, []);

  const handleStart = async () => {
    if (!inputPath) {
      setError("Please select an input video file.");
      return;
    }

    // Simple output path generation if not provided
    const outPath = outputPath || inputPath.replace(/(\.[^.]+)$/, "_upscaled$1");
    setOutputPath(outPath);

    setError(null);
    setIsFinished(false);
    setIsProcessing(true);
    setProgress({ current: 0, total: 100, percentage: 0, message: "Initializing..." });

    try {
      await invoke("start_upscale", {
        input: inputPath,
        output: outPath,
        scale,
        model,
      });
    } catch (e: any) {
      setError(e.toString());
      setIsProcessing(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-8 flex flex-col items-center justify-center">
      <div className="w-full max-w-2xl bg-slate-900/50 border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur-sm">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            Vibe Video Upscaler
          </h1>
          <p className="text-slate-400 mt-2">AI-powered high resolution video enhancement</p>
        </header>

        <div className="space-y-6">
          {/* File Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <Video size={16} /> Input Video Path
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="C:\Videos\my_video.mp4"
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                value={inputPath}
                onChange={(e) => setInputPath(e.target.value)}
                disabled={isProcessing}
              />
            </div>
          </div>

          {/* Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Settings size={16} /> Scale
              </label>
              <select
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm appearance-none"
                value={scale}
                onChange={(e) => setScale(Number(e.target.value))}
                disabled={isProcessing}
              >
                <option value={2}>2x Upscale</option>
                <option value={4}>4x Upscale</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Settings size={16} /> AI Model
              </label>
              <select
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm appearance-none"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                disabled={isProcessing}
              >
                <option value="realesrgan-x4plus">Real-ESRGAN Plus</option>
                <option value="realesrgan-x4plus-anime">Real-ESRGAN Anime</option>
              </select>
            </div>
          </div>

          {/* Progress Section */}
          {(isProcessing || progress || error || isFinished) && (
            <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">
                  {error ? "Error occurred" : isFinished ? "Process complete" : progress?.message || "Preparing..."}
                </span>
                <span className="font-mono text-indigo-400">
                  {progress ? `${progress.percentage}%` : "0%"}
                </span>
              </div>
              
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ease-out ${
                    error ? 'bg-red-500' : isFinished ? 'bg-green-500' : 'bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]'
                  }`}
                  style={{ width: `${progress?.percentage || 0}%` }}
                />
              </div>

              {error && (
                <div className="flex items-start gap-2 text-red-400 text-xs mt-2 bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                  <AlertCircle size={14} className="shrink-0 mt-0.5" />
                  <p>{error}</p>
                </div>
              )}

              {isFinished && (
                <div className="flex items-center gap-2 text-green-400 text-sm bg-green-500/10 p-3 rounded-lg border border-green-500/20">
                  <CheckCircle size={16} />
                  <span>Success! Upscaled video saved to output path.</span>
                </div>
              )}
            </div>
          )}

          {/* Action Button */}
          <button
            onClick={handleStart}
            disabled={isProcessing || !inputPath}
            className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all duration-300 ${
              isProcessing 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white shadow-lg hover:shadow-indigo-500/20 active:scale-[0.98]'
            }`}
          >
            {isProcessing ? (
              <>
                <Loader2 className="animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Play size={20} fill="currentColor" />
                Start Upscaling
              </>
            )}
          </button>
        </div>
      </div>

      <footer className="mt-8 text-slate-500 text-xs flex items-center gap-4">
        <p>Vibe Video Upscaler v0.1.0</p>
        <div className="w-1 h-1 bg-slate-800 rounded-full" />
        <p>Powered by Real-ESRGAN & Tauri</p>
      </footer>
    </main>
  );
}
