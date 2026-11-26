# alise.py — переводчик игр с озвучкой

Офлайн-перевод речи и субтитров в играх: Whisper распознаёт речь игры,
Argos переводит на русский, Silero озвучивает голосом по полу диктора.
Есть режим субтитров-оверлея и режим озвучки субтитров с экрана (OCR).

Работает на Windows 10/11. Общение — в консоли, плюс маленькое окно
превью с кнопками.

---

## 1. Установка Python (с нуля)

1. Скачай Python 3.11 с официального сайта: https://www.python.org/downloads/
   (кнопка Download Python; 3.12+ тоже работает, но 3.11 проверен лучше).
2. Запусти установщик и **обязательно поставь галочку
   «Add python.exe to PATH»** на первом экране.
3. Нажми Install Now и дождись окончания.
4. Проверь: открой PowerShell (Пуск → набери «powershell») и выполни:

   ```
   py --version
   ```

   Должно напечататься что-то вроде `Python 3.11.x`. Если «py не является
   командой» — переустанови Python и не забудь галочку PATH.

## 2. Подготовка папки проекта

1. Создай папку, например `C:\alise`.
2. Положи туда файлы из раздела «Приложения» (в конце этой инструкции):
   - `alise.py` — основной скрипт;
   - `install_deps.py` — авто-установка окружения;
   - `README.md` — эта инструкция (не обязательна для работы).

## 3. Установка зависимостей

В PowerShell перейди в папку и запусти установщик:

```
cd C:\alise
py install_deps.py
```

Скрипт сам:

- поставит pip-пакеты: numpy, mss, opencv-python, torch, sounddevice,
  rapidocr, pillow, faster-whisper, argostranslate, keyboard;
- при наличии видеокарты NVIDIA поставит PyTorch с CUDA;
- удалит конфликтный пакет paddle (мешает RapidOCR);
- скачает пакет перевода Argos en→ru;
- скачает модель Whisper `large-v3-turbo`.

Это долго (Whisper ~1.5 ГБ, PyTorch до 2–3 ГБ) — но один раз.
Если что-то упало, запусти `py install_deps.py` ещё раз: скрипт
идемпотентный, повторный запуск не ломает уже установленное.

## 4. Виртуальный аудиокабель (VB-Cable)

Скрипт должен «слышать» речь игры. Для этого звук игры направляется
в виртуальный кабель.

### 4.1 Установка VB-Cable

1. Скачай пакет: https://vb-audio.com/Cable/ → VBCABLE_Driver_Pack43.zip.
2. Распакуй архив, правый клик на `VBCABLE_Setup_x64.exe` →
   «Запуск от имени администратора» → кнопка Install Driver.
3. Перезагрузи компьютер.
4. Проверь: в списке устройств воспроизведения появился **CABLE Input**,
   в списке устройств записи — **CABLE Output**.

### 4.2 Направление звука игры в кабель

В настройках звука игры выбери устройство вывода **CABLE Input**.
Громкость не убавляй — скрипт слушает кабель.

Пока игра выводит звук в CABLE Input, ты её сам не слышишь. Варианты:

- **Вариант А (без OBS): «Прослушивать с устройства».**
  Открой Панель управления звуком → вкладка «Запись» → правый клик на
  CABLE Output → «Свойства» → вкладка «Прослушать» → галочка
  «Прослушивать с данного устройства» → «Воспроизводить через»:
  выбери свои наушники/колонки → ОК. Теперь слышишь и игру, и перевод.
  Минус: чуть задержка и лёгкий сдвиг качества.
- **Вариант Б (с OBS, рекомендуемый для записи/стрима)** — раздел 5.

## 5. Настройка OBS с VB-Cable

Если пишешь видео или стримишь — удобнее держать OBS «микшером» звука:

1. В OBS внизу в панели «Микшер аудио» нажми «⚙» (Настройки микшера) →
   «Расширенные свойства аудио».
2. Добавь два источника звука:
   - **«Захват входного аудиопотока»** (Audio Input Capture) →
     устройство **CABLE Output**. Это оригинальный звук игры — тот же,
     который слушает скрипт. Назови источник «Игра».
   - **«Захват выходного аудиопотока»** (Desktop Audio) — это голос
     переводчика (TTS) и всё, что играет в твои наушники. Назови «Перевод».
3. Чтобы слышать игру сам (скрипт уже слушает кабель), в расширенных
   свойствах аудио для источника «Игра» поставь **Аудио-мониторинг:
   «Мониторинг и вывод» (Monitor and Output)** → и выбери устройство
   мониторинга: Настройки OBS → Аудио → Устройство аудио-мониторинга —
   твои наушники. Теперь игра идёт тебе в уши через OBS, а скрипту —
   через кабель.
4. Микрофон добавь отдельным источником «Захват входного аудиопотока» →
   твой микрофон. В расширенных свойствах для него можно выключить
   мониторинг, чтобы не слышать себя.
5. Итоговая запись/стрим содержит: оригинальный звук игры («Игра»),
   русскую озвучку переводчика («Перевод») и твой голос.

Проверка: скажи в игре что-нибудь, в OBS на дорожке «Игра» должна
прыгать громкость; когда переводчик заговорит — прыгает «Перевод».

## 6. Первый запуск

```
cd C:\alise
py alise.py
```

Скрипт:

1. Спросит устройства ввода/вывода (ввод — **CABLE Output**, вывод —
   твои наушники/колонки). Выбор сохранится в `gta_translator.json`.
2. Откроется полупрозрачный экран: **обведи мышкой полосу субтитров
   в игре** — все строки субтитров с запасом 10–15 px сверху и снизу,
   не весь кадр.
3. Появится окно превью: там видно, что захватывает скрипт.

Консоль убери с той части экрана, где субтитры игры, — иначе OCR будет
читать и её.

## 7. Горячие клавиши

| Клавиша      | Действие                                          |
|--------------|---------------------------------------------------|
| ← Влево      | Режим «Голос»: речь → Whisper → перевод → озвучка |
| → Вправо     | Режим «Субтитры»: речь → Whisper → перевод → оверлей |
| Right Ctrl   | Режим «Голос по сабам»: OCR субтитров → озвучка   |
| ↑ Вверх      | Пометить диктора МУЖИКОМ (+ сохранить WAV-образец) |
| ↓ Вниз       | Пометить диктора ДЕВУШКОЙ (+ сохранить WAV-образец) |
| Right Shift  | Вкл/выкл озвучку (субтитры продолжают работать)   |
| Right Alt    | Сброс логики диалога (голос вернётся к базовому)  |
| R            | Обвести область субтитров заново без перезапуска  |

При переключении режима оверлей показывает жёлтую плашку с названием
режима (~2.5 с). Накопленная очередь озвучки при смене режима очищается.

## 8. Метки дикторов (голоса по полу)

Без меток пол угадывается по порогу 165 Гц. Для надёжной работы:

1. Включи режим «Голос» (ВЛЕВО) или «Субтитры» (ВПРАВО).
2. Когда говорит персонаж-мужчина — жми **ВВЕРХ**. Скрипт замерит живую
   высоту голоса (F0) и сохранит её как мужскую опору.
3. Когда говорит женщина — жми **ВНИЗ**.
4. В логе смотри строку `[OK] Метка МУЖИК: ... (n=..., медиана ...Гц)`.
   Нормальные медианы: муж 85–155 Гц, жен 165–280 Гц.

Каждая метка сразу пишется в `gta_translator.json`, а WAV-образец —
в папку `voice_samples/`.

Если метки «отравились» (например, замер пошёл от музыки и медиана
мужчины вышла 200+ Гц, из-за чего пол путается), очисти их:

```
py -c "import json; c=json.load(open('gta_translator.json',encoding='utf-8')); c.pop('speaker_refs',None); c.pop('sub_cps_calib',None); json.dump(c,open('gta_translator.json','w',encoding='utf-8'),ensure_ascii=False,indent=2); print('Очищено')"
```

Потом заново набери метки на чистой речи персонажей.

## 9. Файлы проекта

| Файл                    | Что это                                       |
|-------------------------|-----------------------------------------------|
| `gta_translator.json`   | Конфиг: область, устройства, режим, метки, калибровка |
| `voice_metrics.jsonl`   | Журнал событий (распознавания, переводы, TTS) |
| `voice_samples.csv`     | Таблица меток дикторов                        |
| `voice_samples/`        | WAV-образцы голосов при метках                |

## 10. Как это работает

- **Звук**: игра играет в CABLE Input → VAD (детектор речи с
  относительным порогом тишины, музыка не мешает) → сегменты речи.
- **Живой F0**: каждые 50 мс скрипт меряет высоту голоса автокорреляцией —
  параллельно с распознаванием, не дожидаясь Whisper.
- **Распознавание**: Whisper large-v3-turbo транскрибирует сегмент
  ПОТОКОВО — предложения уходят в перевод по мере декодирования,
  не дожидаясь конца реплики.
- **Перевод**: Argos en→ru, полностью офлайн.
- **Озвучка**: Silero v4. Голоса: eugene/aidar (муж), xenia/baya (жен).
  Темп подстраивается под длительность оригинала (самокалибровка по VAD).
- **Оверлей**: прозрачное окно поверх зоны субтитров; шрифт автоматически
  вписывает блок в зону; цвет текста по диктору (голубой — муж,
  розовый — жен, белый — не определён).

## 11. Решение проблем

**«py не является внутренней или внешней командой»**
Переустанови Python с галочкой «Add python.exe to PATH».

**Ошибка про protobuf / PaddleOCR при старте OCR**
`py -m pip uninstall paddleocr paddle -y`, затем `py install_deps.py`.

**Whisper грузится на CPU, хотя видеокарта есть**
`py -m pip install torch --index-url https://download.pytorch.org/whl/cu121`
(или cu124 — сверься с версией CUDA-драйвера: `nvidia-smi`).

**«переводчик en->ru не установлен»**
`py install_deps.py` — он докачает пакет Argos.

**Скрипт ничего не слышит**
Проверь: игра выводит в CABLE Input; при первом запуске выбрал CABLE
Output как устройство ввода. В логе строка `[REC] RMS=...` — если RMS
всегда около нуля, игра не играет в кабель. С OBS проверь, что источник
«Игра» ловит звук (полоска громкости в микшере OBS дёргается).

**OCR пусто в режиме «Голос по сабам»**
Обведи заново область (R): она должна накрывать ВСЕ строки субтитров
с запасом. Не обводи весь кадр — детектор теряет текст.

**Переводчик «вываливает» старые фразы при смене режима**
Исправлено в текущей версии: при смене режима очередь очищается.

**Звук переводчика слишком быстрый/медленный**
Калибровка темпа учится на игре. Сброс — та же команда очистки,
что в разделе 8 (она стирает и калибровку), начнёт с дефолта 15 зн/с.

**Оверлей слишком мелкий/крупный**
Шрифт вписывается в зону захвата. Хочешь крупнее — обведи зону повыше (R).
Хочешь жёстче вписывать в зону — в `alise.py` уменьши `OVERLAY_FIT_FACTOR`
с 1.3 до 1.1.

## 12. Ограничения

- Перевод Argos — лёгкая офлайн-модель: сленг и идиомы передаёт приблизительно.
- Классификация пола по F0 — эвристика: шёпот и крик могут путаться.
- OCR требует, чтобы субтитры были на экране в обведённой зоне.

---

## Приложения (исходники)

### Приложение A — `install_deps.py`

# -*- coding: utf-8 -*-
"""
install_deps.py — авто-установка окружения для alise.py.

Ставит pip-пакеты, PyTorch с CUDA (если есть NVIDIA), удаляет конфликтный
paddle, скачивает пакет перевода Argos en->ru и модель Whisper.

Запуск:  py install_deps.py
Скрипт идемпотентный: повторный запуск не ломает уже установленное.
Также вызывается из alise.py при старте (ensure_environment).
"""

import subprocess
import sys
import os
import importlib

PIP_PACKAGES = [
    "numpy",
    "mss",
    "opencv-python",
    "sounddevice",
    "rapidocr",
    "pillow",
    "faster-whisper",
    "argostranslate",
    "keyboard",
]

