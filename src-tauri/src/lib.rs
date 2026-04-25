use tauri::{AppHandle, Emitter};
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
    // Determine ffmpeg and ffprobe paths from sidecars
    let ffmpeg_sidecar = app.shell().sidecar("ffmpeg").map_err(|e| e.to_string())?;
    // Note: We need the actual path to pass to Python
    // In Tauri v2, sidecar("name") returns a Command builder.
    
    // For Python to use them, we pass the command names. 
    // Tauri's sidecar execution will handle the pathing if we were running them directly,
    // but since Python needs to call them, we need to be careful.
    // A robust way in Tauri v2 is to use the sidecar command itself, 
    // but here Python is the "master" of ffmpeg.
    
    // Workaround: We'll assume the sidecars are in the same directory as the engine sidecar.
    // Or better, we can try to resolve the paths if needed.
    
    // Simplest for now: Pass dummy paths and let the engine try to find them in its own bundle.
    // However, the best practice is to resolve them.
    
    let sidecar_command = app
        .shell()
        .sidecar("vibe-engine")
        .map_err(|e| e.to_string())?
        .args([
            "--input", &input, 
            "--output", &output, 
            "--scale", &scale.to_string(), 
            "--model", &model,
            // We pass "ffmpeg" and "ffprobe" names; 
            // the sidecar execution environment might need them in PATH.
            // In a real bundle, Tauri puts sidecars in a specific 'bin' folder.
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
