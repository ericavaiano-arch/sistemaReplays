import argparse
import sys
import time

from buffer import FrameBuffer
from recorder import save_clip
from uploader import upload


def parse_args():
    parser = argparse.ArgumentParser(description="Sistema de Replay de Câmera")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Salva o clip localmente sem fazer upload para o R2",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Pasta de saída para os clips (padrão: pasta temporária do sistema)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    buf = FrameBuffer()
    buf.start()

    # Aguarda a câmera estabilizar
    time.sleep(1.0)

    mode = "DRY-RUN (sem upload)" if args.dry_run else "modo normal (com upload para R2)"
    print(f"\nSistema de Replay iniciado em {mode}.")
    print("Pressione ENTER para salvar os últimos 30 segundos.")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            input()  # bloqueia até ENTER

            frames = buf.snapshot()
            if not frames:
                print("Buffer ainda vazio, aguarde alguns segundos e tente novamente.")
                continue

            print(f"Capturando replay com {len(frames)} frames...")

            try:
                filepath = save_clip(frames, frame_size=buf.frame_size, output_dir=args.output_dir)
            except Exception as exc:
                print(f"Erro ao salvar clip: {exc}")
                continue

            if args.dry_run:
                print(f"[DRY-RUN] Clip disponível em: {filepath}")
                continue

            try:
                url = upload(filepath)
                print(f"\nReplay disponível em:\n  {url}\n")
            except Exception as exc:
                print(f"Erro no upload: {exc}")
                print(f"Clip mantido localmente em: {filepath}")

    except KeyboardInterrupt:
        print("\nEncerrando...")
        buf.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
