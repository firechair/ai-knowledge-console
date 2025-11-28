import os
import time
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("DEMO_BASE_URL", "http://localhost")
OUTDIR = os.path.join("docs", "media")
os.makedirs(OUTDIR, exist_ok=True)

shots = []

def snap(page, name):
    p = os.path.join(OUTDIR, name)
    page.screenshot(path=p, full_page=True)
    shots.append(p)

def make_gif(paths, outfile):
    images = [Image.open(p).convert("RGB") for p in paths]
    images[0].save(outfile, save_all=True, append_images=images[1:], duration=900, loop=0)

def main():
    tmpfile = "/tmp/demo_console.txt"
    with open(tmpfile, "w") as f:
        f.write("This is a demo document for RAG. It contains a couple of sentences for testing.")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(BASE_URL, wait_until="networkidle")
        snap(page, "demo_1_home.png")

        try:
            page.get_by_text("Documents").click()
            page.set_input_files("input[type=file]", tmpfile)
            page.get_by_role("button", name="Upload").click()
            page.wait_for_timeout(1200)
        except Exception:
            pass
        snap(page, "demo_2_documents.png")

        try:
            page.get_by_text("Chat").click()
            sent = False
            for sel in ["textarea", "input[type=text]"]:
                loc = page.locator(sel)
                if loc.count() > 0:
                    loc.first.fill("Hello demo — using Traefik local proxy")
                    sent = True
                    break
            if sent:
                page.get_by_role("button", name="Send").click()
                page.wait_for_timeout(1400)
        except Exception:
            pass
        snap(page, "demo_3_chat.png")

        browser.close()
        time.sleep(0.2)

    outfile = os.path.join(OUTDIR, "usage.gif")
    make_gif(shots, outfile)
    print("Wrote:", outfile, os.path.getsize(outfile), "bytes")

if __name__ == "__main__":
    main()