WHISPER_MODEL = "large-v3-turbo"

TORCH_CUDA_INDEX = "https://download.pytorch.org/whl/cu121"

CONFLICTING_PACKAGES = ["paddleocr", "paddle", "paddlepaddle"]


def run(cmd, check=True):
    print(f"[RUN] {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[!!] код {proc.returncode}")
        out = (proc.stdout or "").strip().splitlines()
        err = (proc.stderr or "").strip().splitlines()
        for line in out[-5:]:
            print(f"  out: {line}")
        for line in err[-10:]:
            print(f"  err: {line}")
        if check:
            raise RuntimeError(f"Команда не удалась: {' '.join(cmd)}")
    return proc


def pip_install(args, check=True):
    run([sys.executable, "-m", "pip", "install"] + args, check=check)


def ensure_pip():
    try:
        run([sys.executable, "-m", "pip", "--version"])
    except RuntimeError:
        print("[*] pip не найден — пробую ensurepip")
        run([sys.executable, "-m", "ensurepip", "--upgrade"])
        pip_install(["--upgrade", "pip", "setuptools", "wheel"])


def pip_ok():
    """Проверяет, ставятся ли пакеты вообще (без записи в системный Python)."""
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--dry-run", "--quiet",
         "six"],
        capture_output=True, text=True)
    return proc.returncode == 0


def uninstall_conflicting():
    print("[*] Удаление конфликтных пакетов (paddle мешает RapidOCR)")
    pip_install(["uninstall", "-y"] + CONFLICTING_PACKAGES, check=False)


def install_pip_packages():
    print("[*] Установка pip-пакетов")
    # torch ставится отдельно: у него особый индекс для CUDA
    others = [p for p in PIP_PACKAGES if p != "torch"]
    pip_install(others)


def install_torch():
    print("[*] Установка PyTorch")
    try:
        import torch  # noqa: F401
        print("[OK] PyTorch уже установлен:", torch.__version__)
        return
    except ImportError:
        pass

    # есть ли NVIDIA-драйвер?
    has_nvidia = False
    try:
        proc = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        has_nvidia = (proc.returncode == 0)
    except FileNotFoundError:
        pass

    if has_nvidia:
        print("[*] NVIDIA обнаружена — ставлю PyTorch с CUDA")
        pip_install(["torch", "--index-url", TORCH_CUDA_INDEX], check=False)
        try:
            import torch
            if torch.cuda.is_available():
                print("[OK] PyTorch CUDA готов:", torch.__version__)
                return
            print("[!] CUDA недоступна внутри torch — откат на обычный")
        except ImportError:
            pass

    print("[*] Ставлю PyTorch (CPU/CUDA по умолчанию)")
    pip_install(["torch"], check=False)
    try:
        import torch  # noqa: F401
        print("[OK] PyTorch установлен:", torch.__version__)
    except ImportError:
        print("[!] PyTorch не установился — Whisper не заработает")


def install_argos_pair():
    print("[*] Установка пакета перевода Argos en->ru")
    try:
        from argostranslate import package
        installed = {p.code for p in package.get_installed_languages()}
        if "en" in installed and "ru" in installed:
            src = next(p for p in package.get_installed_languages()
                       if p.code == "en")
            if any(t.code == "ru" for t in src.translations_to()):
                print("[OK] Argos en->ru уже установлен")
                return
        print("[*] Скачиваю argospackage en_ru (~250 МБ)")
        package.update_package_index()
        available = package.get_available_packages()
        target = [p for p in available
                  if p.from_code == "en" and p.to_code == "ru"]
        if not target:
            print("[!] Пакет en->ru не найден в индексе")
            return
        pkg = target[0]
        path = pkg.download()
        package.install_from_path(path)
        print("[OK] Argos en->ru установлен")
    except Exception as e:
        print(f"[!] Argos: {e}")
        print("    Запусти install_deps.py ещё раз позже")


def predownload_whisper():
    """Скачивает модель Whisper заранее, чтобы не тянуть при первом запуске."""
    print(f"[*] Скачивание модели Whisper {WHISPER_MODEL}")
    try:
        from faster_whisper import WhisperModel
        WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        print("[OK] Whisper-модель скачана")
    except Exception as e:
        print(f"[!] Модель не скачалась ({e}) — будет скачана при первом запуске")


def fix_protobuf_if_needed():
    """Иногда onnxruntime/protobuf конфликтуют по версии."""
    try:
        import google.protobuf  # noqa: F401
        import onnxruntime  # noqa: F401
    except ImportError:
        return
    except Exception as e:
        print(f"[*] Проблема с protobuf/onnxruntime: {e} — пробую починить")
        pip_install(["-U", "protobuf", "onnxruntime"], check=False)


def ensure_environment():
    """Точка входа для вызова из alise.py: тихая проверка, ничего не ломает."""
    missing = []
    for name in PIP_PACKAGES:
        try:
            importlib.import_module(
                {"opencv-python": "cv2",
                 "faster-whisper": "faster_whisper",
                 "argostranslate": "argostranslate"}.get(name, name))
        except ImportError:
            missing.append(name)
    if missing:
        print(f"[!] Не хватает пакетов: {', '.join(missing)}")
        print("    Запусти: py install_deps.py")
    return missing


def main():
    print("=" * 60)
    print("Установка окружения для alise.py")
    print("=" * 60)

    ensure_pip()
    if not pip_ok():
        print("[X] pip не может ставить пакеты.")
        print("    Проверь установку Python (галочка PATH) или права.")
        sys.exit(1)

    uninstall_conflicting()
    install_pip_packages()
    install_torch()
    fix_protobuf_if_needed()
    install_argos_pair()
    predownload_whisper()

    print("=" * 60)
    print("[OK] Установка завершена. Запускай: py alise.py")
    print("=" * 60)


if __name__ == "__main__":
    main()


### Приложение B — `alise.py`

# -*- coding: utf-8 -*-
"""
alise.py — переводчик для игр: Whisper (large-v3-turbo) + Argos (en->ru)
+ Silero TTS + RapidOCR. Кириллица.

РЕЖИМЫ (клавиши):
  ВЛЕВО      — «ГОЛОС»: речь игры (en/ru) -> Whisper -> перевод -> озвучка.
               Голос подбирается по диктору (метки ВВЕРХ/ВНИЗ + живой F0).
  ВПРАВО     — «СУБТИТРЫ»: речь игры -> Whisper -> перевод -> прозрачный
               компактный оверлей в зоне захвата, цвет текста по диктору
               (голубой — муж, розовый — жен, белый — не определён).
               Шрифт автоматически вписывает блок в зону захвата.
               Предложения уходят в оверлей по мере расшифровки.
  Right Ctrl — «ГОЛОС ПО САБАМ»: русские субтитры на экране -> OCR ->
               озвучка. Пока OCR читает текст, голос слушается параллельно.

При переключении режима оверлей показывает жёлтую плашку с названием
режима, накопленная очередь озвучки очищается. Фразы в режиме «Голос»
играют ПОДРЯД (очередь), а не прерывают друг друга.
Right Shift — вкл/выкл озвучку (субтитры продолжают работать).

КЛАВИШИ:
  ← Влево        режим «Голос» (озвучка) на основе речи
  → Вправо       режим «Субтитры» (оверлей) на основе речи
  Right Ctrl     режим «Голос по сабам» (OCR -> озвучка)
  ↑ Вверх        пометить текущего диктора МУЖИКОМ (+ WAV-образец)
  ↓ Вниз         пометить текущего диктора ДЕВУШКОЙ (+ WAV-образец)
  Right Shift    ВКЛ/ВЫКЛ озвучки
  Right Alt      сброс логики диалога
  R              обвести область субтитров заново без перезапуска

Whisper распознаёт ПОТОКОВО: предложения уходят в перевод и озвучку
по мере расшифровки, не дожидаясь конца всей реплики.

Темп речи под фразу: dur_оригинала = длина фразы x k (стартовый k = 1/15 сек
на знак), самокалибровка по VAD-сегментам реальной речи (после 5 пар —
измеренный k). Метки дикторов и калибровка сохраняются в конфиг сразу.

Зависимости: ставятся автоматически при первом запуске (install_deps.py),
или вручную:
  pip install numpy mss opencv-python torch sounddevice rapidocr pillow
  pip install faster-whisper argostranslate keyboard
"""

import os
import ctypes

# Лимиты потоков ДО импорта numpy/torch
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

# DPI-aware: процесс видит физическое разрешение, координаты консистентны.
def make_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def _physical_screen_size():
    """Физическое разрешение экрана независимо от DPI-aware процесса."""
    try:
        user32 = ctypes.windll.user32
        set_ctx = user32.SetThreadDpiAwarenessContext
        set_ctx.restype = ctypes.c_void_p
        set_ctx.argtypes = [ctypes.c_void_p]
        old = set_ctx(ctypes.c_void_p(-4))   # PER_MONITOR_AWARE_V2
        w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        set_ctx(old)
        return w, h
    except Exception:
        return None, None

make_dpi_aware()

# --- авто-установка окружения (до тяжёлых импортов) ---
try:
    import install_deps
    install_deps.ensure_environment()
except ImportError:
    pass   # install_deps.py не лежит рядом — не критично
except Exception as _e:
    print(f"[!] Авто-установка недоступна ({_e}) — работаем с тем, что есть")

import subprocess
import traceback
import logging
import json
import re
import sys
import time
import wave
import csv
import threading
import queue
from datetime import datetime

import numpy as np
import mss
import cv2
import torch
import sounddevice as sd
from rapidocr import RapidOCR

import tkinter as tk

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ======================================================
# Конфигурация
# ======================================================
CONFIG_FILE = "gta_translator.json"
METRICS_FILE = "voice_metrics.jsonl"
CSV_LOG_FILE = "voice_samples.csv"
WAV_DIR = "voice_samples"

SAMPLE_RATE = 48000      # Silero v4 работает на 48 кГц

COOLDOWN_SEC = 0.8        # минимальная пауза между озвучками
LAST_SPOKEN_SEC = 10.0    # столько секунд одна фраза не повторяется
MIN_TEXT_LEN = 3
SCORE_MIN = 0.60

# --- опрос экрана: всегда быстрый, холостой OCR отсекается дёшево ---
POLL_IDLE_SEC = 0.09
POLL_ACTIVE_SEC = 0.09
OCR_SKIP_STATIC = 3
TEXT_STABLE_SEC = 0.15

OCR_SCALE = 2.0
RETRY_SCALE = 3.0
MAX_OCR_WIDTH = 4096
TRIM_BRIGHT = 24
TRIM_PAD = 6

PREVIEW_WIDTH = 720

# --- живой замер F0: окно 200 мс, замер каждые 50 мс ---
LIVE_WINDOW_SEC = 0.20
LIVE_HOP_SEC = 0.05
LIVE_MAX_AGE = 1.5

# --- логика диалога ---
VOICE_MALE = "eugene"
VOICE_MALE_ALT = "aidar"
VOICE_FEMALE = "xenia"
VOICE_FEMALE_ALT = "baya"
F0_SWITCH_DELTA = 30.0
F0_FALLBACK = 165.0

# --- цвета оверлея по диктору ---
COLOR_MALE = "#7FD4FF"     # голубой
COLOR_FEMALE = "#FF9ECF"   # розовый
COLOR_UNKNOWN = "#FFFFFF"  # белый
COLOR_MODE_FLASH = "#FFD966"   # жёлтая плашка режима/статуса

# --- оверлей: вписывание в зону захвата ---
OVERLAY_FIT_FACTOR = 1.3   # блок может занять до 130% высоты зоны
OVERLAY_MIN_FONT = 12      # ниже не жмём — читаемость важнее
OVERLAY_MAX_FONT = 28      # компактные субтитры
OVERLAY_MODE_FLASH_SEC = 2.5   # сколько секунд висит плашка режима

# --- маркировка дикторов ---
MARK_SAMPLES_MAX = 50
RECENT_AUDIO_SEC = 3.0     # кольцевой буфер звука для меток
MARK_AUDIO_SEC = 2.5       # сколько последних секунд сохранять в WAV при метке

