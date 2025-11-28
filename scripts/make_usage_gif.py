from PIL import Image, ImageDraw, ImageFont
import os

W, H = 900, 540
SLIDES = [
    'AI Knowledge Console — Quick Demo',
    '1) docker compose up -d',
    '2) Open http://localhost',
    '3) Upload a document',
    "4) Chat with 'Use documents' enabled",
    'Sources appear below the answer',
]

def main():
    frames = []
    font = ImageFont.load_default()
    for txt in SLIDES:
        img = Image.new('RGB', (W, H), 'white')
        d = ImageDraw.Draw(img)
        d.rectangle([40, 40, W - 40, H - 40], outline=(30, 144, 255), width=6)
        d.text((70, 80), 'AI Knowledge Console', fill=(0, 0, 0), font=font)
        d.line([(70, 105), (370, 105)], fill=(0, 0, 0), width=2)
        d.text((70, 140), txt, fill=(0, 0, 0), font=font)
        hint = 'Demo: upload a doc, enable RAG, chat'
        d.text((70, H - 80), hint, fill=(90, 90, 90), font=font)
        frames.append(img)

    outdir = os.path.join('docs', 'media')
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, 'usage.gif')
    frames[0].save(outfile, save_all=True, append_images=frames[1:], duration=900, loop=0)
    print('Wrote:', outfile, os.path.getsize(outfile), 'bytes')

if __name__ == '__main__':
    main()

