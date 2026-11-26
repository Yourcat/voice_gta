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