# --- прогноз длительности оригинала по длине субтитра ---
CPS_SUB_DEFAULT = 15.0
CAL_MIN_PAIRS = 5

# --- Whisper ---
WHISPER_MODEL = "large-v3-turbo"   # переопределяется конфигом
WHISPER_DEVICE = "cuda"            # при проблемах поставь "cpu"
WHISPER_LANG = None                # None = автоопределение
SEG_MIN_SEC = 0.5
SEG_SILENCE_SEC = 0.40             # тишина = конец фразы
SEG_MAX_SEC = 20.0                 # предохранитель: длинный сегмент режем
BASE_CPS = 15.0
RATE_MIN, RATE_MAX = 0.8, 1.3      # границы speeech_rate
SAVE_SEGMENT_WAV = False           # True — каждый Whisper-сегмент в WAV

# --- обучение слепков ---
STATS_SAVE_SEC = 5.0
F0_LO, F0_HI = 60.0, 400.0

# --- чувствительность VAD ---
VAD_MIN_THRESH = 0.0025
VAD_FLOOR_K = 2.5
NOISE_FLOOR_INIT = 0.001
SILENCE_RATIO = 0.30    # тишина = ниже 30% пика речи (музыка не мешает)
PEAK_DECAY = 0.999      # затухание пика за блок

REC_METER_SEC = 2.0

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- режимы ---
VALID_MODES = ("voice", "subs", "subs_voice")
MODE_NAMES = {
    "voice":      "ГОЛОС: речь игры -> Whisper -> перевод -> озвучка",
    "subs":       "СУБТИТРЫ: речь игры -> Whisper -> перевод -> оверлей",
    "subs_voice": "ГОЛОС ПО САБАМ: OCR субтитров -> озвучка",
}
CURRENT_MODE = "voice"
_mode_lock = threading.Lock()

CYR_RE = re.compile(r"[а-яёА-ЯЁ]")

# разбиение распознанного на предложения для немедленного вывода
SENTENCE_FLUSH_RE = re.compile(r"^(.*?[.!?…])(\s+|$)")

def norm_key(s):
    s = s.lower()
    s = re.sub(r"[^а-яёa-z ]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:48]

def get_mode():
    with _mode_lock:
        return CURRENT_MODE

def set_mode(mode):
    global CURRENT_MODE
    if mode not in VALID_MODES:
        print(f"[!] Неизвестный режим: {mode}")
        return
    with _mode_lock:
        CURRENT_MODE = mode
    print(f"[MODE] {MODE_NAMES[mode]}")
    # не вываливать накопленное после смены режима:
    # чистим очередь TTS и глушим всё, что звучит
    while True:
        try:
            _tts_queue.get_nowait()
        except queue.Empty:
            break
    _bump_gen()
    try:
        sd.stop()
    except Exception:
        pass
    log_metrics(source="mode", mode=mode)
    # плашка режима в оверлее: set_mode может зваться из потока клавиш,
    # Tk трогаем только через root.after в главном потоке
    def _mode_flash_soon():
        try:
            overlay._flash_text(f"● {MODE_NAMES[get_mode()]}")
        except Exception:
            pass
    if _app is not None and _app.root is not None:
        try:
            _app.root.after(0, _mode_flash_soon)
        except Exception:
            pass

# ======================================================
# Глобальное состояние
# ======================================================
ocr_model = None
tts_model = None
OUTPUT_DEVICE_INDEX = None
INPUT_DEVICE_INDEX = None
_app = None
recorder = None                  # ссылка на SpeechRecorder для меток
DPI_SCALE = 1.0

# ======================================================
# Хранилище образцов (WAV + CSV) и метрик
# ======================================================
_metrics_lock = threading.Lock()
_csv_lock = threading.Lock()

def init_sample_storage():
    if not os.path.exists(WAV_DIR):
        os.makedirs(WAV_DIR)
        print(f"[OK] Папка образцов: {os.path.abspath(WAV_DIR)}")
    if not os.path.exists(CSV_LOG_FILE):
        with open(CSV_LOG_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                ["timestamp", "gender", "f0_hz", "wav_path", "duration_sec"])
        print(f"[OK] Таблица образцов: {os.path.abspath(CSV_LOG_FILE)}")

def log_metrics(source, **kw):
    entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "source": source}
    entry.update(kw)
    try:
        with _metrics_lock:
            with open(METRICS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[!] Не удалось записать метрики: {e}")

def save_wav(audio, sr, gender, prefix="mark"):
    """Сохраняет float32-сегмент в WAV (int16). Возвращает путь или None."""
    if audio is None or len(audio) == 0 or not sr:
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filepath = os.path.join(WAV_DIR, f"{prefix}_{ts}_{gender}.wav")
    a = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    a_int = (a * 32767.0).astype(np.int16)
    try:
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(int(sr))
            wf.writeframes(a_int.tobytes())
        return filepath
    except Exception as e:
        print(f"[!] Не удалось сохранить WAV: {e}")
        return None

def log_sample_row(gender, f0, wav_path, dur_sec):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _csv_lock:
            with open(CSV_LOG_FILE, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    ts, gender or "", f"{f0:.1f}" if f0 else "",
                    wav_path if wav_path else "", f"{dur_sec:.2f}",
                ])
        if wav_path:
            if f0:
                print(f"[SAMPLE] {os.path.basename(wav_path)} -> {gender}, "
                      f"F0={f0:.0f} Гц")
            else:
                print(f"[SAMPLE] {os.path.basename(wav_path)} -> {gender}")
    except Exception as e:
        print(f"[!] Ошибка записи CSV: {e}")

def save_marks_now():
    """Немедленно сохраняет метки дикторов в конфиг."""
    try:
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        speaker_registry.save_into(cfg)
        save_config(cfg)
    except Exception as e:
        print(f"[!] Не удалось сохранить метки: {e}")

# ======================================================
# Реестр дикторов: маркировка ВВЕРХ/ВНИЗ + классификация по живому F0
# ======================================================
class SpeakerRegistry:
    """Опорные F0 мужских и женских дикторов.

    ВВЕРХ/ВНИЗ копят живые замеры F0; классификация по ближайшей опоре.
    Нет меток — порог F0_FALLBACK.
    """
    def __init__(self):
        self.male = []
        self.female = []
        self.lock = threading.Lock()

    def load(self, saved):
        if not saved:
            return
        with self.lock:
            for pool_name in ("male", "female"):
                vals = saved.get(pool_name, [])
                pool = [float(x) for x in vals
                        if isinstance(x, (int, float)) and F0_LO < x < F0_HI]
                if pool_name == "male":
                    self.male = pool[-MARK_SAMPLES_MAX:]
                else:
                    self.female = pool[-MARK_SAMPLES_MAX:]
            if self.male or self.female:
                m = (f"муж {np.median(self.male):.0f}Гц (n={len(self.male)})"
                     if self.male else "муж —")
                f = (f"жен {np.median(self.female):.0f}Гц (n={len(self.female)})"
                     if self.female else "жен —")
                print(f"[OK] Метки дикторов: {m}, {f}")

    def save_into(self, cfg):
        with self.lock:
            cfg["speaker_refs"] = {
                "male": [round(x, 1) for x in self.male[-MARK_SAMPLES_MAX:]],
                "female": [round(x, 1) for x in self.female[-MARK_SAMPLES_MAX:]],
            }

    def refs_snapshot(self):
        with self.lock:
            m = float(np.median(self.male)) if self.male else None
            f = float(np.median(self.female)) if self.female else None
            return m, f

    def mark(self, gender, f0, wav_audio=None, sr=None):
        if f0 is None or not (F0_LO < f0 < F0_HI):
            return False, "нет живого замера F0 — диктор молчит?"
        with self.lock:
            pool = self.male if gender == "male" else self.female
            pool.append(float(f0))
            if len(pool) > MARK_SAMPLES_MAX:
                pool.pop(0)
            median = float(np.median(pool))
            n = len(pool)
        if wav_audio is not None and sr:
            wav_path = save_wav(wav_audio, sr,
                                "муж" if gender == "male" else "дев")
            if wav_path:
                log_sample_row(gender, f0, wav_path, len(wav_audio) / sr)
        else:
            log_sample_row(gender, f0, None, 0.0)
        return True, (f"{gender}: F0={f0:.0f}Гц добавлен "
                      f"(n={n}, медиана {median:.0f}Гц)")

    def classify(self, f0):
        """'male' | 'female' по ближайшей опоре или порогу."""
        if f0 is None or not (F0_LO < f0 < F0_HI):
            return None
        m, f = self.refs_snapshot()
        if m is not None and f is not None:
            return "male" if abs(f0 - m) <= abs(f0 - f) else "female"
        if m is not None:
            return "male" if abs(f0 - m) < abs(f0 - F0_FALLBACK) else "female"
        if f is not None:
            return "female" if abs(f0 - f) < abs(f0 - F0_FALLBACK) else "male"
        return "male" if f0 <= F0_FALLBACK else "female"

speaker_registry = SpeakerRegistry()

# ======================================================
# Профиль голоса: живой F0 + калибровка темпа
# ======================================================
class VoiceProfile:
    def __init__(self):
        self.rate = 1.0
        self.cps = None
        self.live_f0 = None
        self.live_time = 0.0
        self.calib = []
        self.last_spoken = None
        self._last_stats_save = 0.0
        self.lock = threading.Lock()

    def load_calibration(self, pairs):
        if not pairs:
            return
        with self.lock:
            for p in pairs:
                try:
                    l, d = float(p[0]), float(p[1])
                except (TypeError, ValueError, IndexError):
                    continue
                if l >= 8 and d >= 0.7:
                    self.calib.append((l, d))
            self.calib = self.calib[-50:]
            if self.calib:
                print(f"[OK] Калибровка темпа загружена: {len(self.calib)} пар")

    def _save_stats_throttled(self):
        now = time.time()
        if now - self._last_stats_save < STATS_SAVE_SEC:
            return
        self._last_stats_save = now
        try:
            cfg = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            cfg["sub_cps_calib"] = [
                [round(l, 1), round(d, 2)] for l, d in self.calib[-50:]
            ]
            speaker_registry.save_into(cfg)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[!] Не удалось сохранить слепки: {e}")

    def observe_live(self, f0):
        if f0 is None or not (F0_LO < f0 < F0_HI):
            return
        with self.lock:
            self.live_f0 = float(f0)
            self.live_time = time.time()

    def live_f0_fresh(self):
        with self.lock:
            if (self.live_f0 is not None
                    and time.time() - self.live_time < LIVE_MAX_AGE):
                return self.live_f0
            return None

    def set_last_spoken(self, text_len):
        with self.lock:
            self.last_spoken = (int(text_len), time.time())

    def observe_calibration(self, orig_dur):
        with self.lock:
            if self.last_spoken is None:
                return
            n, t = self.last_spoken
            if time.time() - t > 4.0:
                return
            if n < 8 or orig_dur < 0.7:
                return
            self.calib.append((n, float(orig_dur)))
            if len(self.calib) > 50:
                self.calib.pop(0)
            self._save_stats_throttled()

    def predict_dur(self, text_len):
        with self.lock:
            if len(self.calib) >= CAL_MIN_PAIRS:
                ratios = [d / l for l, d in self.calib]
                return text_len * float(np.median(ratios)), \
                    f"калибровка n={len(self.calib)}"
        return text_len / CPS_SUB_DEFAULT, f"дефолт {CPS_SUB_DEFAULT} зн/с"

    def update(self, cps):
        with self.lock:
            self.cps = cps
            if cps is not None:
                self.rate = max(RATE_MIN, min(RATE_MAX, cps / BASE_CPS))
            return self.rate

    def snapshot(self):
        with self.lock:
            return self.rate

voice_profile = VoiceProfile()

