"""Run against the built static preview. Set BROWSER_PATH to use another Chromium browser."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

url = os.environ.get("PREVIEW_URL", "http://127.0.0.1:4317")
edge = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get("BROWSER_PATH",str(edge) if edge.exists() else None),
                                args=["--enable-unsafe-swiftshader","--use-angle=swiftshader"])
    page = browser.new_page(viewport={"width":1366,"height":900})
    errors = []
    page.on("pageerror",lambda e: errors.append(str(e)))
    page.goto(url)
    expect(page.get_by_role("heading",name="Audit overview")).to_be_visible()
    page.keyboard.press("Tab")
    expect(page.get_by_text("Skip to content")).to_be_focused()
    expect(page.get_by_role("button",name="Pause animation")).to_be_visible()
    expect(page.locator(".visualFoot span")).to_have_text("Inspection",timeout=20000)
    page.get_by_role("button",name="Pause animation").click()
    expect(page.get_by_role("button",name="Play animation")).to_be_visible()
    page.get_by_role("link",name="Explore Security Audit").click()
    page.get_by_placeholder("Title, ID or component").fill("CG-001")
    expect(page.locator(".row")).to_have_count(1)
    page.locator(".row").click()
    expect(page.get_by_role("heading",name="Owner check missing")).to_be_visible()
    page.get_by_role("link",name="Code comparison",exact=True).click()
    page.locator("select").select_option("CG-004")
    expect(page.get_by_text("Read the role from the database and deny unauthorized access.")).to_be_visible()
    for name in ["Security analysis","Remediation","Reports"]:
        page.get_by_role("navigation").get_by_role("link",name=name).click()
        expect(page.locator("main h1")).to_be_visible()
    page.get_by_role("link",name="Developer lab").click()
    page.get_by_role("button",name="ID and session user").click()
    expect(page.get_by_role("status")).to_contain_text("Correct")
    page.reload()
    expect(page.get_by_role("status")).to_contain_text("Correct")
    page.set_viewport_size({"width":390,"height":844})
    for route in ["/","/findings","/compare","/analysis","/reports","/lab","/remediation"]:
        page.goto(url+"/#"+route)
        expect(page.locator("main h1")).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"),route
    page.emulate_media(reduced_motion="reduce")
    page.goto(url+"/#/")
    expect(page.locator(".visualFoot span")).to_have_text("Verified shield")
    page.add_init_script("""const old=HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext=function(kind,...args){return kind==='webgl'?null:old.call(this,kind,...args)}""")
    page.reload()
    expect(page.locator(".fallback")).to_be_visible()
    assert not errors,errors
    browser.close()
    print("PASS: desktop navigation, skip link, particle transition, pause, search, finding, comparison, reports, lab persistence, seven mobile routes, reduced motion, WebGL fallback, no page errors.")
