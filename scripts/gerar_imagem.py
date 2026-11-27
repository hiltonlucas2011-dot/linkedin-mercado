#!/usr/bin/env python3
"""Gera a foto do post com a API de imagens da OpenAI e salva em 1080x1350 (4:5, formato do feed do LinkedIn).

Uso:
  python3 scripts/gerar_imagem.py posts/<id>/post.json

Lê o campo "prompt_imagem" do post.json e grava posts/<id>/post.png.
A chave da OpenAI não fica no código: neste ambiente o proxy de rede injeta a chave salva
nas chamadas para api.openai.com. Fora dele, defina OPENAI_API_KEY.
"""
import base64
import io
import json
import os
import sys
import urllib.error
import urllib.request

from PIL import Image

ESTILO = (
    "Fotografia editorial realista, luz natural suave, cores naturais, profundidade de campo rasa, "
    "lente 35mm, composição limpa com espaço livre, cenário brasileiro contemporâneo. "
    "Sem texto, sem letras, sem números, sem logotipos, sem marcas reconhecíveis, sem marca d'água. "
    "Pessoas, se houver, de costas, de perfil ou fora de foco, sem rosto identificável."
)


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 scripts/gerar_imagem.py posts/<id>/post.json")
    post_path = sys.argv[1]
    post = json.load(open(post_path, encoding="utf-8"))
    cfg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "config.json"), encoding="utf-8"))["imagem"]

    prompt = post.get("prompt_imagem", "").strip()
    if not prompt:
        sys.exit("post.json não tem 'prompt_imagem'.")

    body = json.dumps({
        "model": cfg.get("modelo", "gpt-image-1"),
        "prompt": f"{prompt}\n\nEstilo: {ESTILO}",
        "size": cfg.get("tamanho_gerado", "1024x1536"),
        "quality": cfg.get("qualidade", "high"),
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Content-Type": "application/json",
            # Valor provisório: o proxy do ambiente troca pela chave salva.
            "Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "sk-placeholder"),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Erro da OpenAI ({e.code}): {e.read().decode(errors='replace')[:500]}")

    item = data["data"][0]
    if "b64_json" in item:
        raw = base64.b64decode(item["b64_json"])
    else:
        with urllib.request.urlopen(item["url"], timeout=120) as r:
            raw = r.read()

    img = Image.open(io.BytesIO(raw)).convert("RGB")
    # Recorta para 4:5 pelo centro e redimensiona para 1080x1350
    w, h = img.size
    alvo = 4 / 5
    if w / h > alvo:
        nw = int(h * alvo); img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / alvo); img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    img = img.resize((1080, 1350), Image.LANCZOS)

    out = os.path.join(os.path.dirname(post_path), "post.png")
    img.save(out, optimize=True)
    print("ok:", out)


if __name__ == "__main__":
    main()