# ======================================================
# DialogueTracker: голос и пол по диктору (метки + живой F0)
# ======================================================
class DialogueTracker:
    """Определяет голос и пол по классификации диктора.

    Правила:
    - пол — по ближайшей маркированной опоре (или порогу F0_FALLBACK);
    - муж -> eugene, жен -> xenia;
    - тот же пол, но F0 прыгнул >= F0_SWITCH_DELTA -> альтернативный голос
      (aidar / baya) — так различаются два говорящих одного пола;
    - нет замера -> текущий голос.
    Возвращает (голос, пол, причина).
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.last_f0 = None
        self.last_gender = None
        self.last_text = None
        self.current_voice = VOICE_MALE
        self.current_gender = "male"

    def on_phrase(self, text, f0):
        with self.lock:
            gender = speaker_registry.classify(f0)
            if gender is None:
                self.last_text = text
                return self.current_voice, self.current_gender, "нет замера F0"

            if self.last_f0 is None:
                self.current_gender = gender
                self.current_voice = (VOICE_FEMALE if gender == "female"
                                      else VOICE_MALE)
                self.last_f0 = f0
                self.last_gender = gender
                self.last_text = text
                return (self.current_voice, gender,
                        f"первая фраза: {gender}, F0={f0:.0f}Гц")

            if gender != self.last_gender:
                prev_f0 = self.last_f0
                prev_gender = self.last_gender
                self.current_gender = gender
                self.current_voice = (VOICE_FEMALE if gender == "female"
                                      else VOICE_MALE)
                self.last_f0 = f0
                self.last_gender = gender
                self.last_text = text
                return (self.current_voice, gender,
                        f"смена: F0 {prev_f0:.0f}Гц "
                        f"({prev_gender}->{gender})")

            if text != self.last_text and abs(f0 - self.last_f0) >= F0_SWITCH_DELTA:
                self.current_voice = (VOICE_FEMALE_ALT if gender == "female"
                                      else VOICE_MALE_ALT)
                self.last_f0 = f0
                self.last_text = text
                return (self.current_voice, gender,
                        f"тот же пол, другой голос: F0 {self.last_f0:.0f}"
                        f"-> {f0:.0f}Гц")

            self.last_f0 = f0
            self.last_gender = gender
            self.last_text = text
            return (self.current_voice, gender,
                    f"тот же говорящий: {gender}, F0={f0:.0f}Гц")

    def reset(self):
        with self.lock:
            self.last_f0 = None
            self.last_gender = None
            self.last_text = None
            self.current_voice = VOICE_MALE
            self.current_gender = "male"

    def snapshot(self):
        with self.lock:
            return self.current_voice

dialogue = DialogueTracker()

def gender_color(gender):
    return (COLOR_MALE if gender == "male"
            else COLOR_FEMALE if gender == "female"
            else COLOR_UNKNOWN)

# ======================================================
# Конфиг-файл
# ======================================================
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Не удалось прочитать {CONFIG_FILE}: {e}")
        return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print(f"[OK] Конфиг сохранён: {CONFIG_FILE}")
    except Exception as e:
        print(f"[!] Не удалось сохранить конфиг: {e}")

# ======================================================
# Звуковые устройства (опрос в подпроцессе с таймаутом)
# ======================================================
SD_SNIPPET = (
    "import json; import sounddevice as sd; "
    "print(json.dumps("
    "[{'i': i, 'name': d['name'], "
    "'in': d['max_input_channels'] > 0, "
    "'out': d['max_output_channels'] > 0} "
    "for i, d in enumerate(sd.query_devices())]))"
)

def list_devices_subprocess(timeout=20):
    try:
        proc = subprocess.run(
            [sys.executable, "-u", "-c", SD_SNIPPET],
            capture_output=True, text=True, timeout=timeout
        )
        out = proc.stdout.strip().splitlines()
        if proc.returncode == 0 and out:
            return json.loads(out[-1])
        print(f"[!] sounddevice вернул код {proc.returncode}")
        return None
    except subprocess.TimeoutExpired:
        print("[X] sounddevice завис и был убит по таймауту")
        return None
    except Exception as e:
        print(f"[X] Опрос устройств не удался: {e}")
        return None

def resolve_saved_device(cfg, devices, kind):
    key = "input_device" if kind == "in" else "output_device"
    saved = cfg.get(key)
    if not saved or not devices:
        return None
    idx, name = saved.get("index"), saved.get("name")
    field = "in" if kind == "in" else "out"
    if idx is not None:
        for d in devices:
            if d["i"] == idx and d[field]:
                return d["i"], d["name"]
    if name:
        for d in devices:
            if d[field] and d["name"] == name:
                return d["i"], d["name"]
        for d in devices:
            if d[field] and name and name[:15].lower() in d["name"].lower():
                return d["i"], d["name"]
    return None

def choose_device(devices, kind, cfg):
    field = "in" if kind == "in" else "out"
    label = "ВХОДА" if kind == "in" else "ВЫВОДА"

    resolved = resolve_saved_device(cfg, devices, kind)
    if resolved:
        idx, name = resolved
        print(f"[OK] Устройство {label} из конфига: [{idx}] {name}")
        return idx, name

    print(f"\n=== Доступные устройства {label} ===")
    devs = [d for d in devices if d[field]]
    for d in devs:
        print(f"{d['i']:2d}: {d['name']}")

    if kind == "in":
        keywords = ["cable output", "vb-audio virtual", "cable"]
        cands = [(d["i"], d["name"]) for d in devs
                 if any(k in d["name"].lower() for k in keywords)]
        if cands:
            idx, name = cands[0]
            print(f"\n-> Похоже на VB-Cable: [{idx}] {name}")
            ans = input("Использовать? (Enter — да, номер — другой): ").strip()
            if ans and ans.isdigit() and int(ans) in {d["i"] for d in devs}:
                idx, name = int(ans), next(d["name"] for d in devs
                                           if d["i"] == int(ans))
        else:
            raw = input("VB-Cable не найден. Введи номер устройства ввода: ").strip()
            idx, name = int(raw), next(d["name"] for d in devs if d["i"] == int(raw))
    else:
        raw = input("\nВведи номер устройства вывода: ").strip()
        idx, name = int(raw), next(d["name"] for d in devs if d["i"] == int(raw))

    return idx, name

# ======================================================
# Приглушение логов RapidOCR
# ======================================================
def silence_rapidocr_logs():
    for lname in ("RapidOCR", "rapidocr"):
        logging.getLogger(lname).setLevel(logging.ERROR)
    try:
        from loguru import logger as lu
        lu.remove()
        lu.disable("rapidocr")
        lu.disable("RapidOCR")
    except Exception:
        pass

# ======================================================
# Инициализация OCR (кириллица, попытка GPU)
# ======================================================
def init_ocr():
    silence_rapidocr_logs()

    import onnxruntime as ort
    providers = ort.get_available_providers()
    print(f"ONNX Runtime providers: {providers}")

    cyr_kwargs = {}
    try:
        from rapidocr import LangRec, OCRVersion, ModelType
        cyr_kwargs = {
            "Rec.lang_type": LangRec.CYRILLIC,
            "Rec.ocr_version": OCRVersion.PPOCRV5,
            "Rec.model_type": ModelType.MOBILE,
        }
    except ImportError:
        print("[!] Enum-классы не найдены — используем настройки OCR по умолчанию")

    det_kwargs = {
        "Det.limit_side_len": 4096,
        "Det.limit_type": "max",
        "Det.thresh": 0.2,
        "Det.box_thresh": 0.25,
    }

    def build(params):
        o = RapidOCR(params=params)
        silence_rapidocr_logs()
        return o

    if "CUDAExecutionProvider" in providers:
        try:
            ocr = build({"EngineConfig.onnxruntime.use_cuda": True,
                         **det_kwargs, **cyr_kwargs})
            print("[OK] RapidOCR готов (GPU, кириллица)")
            return ocr
        except Exception as e:
            print(f"[!] CUDA EP не завёлся: {e}")
    else:
        print("[!] CUDAExecutionProvider отсутствует — OCR на CPU")

    try:
        ocr = build({**det_kwargs, **cyr_kwargs})
        print("[OK] RapidOCR готов (CPU, кириллица)")
        return ocr
    except Exception as e:
        print(f"[!] Кириллические параметры не приняты: {e}")
        print("    Откат на настройки по умолчанию")

    ocr = build({})
    print("[OK] RapidOCR готов (настройки по умолчанию)")
    return ocr

# ======================================================
# DPI: масштаб физических/логических пикселей
# ======================================================
def compute_dpi_scale():
    global DPI_SCALE
    try:
        r = tk.Tk()
        r.withdraw()
        r.update_idletasks()
        log_w = r.winfo_screenwidth()
        r.destroy()
        phys_w, _ = _physical_screen_size()
        if phys_w and log_w and phys_w > log_w + 2:
            DPI_SCALE = phys_w / log_w
            print(f"[DPI] масштаб {DPI_SCALE:.3f}")
        else:
            DPI_SCALE = 1.0
    except Exception:
        DPI_SCALE = 1.0
    return DPI_SCALE

# ======================================================
# Выбор области мышкой (полупрозрачный оверлей, DPI-корректно)
# ======================================================
def select_region(parent=None):
    if parent is not None:
        root = tk.Toplevel(parent)
        root.transient(parent)
        root.grab_set()
    else:
        root = tk.Tk()

    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.35)
    root.configure(bg="black")

    scale = DPI_SCALE
    if scale != 1.0:
        print(f"[DPI] масштаб {scale:.3f}: логические координаты -> физические")

    canvas = tk.Canvas(root, cursor="cross", bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_text(
        root.winfo_screenwidth() // 2, 60,
        text="Зажми ЛКМ и обведи ТОЛЬКО полосу субтитров, с запасом.\n"
             "Не весь кадр — иначе мелкий текст детектор теряет.\n"
             "Esc — отмена",
        fill="yellow", font=("Arial", 24, "bold"), justify="center")

    start = [0, 0]
    rect_id = [None]
    result = {}

    def on_press(e):
        start[0], start[1] = e.x_root, e.y_root
        if rect_id[0]:
            canvas.delete(rect_id[0])
        rect_id[0] = None

    def on_drag(e):
        if rect_id[0]:
            canvas.delete(rect_id[0])
        rect_id[0] = canvas.create_rectangle(
            start[0], start[1], e.x_root, e.y_root,
            outline="lime", width=3)

    def on_release(e):
        x1, y1 = int(start[0] * scale), int(start[1] * scale)
        x2, y2 = int(e.x_root * scale), int(e.y_root * scale)
        w, h = abs(x2 - x1), abs(y2 - y1)
        if w > 20 and h > 10:
            result["box"] = (min(x1, x2), min(y1, y2), w, h)
        root.grab_release()
        root.destroy()

    def on_esc(e):
        root.grab_release()
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_esc)
    root.mainloop()
    return result.get("box")

# ======================================================
# Захват области
# ======================================================
def capture_region(box):
    left, top, width, height = box
    with mss.MSS() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        frame = np.array(sct.grab(monitor))
    if len(frame.shape) == 3 and frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    return frame

# ======================================================
# Обрезка чёрных полей (letterbox) вокруг субтитров
# ======================================================
def trim_black_borders(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]

    row_mean = gray.mean(axis=1)
    rows = np.where(row_mean > TRIM_BRIGHT)[0]
    if len(rows) == 0:
        return frame, 0, 0, False
    top = max(0, rows[0] - TRIM_PAD)
    bottom = min(h, rows[-1] + 1 + TRIM_PAD)

    col_mean = gray[top:bottom].mean(axis=0)
    cols = np.where(col_mean > TRIM_BRIGHT)[0]
    if len(cols) == 0:
        return frame, 0, 0, False
    left = max(0, cols[0] - TRIM_PAD)
    right = min(w, cols[-1] + 1 + TRIM_PAD)

    if (bottom - top) < 10 or (right - left) < 10:
        return frame, 0, 0, False
    if top == 0 and bottom == h and left == 0 and right == w:
        return frame, 0, 0, False
    return frame[top:bottom, left:right], left, top, True

# ======================================================
# Извлечение текста (OCR с дедупом и фильтром кириллицы)
# ======================================================
def _safe_list(x):
    if x is None:
        return []
    try:
        return list(x)
    except (TypeError, ValueError):
        return []

def _parse_ocr_results(results, eff, trim_left, trim_top):
    raw = []
    if hasattr(results, "txts"):
        txts = _safe_list(results.txts)
        scores = _safe_list(getattr(results, "scores", None))
        boxes = _safe_list(getattr(results, "boxes", None))
        for i, t in enumerate(txts):
            s = scores[i] if i < len(scores) else 0.0
            b = boxes[i] if i < len(boxes) else None
            raw.append((t, s, b))
    else:
        rows = (results[0] if isinstance(results, (tuple, list)) and results
                else results)
        for line in _safe_list(rows):
            if isinstance(line, (list, tuple)) and len(line) >= 3:
                raw.append((line[1], line[2], line[0]))

    texts, box_rects = [], []
    for t, s, b in raw:
        t = str(t).strip()
        try:
            s = float(s)
        except (TypeError, ValueError):
            s = 0.0
        if len(t) < MIN_TEXT_LEN or s < SCORE_MIN or not CYR_RE.search(t):
            continue
        if b is not None:
            try:
                xs = [float(p[0]) for p in b]
                ys = [float(p[1]) for p in b]
                x1 = min(xs) / eff + trim_left
                y1 = min(ys) / eff + trim_top
                x2 = max(xs) / eff + trim_left
                y2 = max(ys) / eff + trim_top
                box_rects.append((x1, y1, x2, y2))
            except Exception:
                pass
        texts.append((t, s))

    seen = set()
    uniq_t, uniq_b = [], []
    for i, (t, s) in enumerate(texts):
        if t in seen:
            continue
        seen.add(t)
        uniq_t.append((t, s))
        if i < len(box_rects):
            uniq_b.append(box_rects[i])
    return uniq_t, uniq_b

def _run_ocr_pass(frame, scale, trim_left=0, trim_top=0):
    w = frame.shape[1]
    eff = scale
    if w * eff > MAX_OCR_WIDTH:
        eff = MAX_OCR_WIDTH / w
    if eff and eff != 1.0:
        work = cv2.resize(frame, None, fx=eff, fy=eff,
                          interpolation=cv2.INTER_CUBIC)
    else:
        work = frame
        eff = 1.0

    t_ocr = time.perf_counter()
    results = ocr_model(work)
    ocr_ms = (time.perf_counter() - t_ocr) * 1000

    uniq, uniq_b = _parse_ocr_results(results, eff, trim_left, trim_top)
    raw_dbg = []
    if hasattr(results, "txts"):
        raw_dbg = [str(t) for t in _safe_list(results.txts)][:5]
    return uniq, uniq_b, raw_dbg, ocr_ms, work.shape[1], work.shape[0]

def extract_text(frame):
    frame, tl, tt, trimmed = trim_black_borders(frame)

    uniq, uniq_b, raw, ocr_ms, w, h = _run_ocr_pass(frame, OCR_SCALE, tl, tt)
    scale_note = None

    if not uniq:
        h0 = frame.shape[0]
        if h0 > 300:
            strip = frame[int(h0 * 0.5):, :]
            uniq, uniq_b, raw, ms2, w, h = _run_ocr_pass(
                strip, RETRY_SCALE, tl, tt + int(h0 * 0.5))
            scale_note = "перечитана нижняя половина x%.1f" % RETRY_SCALE
        else:
            uniq, uniq_b, raw, ms2, w, h = _run_ocr_pass(frame, RETRY_SCALE, tl, tt)
            scale_note = "перечитано x%.1f" % RETRY_SCALE
        ocr_ms += ms2

    if uniq:
        parts = ", ".join(f"{t!r} ({s:.2f})" for t, s in uniq)
        note = f", {scale_note}" if scale_note else ""
        print(f"[OCR {ocr_ms:5.0f}мс] найдено {len(uniq)}: {parts}{note}")
    elif raw:
        if time.time() - getattr(extract_text, "_last_raw", 0) > 5:
            print(f"[OCR RAW] распознано, но отфильтровано: {raw}")
            extract_text._last_raw = time.time()
    else:
        if time.time() - getattr(extract_text, "_last_empty", 0) > 5:
            print(f"[OCR {ocr_ms:5.0f}мс] пусто "
                  f"(кадр {w}x{h}, обрезка: {'да' if trimmed else 'нет'})")
            extract_text._last_empty = time.time()

    return [t for t, s in uniq], uniq_b

# ======================================================
# Оверлей субтитров: вписывается в зону захвата + плашки статуса
# ======================================================
class SubOverlay:
    """Toplevel без рамки поверх зоны субтитров.
    Фон полностью прозрачный (transparentcolor), текст цветной по диктору.
    Шрифт АВТОМАТИЧЕСКИ подгоняется: блок вписывается в высоту зоны
    (с допуском OVERLAY_FIT_FACTOR), излишки уходят ВВЕРХ от зоны.
    Оверлей прижат к низу зоны и отцентрирован, как настоящие субтитры.
    Плашки (режим, мьют) показываются через _flash_text на пару секунд;
    poll() в это время субтитры в оверлей не рисует и не гасит окно.
    """
    MAX_OVERLAY_W = 900     # логических пикселей — шире субтитры не нужны

    def __init__(self):
        self.win = None
        self.label = None
        self.box = None
        self.shown_key = None
        self.cur_color = COLOR_UNKNOWN
        self._flash_job = None
        self._in_flash = False

    def set_box(self, box):
        self.box = box

    def _ensure(self):
        if self.win is not None and self.win.winfo_exists():
            return
        app = _app
        parent = app.root if app is not None else None
        if parent is None:
            return

        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "magenta")
        self.win.configure(bg="magenta")

        self.label = tk.Label(
            self.win,
            text="",
            bg="magenta",
            fg=self.cur_color,
            font=("Arial", 22, "bold"),
            justify="center",
            wraplength=500,
        )
        self.label.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

    def _position(self):
        if self.win is None or self.box is None:
            return
        x, y, w, h = self.box
        lx, ly = int(x / DPI_SCALE), int(y / DPI_SCALE)
        lw, lh = int(w / DPI_SCALE), int(h / DPI_SCALE)

        box_w = max(280, min(lw, self.MAX_OVERLAY_W))

        # подбор шрифта: блок должен вписаться в зону (с допуском);
        # стартуем от высоты зоны, жмём по 2pt, пока не поместится
        fs = max(OVERLAY_MIN_FONT,
                 min(OVERLAY_MAX_FONT, int(lh * 0.35)))
        fit_h = lh * OVERLAY_FIT_FACTOR
        while True:
            self.label.config(font=("Arial", fs, "bold"),
                              wraplength=max(240, box_w - 12))
            self.win.geometry("")
            self.win.update_idletasks()
            rh = self.label.winfo_reqheight() + 6
            if rh <= fit_h or fs <= OVERLAY_MIN_FONT:
                break
            fs -= 2

        rw = self.label.winfo_reqwidth() + 6
        rh = self.label.winfo_reqheight() + 6

        # низ блока — на нижней границе зоны, центр по горизонтали.
        # если блок выше зоны — уходит ВВЕРХ (прозрачный, игре не мешает)
        cx = lx + (lw - rw) // 2
        cy = ly + lh - rh - 2
        self.win.geometry(f"{rw}x{rh}+{max(0, cx)}+{max(0, cy)}")

    def is_flashing(self):
        return self._in_flash

    def _cancel_flash(self):
        if self._flash_job:
            try:
                self.win.after_cancel(self._flash_job)
            except Exception:
                pass
            self._flash_job = None
        self._in_flash = False

    def _flash_text(self, text, color=COLOR_MODE_FLASH):
        """Показывает произвольное сообщение в оверлее на пару секунд."""
        if self.win is not None and self.win.winfo_exists() and self._flash_job:
            try:
                self.win.after_cancel(self._flash_job)
            except Exception:
                pass
        self._ensure()
        if self.win is None:
            return
        self._in_flash = True
        self.label.config(fg=color, text=text)
        self._position()
        self.win.deiconify()
        self._flash_job = self.win.after(
            int(OVERLAY_MODE_FLASH_SEC * 1000), self._flash_end)

    def _flash_end(self):
        self._flash_job = None
        self._in_flash = False
        # если субтитры уже пришли — show_text перезаписал текст сам;
        # иначе гасим плашку
        if self.win is not None and self.win.winfo_exists():
            self.win.withdraw()

    def show_text(self, text, gender=None):
        if self.box is None:
            return
        self._ensure()
        if self.win is None:
            return
        self._cancel_flash()
        self.win.attributes("-topmost", True)
        self.win.lift()
        if gender is not None:
            self.cur_color = gender_color(gender)
        self.label.config(fg=self.cur_color, text=text)
        self._position()
        self.win.deiconify()

    def hide(self):
        if self.win is not None and self.win.winfo_exists():
            self._cancel_flash()
            self.win.withdraw()
        self.shown_key = None

overlay = SubOverlay()

# ======================================================
# Оценка F0 (автокорреляция, медиана по кадрам)
# ======================================================
def estimate_pitch_f0(audio, sr):
    audio = audio - audio.mean()
    frame = int(sr * 0.05)
    hop = int(sr * 0.025)
    lo, hi = int(sr / 400), int(sr / 80)
    if hi >= frame:
        hi = frame - 1
    if hi <= lo:
        return None
    f0s = []
    for i in range(0, len(audio) - frame, hop):
        seg = audio[i:i + frame]
        if seg.std() < 0.01:
            continue
        seg = seg / (seg.std() + 1e-9)
        corr = np.correlate(seg, seg, "full")[frame - 1:]
        window = corr[lo:hi]
        pk = int(np.argmax(window))
        if window[pk] > 0.3 * corr[0]:
            f0s.append(sr / (lo + pk))
    if not f0s:
        return None
    return float(np.median(f0s))

# ======================================================
# Слушатель речи игры: VAD + живой F0 (50 мс) + кольцевой буфер для меток
# ======================================================
class SpeechRecorder:
    def __init__(self, device_index, seg_queue):
        self.device_index = device_index
        self.seg_queue = seg_queue
        self.sr = None
        self.noise_floor = NOISE_FLOOR_INIT
        self.speaking = False
        self.silence_run = 0.0
        self.speech_len = 0.0
        self.peak = 0.0
        self.buf = []
        self.meter_rms = 0.0
        self.meter_peak = 0.0
        self.meter_t = time.perf_counter()
        # живой замер F0
        self.live_buf = np.zeros(0, np.float32)
        self.live_t = 0.0
        # кольцевой буфер последних секунд — для сохранения WAV при метке
        self.recent_lock = threading.Lock()
        self.recent = []
        self.recent_total = 0.0

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            info = sd.query_devices(self.device_index)
            self.sr = int(info["default_samplerate"]) or 48000
            with sd.InputStream(device=self.device_index, channels=1,
                                samplerate=self.sr, blocksize=0,
                                dtype="float32", callback=self._callback):
                print(f"[REC] Слушаю игру: [{self.device_index}] "
                      f"{info['name']} @ {self.sr} Гц")
                threading.Event().wait()
        except Exception:
            print("[REC ERROR] — полный стек ниже:")
            traceback.print_exc()

    def _thresh(self):
        return max(VAD_MIN_THRESH, self.noise_floor * VAD_FLOOR_K)

    def _push_recent(self, mono, dt):
        with self.recent_lock:
            self.recent.append((mono, dt))
            self.recent_total += dt
            while self.recent_total > RECENT_AUDIO_SEC and len(self.recent) > 1:
                _, d0 = self.recent.pop(0)
                self.recent_total -= d0

    def get_recent_audio(self, sec=MARK_AUDIO_SEC):
        """Последние sec секунд звука (моно float32) или None."""
        with self.recent_lock:
            if not self.recent:
                return None
            picked, total = [], 0.0
            for mono, dt in reversed(self.recent):
                picked.insert(0, mono)
                total += dt
                if total >= sec:
                    break
            if total < 0.5:
                return None
        return np.concatenate(picked).astype(np.float32)

    def _finish_segment(self):
        seg = (np.concatenate(self.buf) if self.buf
               else np.zeros(1, np.float32))
        dur = self.speech_len
        self.buf = []
        self.speaking = False
        self.silence_run = 0.0
        self.peak = 0.0
        self.speech_len = 0.0
        if dur >= SEG_MIN_SEC:
            print(f"[REC] сегмент вырезан: {dur:.1f}с -> Whisper")
            voice_profile.observe_calibration(dur)
            if SAVE_SEGMENT_WAV:
                wav_path = save_wav(seg, self.sr, "сегмент", prefix="seg")
                if wav_path:
                    log_sample_row(None, None, wav_path, dur)
            try:
                self.seg_queue.put_nowait((seg, self.sr))
            except queue.Full:
                print("[REC] очередь полна — сегмент пропущен")

    def _callback(self, indata, frames, t, status):
        mono = indata[:, 0].copy()
        rms = float(np.sqrt(np.mean(mono ** 2)))
        dt = frames / self.sr

        # кольцевой буфер для меток (последние RECENT_AUDIO_SEC секунд)
        self._push_recent(mono, dt)

        self.meter_rms = max(self.meter_rms, rms)
        self.meter_peak = max(self.meter_peak, float(np.abs(mono).max()))
        if time.perf_counter() - self.meter_t >= REC_METER_SEC:
            peak_db = 20 * np.log10(max(self.meter_peak, 1e-6))
            print(f"[REC] RMS={self.meter_rms:.5f} пик={self.meter_peak:.3f} "
                  f"({peak_db:.0f} дБ) порог={self._thresh():.4f} "
                  f"пик_речи={self.peak:.3f} "
                  f"речь: {'ДА' if self.speaking else 'нет'}")
            self.meter_rms = 0.0
            self.meter_peak = 0.0
            self.meter_t = time.perf_counter()

        thresh = self._thresh()

        if not self.speaking:
            self.noise_floor = 0.95 * self.noise_floor + 0.05 * max(rms, 1e-6)
            if rms > thresh:
                self.speaking = True
                self.silence_run = 0.0
                self.speech_len = dt
                self.peak = rms
                self.buf = [mono]
            return

        self.buf.append(mono)
        self.peak = max(rms, self.peak * PEAK_DECAY)   # пик речи с затуханием
        if rms > thresh:
            self.speech_len += dt
            self.silence_run = 0.0
        elif rms >= self.peak * SILENCE_RATIO:
            # музыка/фон между фразами — не тишина, речь продолжается
            self.speech_len += dt
            self.silence_run = 0.0
        else:
            self.silence_run += dt

        if self.silence_run >= SEG_SILENCE_SEC or self.speech_len >= SEG_MAX_SEC:
            self._finish_segment()

        # --- живой F0: скользящее окно 200 мс, замер каждые 50 мс ---
        self.live_buf = np.concatenate([self.live_buf, mono])
        max_len = int(self.sr * (LIVE_WINDOW_SEC + 0.15))
        if len(self.live_buf) > max_len:
            self.live_buf = self.live_buf[-max_len:]
        now = time.perf_counter()
        if now - self.live_t >= LIVE_HOP_SEC:
            self.live_t = now
            w = int(self.sr * LIVE_WINDOW_SEC)
            win = self.live_buf[-w:]
            if len(win) >= w:
                f0 = estimate_pitch_f0(win, self.sr)
                voice_profile.observe_live(f0)

# ======================================================
# Перевод (офлайн Argos: не-русский -> русский)
# ======================================================
MT_LOCK = threading.Lock()
_MT = {}

def _get_translator(lang):
    if lang in _MT:
        return _MT[lang]
    tr = None
    try:
        from argostranslate import translate as at
        langs = at.get_installed_languages()
        src = next((l for l in langs if l.code == lang), None)
        dst = next((l for l in langs if l.code == "ru"), None)
        if src and dst:
            tr = src.get_translation(dst)
    except Exception as e:
        print(f"[!] Argos недоступен: {e}")
    if tr is None:
        print(f"[MT] переводчик {lang}->ru не установлен — фраза пропущена "
              f"(запусти py install_deps.py)")
    _MT[lang] = tr
    return tr

def translate_to_ru(text, lang):
    """Возвращает русский текст или None (переводчика нет)."""
    if not text or lang == "ru":
        return text
    tr = _get_translator(lang)
    if tr is None:
        return None
    t0 = time.perf_counter()
    with MT_LOCK:
        out = tr.translate(text)
    print(f"[MT] {lang}: {text[:50]!r} -> {out[:60]!r} "
          f"({(time.perf_counter() - t0) * 1000:.0f}мс)")
    return out

# ======================================================
# Развязка распознанной речи по режимам
# ======================================================
overlay_queue = queue.Queue(maxsize=4)
_speech_last = {"key": None, "t": 0.0}
_speech_lock = threading.Lock()

def route_speech(text, f0, dur):
    """Whisper-транскрипт -> озвучка (voice) или оверлей (subs)."""
    mode = get_mode()
    if mode not in ("voice", "subs") or not text:
        return
    key = norm_key(text)
    now = time.time()
    with _speech_lock:
        if (key == _speech_last["key"]
                and now - _speech_last["t"] < LAST_SPOKEN_SEC):
            return
        _speech_last["key"] = key
        _speech_last["t"] = now

    voice, gender, reason = dialogue.on_phrase(text, f0)
    dur_est, dur_src = voice_profile.predict_dur(len(text))
    rate = max(RATE_MIN, min(RATE_MAX,
               len(text) / max(0.5, dur_est) / BASE_CPS))

    if mode == "subs":
        try:
            overlay_queue.put_nowait((text, gender))
        except queue.Full:
            pass
        f0_str = f"{f0:.0f}Гц" if f0 else "—"
        print(f"[SUB] {dur:.1f}с | F0 {f0_str} -> {gender} ({reason}), "
              f"в оверлей: {text[:60]!r}")
        return

    f0_str = f"{f0:.0f}Гц" if f0 else "—"
    print(f"[SPEECH] {dur:.1f}с | F0 {f0_str} -> голос {voice} ({reason}), "
          f"rate {rate:.2f}, говорю: {text[:50]!r}")
    voice_profile.set_last_spoken(len(text))   # для калибровки темпа
    speak_text_async(text, voice, rate, dur_src)

# ======================================================
# Whisper: потоковое распознавание + перевод по предложениям
# ======================================================
def resample_to_16k(audio, sr):
    if sr == 16000:
        return audio.astype(np.float32)
    n_out = int(len(audio) * 16000 / sr)
    if n_out <= 1:
        return np.zeros(1, np.float32)
    x_new = np.linspace(0.0, len(audio) - 1.0, n_out)
    return np.interp(x_new, np.arange(len(audio)), audio).astype(np.float32)

def whisper_worker(seg_queue, model_name, whisper_lang):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("[!] Нет faster-whisper — установи: py -m pip install faster-whisper")
        return

    try:
        model = WhisperModel(model_name, device=WHISPER_DEVICE,
                             compute_type=("float16"
                                           if WHISPER_DEVICE == "cuda"
                                           else "int8"))
    except Exception as e:
        print(f"[!] Whisper не запустился ({e}) — пробую CPU")
        try:
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
        except Exception as e2:
            print(f"[!] Whisper не запустился и на CPU: {e2}")
            return

    print(f"[OK] Whisper ({model_name}) готов — потоковое распознавание")

    while True:
        seg, sr = seg_queue.get()
        try:
            dur = len(seg) / float(sr)
            if dur < SEG_MIN_SEC:
                continue

            audio16 = resample_to_16k(seg, sr)

            segments, info = model.transcribe(
                audio16, language=whisper_lang, task="transcribe",
                beam_size=1, vad_filter=True)
            lang = getattr(info, "language", None) or "ru"
            f0 = estimate_pitch_f0(audio16, 16000)

            def emit(sentence, seg_dur):
                """Перевод и отдача одного предложения в режимы."""
                if not sentence:
                    return
                ru = translate_to_ru(sentence, lang)
                if ru:
                    route_speech(ru, f0, seg_dur)
                else:
                    log_metrics(source="whisper", dur=round(seg_dur, 2),
                                f0=round(f0, 1) if f0 else None, lang=lang,
                                transcript=sentence[:120],
                                note="нет переводчика")

            # --- потоковый вывод по предложениям ---
            buf = ""
            full_text = ""
            for seg_item in segments:
                piece = seg_item.text.strip()
                if not piece:
                    continue
                full_text += " " + piece
                buf = f"{buf} {piece}".strip()

                # отдаём всё, что закончилось знаком конца предложения
                while True:
                    m = SENTENCE_FLUSH_RE.match(buf)
                    if not m:
                        break
                    sentence = m.group(1).strip()
                    buf = buf[m.end():].strip()
                    seg_dur = (seg_item.end - seg_item.start) or dur
                    if len(sentence) >= 2:
                        emit(sentence, seg_dur)

            # хвост без точки — конец VAD-сегмента, отдаём как есть
            if buf:
                emit(buf, dur)

            # --- метрики темпа по всей реплике ---
            text = full_text.strip()
            words = re.findall(r"[а-яёА-ЯЁa-zA-Z]+", text)
            cps = (len(text) / dur) if len(text) >= 12 else None

            if cps is None and len(words) < 3:
                log_metrics(source="whisper", dur=round(dur, 2),
                            f0=round(f0, 1) if f0 else None, lang=lang,
                            cps=None, transcript=text[:120], note="мало слов")
                continue

            rate = voice_profile.update(cps)

            f0_str = f"F0={f0:.0f}Гц" if f0 else "F0=?"
            cps_str = f"CPS={cps:.1f}" if cps is not None else "CPS=?"
            print(f"[VOICE] {lang} | {dur:.1f}с | транскрипт: "
                  f"{text[:60]!r}{'…' if len(text) > 60 else ''} | "
                  f"{f0_str} | {cps_str} -> rate {rate:.2f}")

            log_metrics(source="whisper", dur=round(dur, 2),
                        f0=round(f0, 1) if f0 else None, lang=lang,
                        cps=round(cps, 2) if cps is not None else None,
                        rate=round(rate, 3), transcript=text[:120])
        except Exception:
            print("[WHISPER ERROR] — полный стек ниже:")
            traceback.print_exc()

# ======================================================
# Горячие клавиши
# ======================================================
def _apply_mode_voice(e=None):
    set_mode("voice")

def _apply_mode_subs(e=None):
    set_mode("subs")

def _apply_mode_subs_voice(e=None):
    set_mode("subs_voice")

def _apply_mark_male(e=None):
    audio = None
    sr = None
    if recorder is not None and recorder.sr:
        audio = recorder.get_recent_audio(MARK_AUDIO_SEC)
        sr = recorder.sr
    f0 = voice_profile.live_f0_fresh()
    ok, msg = speaker_registry.mark("male", f0, wav_audio=audio, sr=sr)
    tag = "[OK]" if ok else "[!]"
    print(f"{tag} Метка МУЖИК: {msg}")
    if ok:
        dialogue.reset()
        save_marks_now()          # метка сразу в конфиг, не пропадёт
    log_metrics(source="mark", gender="male",
                f0=round(f0, 1) if f0 else None, ok=ok, note=msg)

def _apply_mark_female(e=None):
    audio = None
    sr = None
    if recorder is not None and recorder.sr:
        audio = recorder.get_recent_audio(MARK_AUDIO_SEC)
        sr = recorder.sr
    f0 = voice_profile.live_f0_fresh()
    ok, msg = speaker_registry.mark("female", f0, wav_audio=audio, sr=sr)
    tag = "[OK]" if ok else "[!]"
    print(f"{tag} Метка ДЕВУШКА: {msg}")
    if ok:
        dialogue.reset()
        save_marks_now()
    log_metrics(source="mark", gender="female",
                f0=round(f0, 1) if f0 else None, ok=ok, note=msg)

def _apply_reset(e=None):
    dialogue.reset()
    print("[VOICE] СБРОС: логика диалога в базовое состояние "
          f"(голос {VOICE_MALE})")
    log_metrics(source="manual", note="сброс диалога")

def _apply_reselect(e=None):
    if _app is None:
        print("[!] Превью ещё не запущено — область перевыделить нельзя")
        return
    new_box = select_region(parent=_app.root)
    if new_box:
        _app.reselect_box(new_box)
        overlay.set_box(new_box)

# --- выключатель озвучки (Right Shift) ---
_muted = False
_mute_lock = threading.Lock()

def is_muted():
    with _mute_lock:
        return _muted

def set_muted(v):
    global _muted
    with _mute_lock:
        _muted = v

def _apply_mute_toggle(e=None):
    new = not is_muted()
    set_muted(new)
    state = "ВЫКЛ" if new else "ВКЛ"
    print(f"[MUTE] Озвучка {state}")
    if new:
        # глушим всё, что звучит, и чистим очередь
        while True:
            try:
                _tts_queue.get_nowait()
            except queue.Empty:
                break
        _bump_gen()
        try:
            sd.stop()
        except Exception:
            pass
    def _flash():
        try:
            overlay._flash_text(f"● Озвучка: {state}")
        except Exception:
            pass
    if _app is not None and _app.root is not None:
        try:
            _app.root.after(0, _flash)
        except Exception:
            pass
    log_metrics(source="mute", muted=new)

def keyboard_control():
    """Фоновый поток глобальных горячих клавиш."""
    def apply_left(e=None): _apply_mode_voice()
    def apply_right(e=None): _apply_mode_subs()
    def apply_rctrl(e=None): _apply_mode_subs_voice()
    def apply_up(e=None): _apply_mark_male()
    def apply_down(e=None): _apply_mark_female()
    def apply_rshift(e=None): _apply_mute_toggle()
    def apply_ralt(e=None): _apply_reset()
    def apply_reselect(e=None): _apply_reselect()

    try:
        import keyboard as kb
        kb.on_press_key("left", apply_left)
        kb.on_press_key("right", apply_right)
        kb.on_press_key("right ctrl", apply_rctrl)
        kb.on_press_key("up", apply_up)
        kb.on_press_key("down", apply_down)
        kb.on_press_key("right shift", apply_rshift)
        kb.on_press_key("right alt", apply_ralt)
        kb.on_press_key("r", apply_reselect)
        print("[OK] Клавиши: ВЛЕВО — голос по речи, ВПРАВО — субтитры по речи, "
              "Right Ctrl — голос по сабам, ВВЕРХ/ВНИЗ — метки диктора, "
              "Right Shift — вкл/выкл озвучку, Right Alt — сброс, "
              "R — обвести область заново")
        threading.Event().wait()
    except ImportError:
        try:
            from pynput import keyboard as pk
            def on_key(key):
                try:
                    if key == pk.Key.left:
                        apply_left()
                    elif key == pk.Key.right:
                        apply_right()
                    elif key == pk.Key.ctrl_r:
                        apply_rctrl()
                    elif key == pk.Key.up:
                        apply_up()
                    elif key == pk.Key.down:
                        apply_down()
                    elif key == pk.Key.shift_r:
                        apply_rshift()
                    elif key == pk.Key.alt_r:
                        apply_ralt()
                    elif (hasattr(key, "char") and key.char
                          and key.char.lower() == "r"):
                        apply_reselect()
                except Exception:
                    pass
            with pk.Listener(on_press=on_key) as listener:
                print("[OK] Клавиши (pynput): ВЛЕВО — голос по речи, "
                      "ВПРАВО — субтитры по речи, Right Ctrl — голос по сабам, "
                      "ВВЕРХ/ВНИЗ — метки, Right Shift — вкл/выкл озвучку, "
                      "Right Alt — сброс, R — область")
                listener.join()
        except ImportError:
            print("[!] Ни keyboard, ни pynput не установлены — "
                  "горячие клавиши недоступны")
            print("    py -m pip install keyboard")
    except Exception as e:
        print(f"[!] Горячие клавиши не завелись: {e}")

# ======================================================
# TTS: фразы играют ПОДРЯД (очередь), только свежайшая выталкивает старую
# ======================================================
SENT_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")

def split_for_tts(text):
    parts = [p.strip() for p in SENT_SPLIT_RE.split(text.strip()) if p.strip()]
    out = []
    for p in parts:
        if len(p) > 140:
            sub = [s.strip() for s in p.split(",") if s.strip()]
            cur = ""
            for s in sub:
                if cur and len(cur) + len(s) + 2 > 140:
                    out.append(cur)
                    cur = s
                else:
                    cur = f"{cur}, {s}" if cur else s
            if cur:
                out.append(cur)
        else:
            out.append(p)
    return out or [text.strip()]

def apply_tts_one(model, text, speaker, rate):
    import inspect
    attempts = [
        ("rate", {"texts": [text], "speaker": speaker,
                  "sample_rate": SAMPLE_RATE, "speeech_rate": rate}),
        ("plain", {"texts": [text], "speaker": speaker,
                   "sample_rate": SAMPLE_RATE}),
        ("rate2", {"text": text, "speaker": speaker,
                   "sample_rate": SAMPLE_RATE, "speeech_rate": rate}),
        ("plain2", {"text": text, "speaker": speaker,
                    "sample_rate": SAMPLE_RATE}),
    ]
    for name, kw in attempts:
        try:
            res = model.apply_tts(**kw)
            audio = res[0] if isinstance(res, (list, tuple)) else res
            if audio is not None and len(audio) > 0:
                return audio, name
        except TypeError:
            continue
    sig = inspect.signature(model.apply_tts)
    raise RuntimeError(f"Ни одна сигнатура apply_tts не подошла. "
                       f"Реальная: {sig}")

def _normalize_chunk(audio):
    wav = np.asarray(audio, dtype=np.float32)
    mx = float(np.abs(wav).max())
    if mx > 0:
        wav = wav / mx * 0.85
    return wav

_tts_queue = queue.Queue(maxsize=1)
_gen_lock = threading.Lock()
_gen = 0

def _bump_gen():
    global _gen
    with _gen_lock:
        _gen += 1
        return _gen

def _current_gen():
    with _gen_lock:
        return _gen

def _play_chunk(wav, my_gen):
    if _current_gen() != my_gen:
        try:
            sd.stop()
        except Exception:
            pass
        return False
    if OUTPUT_DEVICE_INDEX is not None:
        sd.play(wav, SAMPLE_RATE, device=OUTPUT_DEVICE_INDEX)
    else:
        sd.play(wav, SAMPLE_RATE)
    sd.wait()
    if _current_gen() != my_gen:
        try:
            sd.stop()
        except Exception:
            pass
        return False
    return True

def tts_speaker():
    while True:
        item = _tts_queue.get()
        try:
            _speak_worker(item)
        except Exception:
            print("[TTS ERROR] — полный стек ниже:")
            traceback.print_exc()

def _speak_worker(item):
    text, voice, rate, rate_src = item
    my_gen = _current_gen()
    t0 = time.perf_counter()

    pieces = split_for_tts(text)
    if not pieces:
        return

    used = "?"
    first_wav = None
    with torch.no_grad():
        try:
            audio, used = apply_tts_one(tts_model, pieces[0], voice, rate)
            first_wav = _normalize_chunk(audio.cpu().numpy())
        except ValueError:
            print(f"[SKIP] Silero не смогла прочитать: {pieces[0]!r}")
    if first_wav is None:
        return

    first_ms = (time.perf_counter() - t0) * 1000
    print(f"[TTS] первое предложение готово за {first_ms:4.0f}мс "
          f"(вариант {used}), голос {voice}, rate {rate:.2f} ({rate_src}) — играю")

    if not _play_chunk(first_wav, my_gen):
        print("[TTS] фраза отменена (смена режима/мьют)")
        return

    pause = np.zeros(int(SAMPLE_RATE * 0.12), dtype=np.float32)
    total = len(first_wav) / SAMPLE_RATE
    for piece in pieces[1:]:
        with torch.no_grad():
            try:
                audio, used2 = apply_tts_one(tts_model, piece, voice, rate)
            except ValueError:
                print(f"[SKIP] Silero не смогла прочитать: {piece!r}")
                continue
        chunk = np.concatenate([pause, _normalize_chunk(audio.cpu().numpy())])
        total += len(chunk) / SAMPLE_RATE
        if not _play_chunk(chunk, my_gen):
            print("[TTS] фраза отменена (смена режима/мьют)")
            return

    log_metrics(source="tts", dur=None, f0=None, cps=None,
                speaker=voice, rate=round(rate, 3),
                transcript=text[:120],
                first_ms=round(first_ms), pieces=len(pieces),
                rate_src=rate_src)
    print(f"[TTS] фраза целиком озвучена: {total:.1f}с "
          f"(rate {rate:.2f}, {rate_src})")

def speak_text_async(text, voice, rate=None, rate_src="—"):
    if is_muted():
        print(f"[SKIP] озвучка выключена: {text[:40]!r}")
        return
    if not CYR_RE.search(text):
        print(f"[SKIP] нет кириллицы: {text!r}")
        return
    if rate is None:
        rate = voice_profile.snapshot()
        rate_src = "темп Whisper"
    # НЕ прерываем звучащую фразу: новая выталкивает только устаревшую
    # из очереди. Прерывание (_bump_gen) — только при смене режима и мьюте.
    if _tts_queue.full():
        try:
            _tts_queue.get_nowait()
        except queue.Empty:
            pass
    _tts_queue.put((text, voice, rate, rate_src))
    print(f"[QUEUE] фраза в очереди: {text[:50]!r}")

# ======================================================
# Окно-превью: опрос, озвучка (режимы) или оверлей
# ======================================================
class PreviewApp:
    def __init__(self, root, box):
        self.root = root
        self.box = box
        self.spoken = {}
        self.last_speak_time = 0.0
        self.photo = None
        self._stable_text = None
        self._stable_since = 0.0
        self._last_text_time = 0.0
        self._poll_delay = POLL_IDLE_SEC
        self._prev_small = None
        self._static_runs = 0
        self._last_had_text = False
        self._sub_key = None
        self._sub_first_len = 0

        root.title("alise.py — превью области распознавания")
        root.attributes("-topmost", True)
        root.geometry("+50+50")
        root.minsize(300, 140)

        self.canvas = tk.Canvas(root, bg="black", highlightthickness=1,
                                highlightbackground="#333")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.status = tk.Label(root, text="...", anchor="w", justify="left",
                               bg="#111", fg="#cfcfcf", font=("Consolas", 10))
        self.status.pack(fill=tk.X, padx=4, pady=(0, 2))

        btns = tk.Frame(root, bg="#111")
        btns.pack(fill=tk.X, padx=4, pady=(0, 6))
        tk.Button(btns, text="Голос (речь)",
                  command=_apply_mode_voice).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Субтитры (речь)",
                  command=_apply_mode_subs).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Голос (сабы)",
                  command=_apply_mode_subs_voice).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Обвести область заново",
                  command=self.reselect).pack(side=tk.LEFT, padx=4)
        tk.Button(btns, text="Выход",
                  command=self.quit).pack(side=tk.RIGHT, padx=4)

        self.resize_canvas()
        w = max(300, self.prev_w + 20)
        h = max(140, self.prev_h + 90)
        root.geometry(f"{w}x{h}+50+50")
        print(f"[WINDOW] превью открыто: {w}x{h}+50+50 "
              f"(канвас {self.prev_w}x{self.prev_h}, область {self.box})")

        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.frame_cnt = 0
        self.t_fps = time.perf_counter()
        root.after(50, self.poll)

    def resize_canvas(self):
        bw = max(40, self.box[2])
        bh = max(40, self.box[3])
        scale = PREVIEW_WIDTH / bw
        if scale > 4:
            scale = 4
        self.prev_scale = scale
        self.prev_w = max(40, int(bw * scale))
        self.prev_h = max(40, int(bh * scale))
        self.canvas.config(width=self.prev_w, height=self.prev_h)

    def reselect_box(self, new_box):
        self.box = new_box
        self._stable_text = None
        self._stable_since = 0.0
        self._prev_small = None
        self._sub_key = None
        cfg = load_config()
        cfg["region"] = {"x": new_box[0], "y": new_box[1],
                         "w": new_box[2], "h": new_box[3]}
        save_config(cfg)
        self.resize_canvas()
        print(f"[OK] Новая область: x={new_box[0]}, y={new_box[1]}, "
              f"w={new_box[2]}, h={new_box[3]}")

    def reselect(self):
        new_box = select_region(parent=self.root)
        if new_box:
            self.reselect_box(new_box)

    def quit(self):
        self.root.destroy()
        os._exit(0)

    def poll(self):
        current_text = ""
        t0 = time.perf_counter()
        try:
            frame = capture_region(self.box)
            cap_ms = (time.perf_counter() - t0) * 1000

            sw = 160
            sh = max(8, int(self.box[3] * sw / max(1, self.box[2])))
            small = cv2.resize(frame, (sw, sh), interpolation=cv2.INTER_AREA)
            g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.int16)
            bright = float((g > 70).mean())
            static = (self._prev_small is not None
                      and float(np.abs(g - self._prev_small).mean()) < 1.5)
            self._prev_small = g

            mode = get_mode()

            # OCR нужен только в режиме «Голос по сабам»
            if mode != "subs_voice" or bright < 0.003:
                texts, boxes = [], []
                self._static_runs = 0
            elif (static and self._static_runs >= OCR_SKIP_STATIC
                  and not self._last_had_text):
                texts, boxes = [], []
                self._static_runs += 1
            else:
                self._static_runs = 0
                texts, boxes = extract_text(frame)
            self._last_had_text = bool(texts)

            ocr_ms = (time.perf_counter() - t0) * 1000 - cap_ms

            self.draw_preview(frame, boxes)

            current_text = " ".join(texts).strip()
            now = time.time()

            # --- речь игры: оверлей в режиме subs, иначе гасим и чистим ---
            if mode == "subs":
                while True:
                    try:
                        txt, gender = overlay_queue.get_nowait()
                    except queue.Empty:
                        break
                    key = norm_key(txt)
                    if (key not in self.spoken
                            or now - self.spoken[key] >= LAST_SPOKEN_SEC):
                        self.spoken[key] = now
                        overlay.show_text(txt, gender)
                        print(f"[SUB] оверлей ({gender}): {txt[:60]!r}")
            else:
                # плашку режима/мьюта не гасим — poll раньше её убивал
                if not overlay.is_flashing():
                    overlay.hide()
                while not overlay_queue.empty():
                    try:
                        overlay_queue.get_nowait()
                    except queue.Empty:
                        break

            # --- линия субтитра на экране (режим «Голос по сабам») ---
            if current_text:
                key_now = norm_key(current_text)
                if self._sub_key and key_now.startswith(self._sub_key):
                    pass
                else:
                    self._sub_key = key_now
                    self._sub_first_len = len(current_text)
            elif self._sub_key and now - self._last_text_time > 0.5:
                self._sub_key = None
                self._stable_text = None

            if current_text:
                self._last_text_time = now

                self.spoken = {k: ts for k, ts in self.spoken.items()
                               if now - ts < LAST_SPOKEN_SEC}

                if current_text != self._stable_text:
                    self._stable_text = current_text
                    self._stable_since = now

                stable_sec = now - self._stable_since
                lineage = self._sub_key
                if (stable_sec >= TEXT_STABLE_SEC
                        and lineage and lineage not in self.spoken
                        and now - self.last_speak_time >= COOLDOWN_SEC
                        and mode == "subs_voice"):

                    # OCR-фраза готова; живой F0 всё это время слушался
                    # параллельно — голос берём под текущего диктора
                    f0_live = voice_profile.live_f0_fresh()
                    voice, gender, reason = dialogue.on_phrase(current_text,
                                                               f0_live)

                    dur_est, dur_src = voice_profile.predict_dur(
                        len(current_text))
                    rate = max(RATE_MIN, min(RATE_MAX,
                               len(current_text) / max(0.5, dur_est) / BASE_CPS))

                    self.spoken[lineage] = now
                    self.last_speak_time = now
                    voice_profile.set_last_spoken(len(current_text))
                    f0_now = voice_profile.live_f0
                    f0_str = f"{f0_now:.0f}Гц" if f0_now else "—"
                    print(f"[SPEAK] живой F0 {f0_str} -> голос {voice} "
                          f"({reason}), rate {rate:.2f} "
                          f"(ориг ~{dur_est:.1f}с, {dur_src}), "
                          f"говорю: {current_text[:50]!r}")
                    speak_text_async(current_text, voice, rate, dur_src)
            else:
                if get_mode() != "subs" and not overlay.is_flashing():
                    overlay.hide()

            voice_now = dialogue.snapshot()
            rate = voice_profile.snapshot()
            live = voice_profile.live_f0
            live_str = (f"{live:.0f}Гц"
                        if (live and now - voice_profile.live_time < LIVE_MAX_AGE)
                        else "—")
            m_refs, f_refs = speaker_registry.refs_snapshot()
            m_str = f"{m_refs:.0f}" if m_refs else "—"
            f_str = f"{f_refs:.0f}" if f_refs else "—"
            mute_str = "ВЫКЛ" if is_muted() else "ВКЛ"
            mode_str = ("ГОЛОС (речь)" if mode == "voice"
                        else "СУБТИТРЫ (речь)" if mode == "subs"
                        else "ГОЛОС (сабы)")
            self.status.config(
                text=f"{mode_str}  |  озвучка {mute_str}  |  "
                     f"область {self.box[2]}x{self.box[3]}  |  "
                     f"захват {cap_ms:.0f}мс + OCR {ocr_ms:.0f}мс  |  "
                     f"голос: {voice_now} (rate {rate:.2f}, F0 {live_str})  |  "
                     f"метки: муж {m_str}Гц / жен {f_str}Гц  |  "
                     f"текст: {current_text if current_text else '—'}")

            elapsed = time.perf_counter() - t0
            self.frame_cnt += 1
            if time.perf_counter() - self.t_fps >= 10:
                print(f"[LOOP] FPS {self.frame_cnt / 10:.1f} "
                      f"(шаг {self._poll_delay * 1000:.0f}мс), "
                      f"кадр {elapsed * 1000:.0f}мс "
                      f"(захват {cap_ms:.0f} + OCR {ocr_ms:.0f})")
                self.frame_cnt, self.t_fps = 0, time.perf_counter()

            self._poll_delay = POLL_ACTIVE_SEC
        except Exception:
            print("[POLL ERROR] — полный стек ниже:")
            traceback.print_exc()
            self._poll_delay = POLL_IDLE_SEC

        self.root.after(int(self._poll_delay * 1000), self.poll)

    def draw_preview(self, frame, boxes):
        if not PIL_OK:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.prev_w // 2, self.prev_h // 2,
                text="Нет Pillow — превью недоступно.\n"
                     "py -m pip install pillow",
                fill="#ff6666", font=("Arial", 12))
            return

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(img).resize((self.prev_w, self.prev_h))
        self.photo = ImageTk.PhotoImage(pil)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        s = self.prev_scale
        for (x1, y1, x2, y2) in boxes:
            self.canvas.create_rectangle(
                x1 * s, y1 * s, x2 * s, y2 * s,
                outline="lime", width=2)

# ======================================================
# Main
# ======================================================
def main():
    global ocr_model, tts_model, OUTPUT_DEVICE_INDEX, INPUT_DEVICE_INDEX
    global _app, recorder

    cfg = load_config()
    print(f"Метрики модуляции пишутся в: {os.path.abspath(METRICS_FILE)}")
    init_sample_storage()
    voice_profile.load_calibration(cfg.get("sub_cps_calib"))
    speaker_registry.load(cfg.get("speaker_refs"))

    global CURRENT_MODE
    CURRENT_MODE = cfg.get("mode", "voice")
    if CURRENT_MODE not in VALID_MODES:
        CURRENT_MODE = "voice"

    global WHISPER_MODEL, WHISPER_LANG
    WHISPER_MODEL = cfg.get("whisper_model", WHISPER_MODEL)
    wl = cfg.get("whisper_lang", "auto")
    WHISPER_LANG = None if wl in (None, "", "auto") else wl

    print(f"[i] Режимы: ВЛЕВО — голос по речи, ВПРАВО — субтитры по речи, "
          f"Right Ctrl — голос по сабам. Текущий: {MODE_NAMES[CURRENT_MODE]}")
    print(f"[i] Метки дикторов: ВВЕРХ — мужик, ВНИЗ — девушка. "
          f"Right Shift — вкл/выкл озвучку, Right Alt — сброс, "
          f"R — область заново. "
          f"Без меток классификация по порогу {F0_FALLBACK:.0f} Гц")
    print(f"[i] Whisper: {WHISPER_MODEL}, язык: "
          f"{WHISPER_LANG if WHISPER_LANG else 'авто'}")

    compute_dpi_scale()

    # --- звуковые устройства ---
    devices = list_devices_subprocess()
    if devices:
        in_idx, in_name = choose_device(devices, "in", cfg)
        out_idx, out_name = choose_device(devices, "out", cfg)
        cfg["input_device"] = {"index": in_idx, "name": in_name}
        cfg["output_device"] = {"index": out_idx, "name": out_name}
        save_config(cfg)
        INPUT_DEVICE_INDEX = in_idx
        OUTPUT_DEVICE_INDEX = out_idx
    else:
        print("[!] Список устройств недоступен — вывод на устройство "
              "по умолчанию")
        OUTPUT_DEVICE_INDEX = None

    # --- OCR ---
    print("Инициализация RapidOCR...")
    ocr_model = init_ocr()

    # --- TTS ---
    print(f"Загрузка Silero TTS (device={DEVICE})...")
    tts_model, _ = torch.hub.load("snakers4/silero-models", "silero_tts",
                                  language="ru", speaker="v4_ru",
                                  trust_repo=True)
    tts_model.to(DEVICE)
    print("[OK] Silero v4 готов.")

    # --- поток-спикер: единственный, кто играет звук ---
    threading.Thread(target=tts_speaker, daemon=True).start()

    # --- слушатель речи (живой F0) + Whisper (распознавание и перевод) ---
    if INPUT_DEVICE_INDEX is not None:
        seg_queue = queue.Queue(maxsize=3)
        recorder = SpeechRecorder(INPUT_DEVICE_INDEX, seg_queue)
        recorder.start()
        threading.Thread(target=whisper_worker,
                         args=(seg_queue, WHISPER_MODEL, WHISPER_LANG),
                         daemon=True).start()
    else:
        print("[!] Входное устройство недоступно — живой F0 отключён, "
              "голос всегда будет базовым")

    # --- горячие клавиши ---
    threading.Thread(target=keyboard_control, daemon=True).start()

    # --- выбор области: ОБЯЗАТЕЛЬНО спрашиваем, даже если есть в конфиге ---
    saved = cfg.get("region")
    box = None
    if saved:
        box = (saved["x"], saved["y"], saved["w"], saved["h"])
        print(f"[OK] Сохранённая область: x={box[0]}, y={box[1]}, "
              f"w={box[2]}, h={box[3]}")
        ans = input("Использовать её? (Enter — да, любой текст+Enter — "
                    "обвести заново): ").strip()
        if ans:
            box = None

    if box is None:
        print("\nОбведи мышкой полосу субтитров В ИГРЕ "
              "(консоль убери с этого места!).")
        box = select_region()
    if not box:
        print("[!] Область не выделена — выход.")
        os._exit(0)

    cfg["region"] = {"x": box[0], "y": box[1], "w": box[2], "h": box[3]}
    cfg["mode"] = CURRENT_MODE
    save_config(cfg)
    overlay.set_box(box)

    print(f"Отслеживаю область: x={box[0]}, y={box[1]}, "
          f"w={box[2]}, h={box[3]}")
    print("Клавиши: ВЛЕВО/ВПРАВО/Right Ctrl — режимы, ВВЕРХ/ВНИЗ — метки "
          "диктора, Right Shift — вкл/выкл озвучку, Right Alt — сброс, "
          "R — область заново. Закрой окно превью, чтобы остановить.")

    root = tk.Tk()
    root.title("alise.py — превью области")
    root.geometry("+50+50")
    root.attributes("-topmost", True)
    app = PreviewApp(root, box)
    _app = app
    root.update_idletasks()
    root.lift()
    root.focus_force()
    root.after(1000, lambda: (root.lift(), root.attributes("-topmost", True)))
    root.mainloop()
    print("\nОстановлено.")

if __name__ == "__main__":
    main()

