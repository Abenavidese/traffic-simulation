from pathlib import Path

FILES = [
    # Entry / app
    "frontend/ui/app.py",

    # Views
    "frontend/ui/views/canvas_view.py",
    "frontend/ui/views/stats_panel.py",
    "frontend/ui/views/controls_panel.py",

    # Rendering
    "frontend/ui/render/sprite_loader.py",
    "frontend/ui/render/renderer.py",

    # Assets folders (no files here; you add images manually)
    # We'll create folders below.

    # Docs
    "frontend/README.md",
]

PACKAGES = [
    "frontend",
    "frontend/ui",
    "frontend/ui/views",
    "frontend/ui/render",
]

ASSET_DIRS = [
    "frontend/assets",
    "frontend/assets/semaforos",
    "frontend/assets/carros",
    "frontend/assets/road",
]


def write_todo(path: Path) -> None:
    if path.suffix == ".md":
        content = "# TODO\n"
    else:
        content = "# TODO\n"
    path.write_text(content, encoding="utf-8")


def main() -> int:
    root = Path.cwd()

    # Create package dirs + __init__.py with TODO
    for pkg in PACKAGES:
        d = root / pkg
        d.mkdir(parents=True, exist_ok=True)
        init_file = d / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# TODO\n", encoding="utf-8")

    # Create asset directories (empty)
    for ad in ASSET_DIRS:
        (root / ad).mkdir(parents=True, exist_ok=True)

    # Create files with # TODO
    for f in FILES:
        p = root / f
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            write_todo(p)

    print("✅ Frontend creado con estructura y archivos TODO en ./frontend")
    print("📁 Recuerda colocar tus imágenes en:")
    print("   - frontend/assets/semaforos/  (rojo.png, amarillo.png, verde.png)")
    print("   - frontend/assets/carros/     (car_1.png, car_2.png, ...)")
    print("   - frontend/assets/road/       (background.png opcional)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
