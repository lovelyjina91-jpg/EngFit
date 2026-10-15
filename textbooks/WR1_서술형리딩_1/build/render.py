#!/usr/bin/env python3
"""HTML → PDF. 사용: python3 build/render.py out/student.html out/student.pdf s|t"""
import sys, json, asyncio, pathlib
from playwright.async_api import async_playwright
async def main(src, dst, kind):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto("file://" + str(pathlib.Path(src).resolve()))
        await pg.wait_for_timeout(800)
        fit = await pg.evaluate("window.__fit||[]")
        for f in fit:
            flag = "  ← 85% 미만: 내용 줄이기 필요" if f["scale"] < 0.85 else ""
            print(f"  p{f['page']}: 글자 {int(f['scale']*100)}%{flag}")
        await pg.pdf(path=dst, format="A4", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"} if kind=="s" else {"top":"13mm","bottom":"14mm","left":"17mm","right":"17mm"}, display_header_footer=(kind=="t"), header_template="<span></span>", footer_template='<div style="font-size:7pt;color:#8a92a3;width:100%;text-align:center">영핏 서술형 리딩 1 · 선생님용 · <span class="pageNumber"></span></div>')
        if kind == "t":
            cov = pathlib.Path(src).with_name("teacher_cover.html")
            if cov.exists():
                await pg.goto("file://" + str(cov.resolve())); await pg.wait_for_timeout(500)
                tmp = str(pathlib.Path(dst).with_suffix(".cover.pdf"))
                await pg.pdf(path=tmp, format="A4", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
                from pypdf import PdfReader, PdfWriter
                w = PdfWriter()
                for f in (tmp, dst):
                    for page in PdfReader(f).pages: w.add_page(page)
                with open(dst, "wb") as fh: w.write(fh)
                pathlib.Path(tmp).unlink()
        await b.close()
asyncio.run(main(*sys.argv[1:4]))
