"use client";

import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open } from "@tauri-apps/plugin-dialog";
import { Upload, Video, Settings, Play, CheckCircle, AlertCircle, Loader2, FolderOpen, Languages } from "lucide-react";
import { useTranslation } from "react-i18next";
import "../i18n/config"; // Initialize i18n

interface ProgressPayload {
  current: number;
  total: number;
  percentage: number;
  message: string;
}

export default function Home() {
  const { t, i18n } = useTranslation();
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

    const unlistenFinished = listen<{ code: number | null; error: string | null }>("upscale-finished", (event) => {
      setIsProcessing(false);
      const { code, error: errMsg } = event.payload;
      if (code === 0) {
        setIsFinished(true);
        setProgress({ current: 100, total: 100, percentage: 100, message: t("completed") });
      } else {
        setIsFinished(false);
        setError(errMsg || `Process exited with code ${code}`);
      }
    });

    return () => {
      unlistenProgress.then((f) => f());
      unlistenFinished.then((f) => f());
    };
  }, [t]);

  const handleBrowse = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [
          {
            name: "Video",
            extensions: ["mp4", "avi", "mkv", "mov", "webm"],
          },
        ],
      });
      if (selected && typeof selected === "string") {
        setInputPath(selected);
        setOutputPath("");
        setIsFinished(false);
        setProgress(null);
        setError(null);
      }
    } catch (e: any) {
      setError("Failed to open file dialog: " + e.toString());
    }
  };

  const handleStart = async () => {
    if (!inputPath) {
      setError("Please select an input video file.");
      return;
    }

    const outPath = outputPath || inputPath.replace(/(\.[^.]+)$/, "_upscaled$1");
    setOutputPath(outPath);

    setError(null);
    setIsFinished(false);
    setIsProcessing(true);
    setProgress({ current: 0, total: 100, percentage: 0, message: t("initializing") });

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

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-8 flex flex-col items-center justify-center">
      {/* Language Selector */}
      <div className="absolute top-6 right-6 flex items-center gap-2 bg-slate-900/80 border border-slate-800 p-1 rounded-full px-3 py-1.5 shadow-lg">
        <Languages size={14} className="text-slate-400" />
        <select 
          className="bg-transparent text-xs font-medium focus:outline-none cursor-pointer text-slate-300"
          value={i18n.language}
          onChange={(e) => changeLanguage(e.target.value)}
        >
          <option value="ko">한국어</option>
          <option value="en">English</option>
          <option value="ja">日本語</option>
        </select>
      </div>

      <div className="w-full max-w-2xl bg-slate-900/50 border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur-sm">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            {t("title")}
          </h1>
          <p className="text-slate-400 mt-2">{t("subtitle")}</p>
        </header>

        <div className="space-y-6">
          {/* File Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <Video size={16} /> {t("input_label")}
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder={t("placeholder")}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                value={inputPath}
                readOnly
              />
              <button
                onClick={handleBrowse}
                disabled={isProcessing}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors border border-slate-700 text-sm font-medium"
              >
                <FolderOpen size={16} />
                {t("browse")}
              </button>
            </div>
          </div>

          {/* Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Settings size={16} /> {t("scale")}
              </label>
              <select
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm appearance-none cursor-pointer"
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
                <Settings size={16} /> {t("model")}
              </label>
              <select
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm appearance-none cursor-pointer"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                disabled={isProcessing}
              >
                <optgroup label="Real-ESRGAN">
                  <option value="realesrgan-x4plus">Real-ESRGAN Plus (General)</option>
                  <option value="realesrgan-x4plus-anime">Real-ESRGAN Anime</option>
                  <option value="realesr-animevideov3">Real-ESRGAN AnimeVideo V3</option>
                </optgroup>
                <optgroup label="Real-CUGAN">
                  <option value="realcugan-se">Real-CUGAN SE (Fast)</option>
                  <option value="realcugan-pro">Real-CUGAN Pro (High Quality)</option>
                </optgroup>
              </select>
            </div>
          </div>

          {/* Progress Section */}
          {(isProcessing || progress || error || isFinished) && (
            <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">
                  {error ? t("error_occurred") : isFinished ? t("completed") : progress?.message || t("preparing")}
                </span>
                <span className="font-mono text-indigo-400">
                  {progress ? `${Math.round(progress.percentage)}%` : "0%"}
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
                <div className="flex items-start gap-2 text-red-400 text-xs mt-2 bg-red-500/10 p-3 rounded-lg border border-red-500/20 max-h-32 overflow-y-auto">
                  <AlertCircle size={14} className="shrink-0 mt-0.5" />
                  <p className="whitespace-pre-wrap">{error}</p>
                </div>
              )}

              {isFinished && (
                <div className="flex items-center gap-2 text-green-400 text-sm bg-green-500/10 p-3 rounded-lg border border-green-500/20">
                  <CheckCircle size={16} />
                  <span>{t("success_msg")}</span>
                </div>
              )}
            </div>
          )}

          {/* Action Button */}
          <button
            onClick={handleStart}
            disabled={isProcessing || !inputPath}
            className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all duration-300 ${
              isProcessing || !inputPath
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed opacity-50'
                : 'bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white shadow-lg hover:shadow-indigo-500/20 active:scale-[0.98]'
            }`}
          >
            {isProcessing ? (
              <>
                <Loader2 className="animate-spin" />
                {t("processing")}
              </>
            ) : (
              <>
                <Play size={20} fill="currentColor" />
                {t("start")}
              </>
            )}
          </button>
        </div>
      </div>

      <footer className="mt-8 text-slate-500 text-xs flex items-center gap-4">
        <p>Vibe Video Upscaler v0.2.1</p>
        <div className="w-1 h-1 bg-slate-800 rounded-full" />
        <p>Multi-language & FFmpeg Bundled</p>
      </footer>
    </main>
  );
}
