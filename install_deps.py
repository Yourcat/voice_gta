# -*- coding: utf-8 -*-
"""
install_deps.py — авто-установка окружения для alise.py.

Пакеты ставятся из requirements.txt, лежащего рядом с этим скриптом.
Отдельно ставится PyTorch (CUDA при наличии NVIDIA, иначе CPU),
удаляется конфликтный paddle, скачивается пакет Argos en->ru
и модель Whisper.

Запуск:  py install_deps.py
Скрипт идемпотентный: повторный запуск не ломает уже установленное.
Также вызывается из alise.py при старте (ensure_environment).
"""

import subprocess
import sys
import os
import importlib
import importlib.metadata

REQUIREMENTS_FILE = "requirements.txt"

# torch не включаем в requirements.txt: для NVIDIA — особый индекс,
# для остальных — обычный CPU/wheel с PyPI
TORCH_CUDA_INDEX = "https://download.pytorch.org/whl/cu121"

CONFLICTING_PACKAGES = ["paddleocr", "paddle", "paddlepaddle"]

# карта: имя пакета в requirements -> имя модуля для проверки импорта
IMPORT_ALIASES = {
    "opencv-python": "cv2",
    "faster-whisper": "faster_whisper",
    "pillow": "PIL",
    "sounddevice": "sounddevice",
}

WHISPER_MODEL = "large-v3-turbo"


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


def _pkg_installed(name):
    """Пакет числится установленным (по метаданным pip)."""
    try:
        importlib.metadata.distribution(name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False
    except Exception:
        return False


def read_requirements():
    """Читает requirements.txt: строки без комментариев и пустые."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        REQUIREMENTS_FILE)
    if not os.path.exists(path):
        print(f"[X] Не найден {REQUIREMENTS_FILE} — положи рядом со скриптом")
        print(f"    Ожидался путь: {path}")
        return None
    pkgs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            pkgs.append(s)
    if not pkgs:
        print(f"[X] {REQUIREMENTS_FILE} пустой — добавь список пакетов")
        return None
    print(f"[*] Пакетов в {REQUIREMENTS_FILE}: {len(pkgs)}")
    for p in pkgs:
        print(f"    - {p}")
    return pkgs


def missing_from_requirements(pkgs):
    """Какие пакеты из requirements ещё не доступны.

    Пакет считается установленным, если он есть в метаданных pip.
    Если метаданные есть, но импорт падает — печатаем настоящую ошибку
    (DLL, конфликт версий) и НЕ ставим пакет повторно: pip это не чинит.
    """
    missing = []
    for pkg in pkgs:
        base = (pkg.split(";")[0].strip()
                .split("==")[0].split(">=")[0].split("<=")[0].strip())
        mod = IMPORT_ALIASES.get(base, base.replace("-", "_"))
        try:
            importlib.import_module(mod)
            continue
        except Exception as e:
            if _pkg_installed(base):
                print(f"[!] {base} установлен, но импорт падает: "
                      f"{type(e).__name__}: {e}")
                print("    Повторная установка через pip не поможет —")
                print("    обычно это DLL или конфликт версий.")
                continue
            missing.append(pkg)
    return missing


def install_from_requirements():
    pkgs = read_requirements()
    if pkgs is None:
        return False

    missing = missing_from_requirements(pkgs)
    if not missing:
        print("[OK] Все пакеты из requirements.txt уже установлены")
        return True

    print(f"[*] Не хватает: {', '.join(missing)}")
    # ставим только недостающие: быстрее и не пересоздаёт окружение
    pip_install(missing, check=False)

    still = missing_from_requirements(pkgs)
    if still:
        print(f"[!] Не импортируются: {', '.join(still)}")
        print("    Полная установка всего списка:")
        pip_install(["-r", REQUIREMENTS_FILE], check=False)
        still = missing_from_requirements(pkgs)
    if still:
        print(f"[!] Часть пакетов не установилась: {', '.join(still)}")
        print("    Смотри сообщения pip выше; alise.py сообщит недостающее")
        return False
    print("[OK] Пакеты из requirements.txt установлены")
    return True


def install_torch():
    print("[*] Установка PyTorch")
    try:
        import torch  # noqa: F401
        print("[OK] PyTorch уже установлен:", torch.__version__)
        return
    except ImportError:
        pass

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

    # AMD/CPU: CUDA не используется, ставим обычный wheel с PyPI
    print("[*] Ставлю PyTorch (CPU — для AMD/NVIDIA без CUDA)")
    pip_install(["torch"], check=False)
    try:
        import torch  # noqa: F401
        print("[OK] PyTorch установлен:", torch.__version__)
    except ImportError:
        print("[!] PyTorch не установился — Whisper не заработает")


def install_argos_pair():
    print("[*] Установка пакета перевода Argos en->ru")
    try:
        # get_installed_languages живёт в argostranslate.translate,
        # а не в argostranslate.package
        from argostranslate import package, translate
        installed = translate.get_installed_languages()
        src = next((l for l in installed if l.code == "en"), None)
        already = (src is not None
                   and any(t.code == "ru" for t in src.translations_to()))
        if already:
            print("[OK] Argos en->ru уже установлен")
            return
        print("[*] Скачиваю пакет Argos en_ru (~250 МБ)")
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


def uninstall_conflicting():
    print("[*] Удаление конфликтных пакетов (paddle мешает RapidOCR)")
    pip_install(["uninstall", "-y"] + CONFLICTING_PACKAGES, check=False)


def fix_protobuf_if_needed():
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
    try:
        pkgs = read_requirements()
    except Exception:
        pkgs = None
    if pkgs is None:
        return []
    missing = missing_from_requirements(pkgs)
    if missing:
        print(f"[!] Не хватает пакетов: {', '.join(missing)}")
        print("    Запусти: py install_deps.py")
    return missing


def main():
    print("=" * 60)
    print("Установка окружения для alise.py")
    print("=" * 60)

    ensure_pip()

    uninstall_conflicting()
    ok = install_from_requirements()
    install_torch()
    fix_protobuf_if_needed()
    install_argos_pair()
    predownload_whisper()

    print("=" * 60)
    if ok:
        print("[OK] Установка завершена. Запускай: py alise.py")
    else:
        print("[!] Есть непоставленные пакеты — смотри сообщения выше,")
        print("    потом запусти py install_deps.py ещё раз")
    print("=" * 60)


if __name__ == "__main__":
    main()
