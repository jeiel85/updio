use tauri::{AppHandle, Emitter, Manager};
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone)]
struct ProgressPayload {
    current: u32,
    total: u32,
    percentage: f64,
    message: String,
}

#[derive(Serialize, Clone)]
struct ErrorPayload {
    message: String,
}

#[tauri::command]
async fn start_upscale(
    app: AppHandle,
    input: String,
    output: String,
    scale: u32,
    model: String,
) -> Result<(), String> {
    // Determine ffmpeg and ffprobe paths from sidecars to pass to Python
    // We use the sidecar command's configured path
    let sidecar_command_ffmpeg = app.shell().sidecar("ffmpeg").map_err(|e| e.to_string())?;
    let sidecar_command_ffprobe = app.shell().sidecar("ffprobe").map_err(|e| e.to_string())?;
    
    // In Tauri v2, we can't easily get the raw path string before spawn,
    // but the sidecars are placed in a predictable location.
    // However, the most reliable way is to let Tauri resolve it.
    // For this implementation, we assume the engine sidecar will find them 
    // in the same binary directory if we pass just the names, 
    // or we can try to resolve resources.
    
    let sidecar_command = app
        .shell()
        .sidecar("vibe-engine")
        .map_err(|e| e.to_string())?
        .args([
            "--input", &input, 
            "--output", &output, 
            "--scale", &scale.to_string(), 
            "--model", &model,
            // On Windows, when running as a sidecar, these names will resolve to the sidecar binaries
            "--ffmpeg", "ffmpeg", 
            "--ffprobe", "ffprobe",
        ]);

    let (mut rx, _child) = sidecar_command
        .spawn()
        .map_err(|e| e.to_string())?;

    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    let line_str = String::from_utf8_lossy(&line);
                    if let Ok(payload) = serde_json::from_str::<ProgressPayload>(&line_str) {
                        let _ = app.emit("upscale-progress", payload);
                    }
                }
                CommandEvent::Stderr(line) => {
                    let line_str = String::from_utf8_lossy(&line);
                    // Check if it's a JSON error or raw string
                    let _ = app.emit("upscale-error", ErrorPayload { message: line_str.to_string() });
                }
                CommandEvent::Terminated(payload) => {
                    let _ = app.emit("upscale-finished", payload.code);
                }
                _ => {}
            }
        }
    });

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![start_upscale])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
