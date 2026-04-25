import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  ko: {
    translation: {
      "title": "Vibe 비디오 업스케일러",
      "subtitle": "AI 기반 고해상도 비디오 향상 도구",
      "input_label": "입력 비디오 경로",
      "placeholder": "비디오 파일을 선택하세요...",
      "browse": "찾아보기",
      "scale": "확대 배율",
      "model": "AI 모델",
      "start": "업스케일링 시작",
      "processing": "처리 중...",
      "completed": "완료!",
      "error_occurred": "오류 발생",
      "preparing": "준비 중...",
      "success_msg": "성공! 업스케일링된 비디오가 저장되었습니다.",
      "initializing": "초기화 중...",
      "upscaling": "업스케일링 중",
      "merging": "병합 중...",
      "extracting": "프레임 추출 중..."
    }
  },
  en: {
    translation: {
      "title": "Vibe Video Upscaler",
      "subtitle": "AI-powered high resolution video enhancement",
      "input_label": "Input Video Path",
      "placeholder": "Select a video file...",
      "browse": "Browse",
      "scale": "Scale",
      "model": "AI Model",
      "start": "Start Upscaling",
      "processing": "Processing...",
      "completed": "Completed!",
      "error_occurred": "Error occurred",
      "preparing": "Preparing...",
      "success_msg": "Success! Upscaled video saved to output path.",
      "initializing": "Initializing...",
      "upscaling": "Upscaling",
      "merging": "Merging...",
      "extracting": "Extracting frames..."
    }
  },
  ja: {
    translation: {
      "title": "Vibe ビデオアップスケーラー",
      "subtitle": "AI搭載の高解像度ビデオエンハンスメント",
      "input_label": "入力ビデオパス",
      "placeholder": "ビデオファイルを選択してください...",
      "browse": "参照",
      "scale": "拡大倍率",
      "model": "AIモデル",
      "start": "アップスケール開始",
      "processing": "処理中...",
      "completed": "完了！",
      "error_occurred": "エラーが発生しました",
      "preparing": "準備中...",
      "success_msg": "成功！アップスケールされたビデオが保存されました。",
      "initializing": "初期化中...",
      "upscaling": "アップスケール中",
      "merging": "結合中...",
      "extracting": "フレーム抽出中..."
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['querystring', 'cookie', 'localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    }
  });

export default i18n;
