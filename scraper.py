from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


def scrape_page(url, path="screenshot.png", plot=False, bbox=True, return_str=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 1080})
        page.goto(url)

        dom_elements = []

        navigation_roles = [
            "button", "caption", "cell", "checkbox", "code", "columnheader", 
            "combobox", "gridcell", "heading", "img", "link", "listitem", 
            "math", "menu", "menuitem", "menuitemcheckbox", "menuitemradio",
            "paragraph", "radio", "rowheader", "scrollbar", "search",
            "searchbox", "slider", "spinbutton", "status", "switch", "table",
            "textbox"
        ]

        page.wait_for_load_state("domcontentloaded")
        
        def is_element_foremost(element_handle):
            return page.evaluate("""(element) => {
                const rect = element.getBoundingClientRect();
                const x = rect.left + rect.width / 2;
                const y = rect.top + rect.height / 2;
                const foremostElement = document.elementFromPoint(x, y);
                return element.contains(foremostElement);
            }""", element_handle)
        
        input()

        for role in navigation_roles:
            try:
                locators = page.get_by_role(role).all()
            except:
                continue
            for loc in locators:
                if loc.is_visible() and is_element_foremost(loc.element_handle()):
                    bounding_box = loc.bounding_box()
                    if bounding_box:
                        bounding_box = {
                            "topX": int(bounding_box["x"]),
                            "topY": int(bounding_box["y"]),
                            "bottomX": int(bounding_box["x"] + bounding_box["width"]),
                            "bottomY": int(bounding_box["y"] + bounding_box["height"]),
                        }
                        if role == "img":
                            aria_label = loc.element_handle().get_attribute("aria-label")
                            dom_elements.append({
                                "role": role,
                                "text": aria_label if aria_label else "",
                                "bounding_box": bounding_box,
                            })
                        else:
                            if loc.inner_text():
                                dom_elements.append({
                                    "role": role,
                                    "text": loc.inner_text().replace("\n", " "),
                                    "bounding_box": bounding_box,
                                })
                        

        dom_elements = sorted(dom_elements, key=lambda x: (x["bounding_box"]["topY"], x["bounding_box"]["topX"]))

        # filter out elements which have same bounding box and inner text
        filtered_elements = []
        for i, element in enumerate(dom_elements):
            if i == 0:
                filtered_elements.append(element)
            else:
                if element["bounding_box"] != filtered_elements[-1]["bounding_box"] or element["text"] != filtered_elements[-1]["text"]:
                    filtered_elements.append(element)

        dom_elements = filtered_elements

        page.screenshot(path=path)

        browser.close()

        if plot:
            image = Image.open("screenshot.png")
            draw = ImageDraw.Draw(image)
            for el in dom_elements:
                topX = el["bounding_box"]["topX"]
                topY = el["bounding_box"]["topY"]
                bottomX = el["bounding_box"]["bottomX"]
                bottomY = el["bounding_box"]["bottomY"]
                draw.rectangle([topX, topY, bottomX, bottomY], outline="red")
                draw.text((topX, topY), el["role"], fill="red")
            image.show()

        if return_str:
            web_scrape = ""
            if bbox:
                for i, element in enumerate(dom_elements):
                    bounding_box = [
                        element["bounding_box"]["topX"],
                        element["bounding_box"]["topY"],
                        element["bounding_box"]["bottomX"],
                        element["bounding_box"]["bottomY"],
                    ]
                    web_scrape += f"<{element['role']} id={i} bbox={bounding_box}> {element['text']}</{element['role']}>\n"
            else:
                for i, element in enumerate(dom_elements):
                    web_scrape += f"<{element['role']} id={i}> {element['text']} </{element['role']}>\n"

            return web_scrape
        else:
            return dom_elements
        