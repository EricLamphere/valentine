#!/usr/bin/env python3
"""Build script that generates static Valentine's Day website from YAML config and Markdown."""

import argparse
import json
import os
import textwrap

import markdown
import yaml

FLOATING_DEFAULTS = {
    "symbols": ["\u2764", "\U0001F495", "\u2665", "\u2763"],
    "count": 20,
    "opacity": 0.15,
    "min_duration": 5,
    "max_duration": 15,
    "min_size": 1,
    "max_size": 2.5,
}

DEFAULT_BACKGROUND = "linear-gradient(135deg, #ffe0e6 0%, #ffc2d1 50%, #ffb3c6 100%)"


def build_shared_css(background):
    return textwrap.dedent(f"""\
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            background: {background};
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}
        h1 {{
            color: #c2185b;
            font-size: 2.8rem;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            padding: 0 1rem;
        }}
        .btn-yes {{
            background: linear-gradient(135deg, #e91e63, #c2185b);
            color: white;
            border: none;
            padding: 1.2rem 3rem;
            font-size: 1.6rem;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(233, 30, 99, 0.4);
            transition: transform 0.2s, box-shadow 0.2s;
            max-width: 90vw;
            text-align: center;
            line-height: 1.4;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-yes:hover {{
            transform: scale(1.08);
            box-shadow: 0 6px 20px rgba(233, 30, 99, 0.6);
        }}
        .btn-no {{
            background: #9e9e9e;
            color: white;
            border: none;
            padding: 0.6rem 1.5rem;
            font-size: 0.9rem;
            border-radius: 30px;
            cursor: pointer;
            position: fixed;
            transition: top 0.15s ease-out, left 0.15s ease-out;
            user-select: none;
        }}
        .hearts {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }}
        .heart {{
            position: absolute;
            font-size: 1.5rem;
            opacity: var(--float-opacity, 0.15);
            animation: float-up linear forwards;
        }}
        @keyframes float-up {{
            0% {{ transform: translateY(100vh) rotate(0deg); opacity: var(--float-opacity, 0.15); }}
            50% {{ opacity: calc(var(--float-opacity, 0.15) + 0.1); }}
            100% {{ transform: translateY(-10vh) rotate(360deg); opacity: 0; }}
        }}
        .content {{
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1.5rem;
        }}
    """)


DODGING_JS = textwrap.dedent("""\
    (function() {
        var noBtn = document.getElementById('no-btn');
        var yesBtn = document.querySelector('.btn-yes');
        var PROXIMITY = 100;
        var BOUND = 150;

        // Position the No button just below the YES button (centered)
        var yesRect = yesBtn.getBoundingClientRect();
        var noBtnWidth = noBtn.offsetWidth;
        var noBtnHeight = noBtn.offsetHeight;
        var originX = yesRect.left + yesRect.width / 2 - noBtnWidth / 2;
        var originY = yesRect.bottom + 20;
        noBtn.style.left = originX + 'px';
        noBtn.style.top = originY + 'px';

        var cursorX = -9999;
        var cursorY = -9999;

        function dodge() {
            var rect = noBtn.getBoundingClientRect();
            var btnCX = rect.left + rect.width / 2;
            var btnCY = rect.top + rect.height / 2;

            // Flee directly away from cursor
            var dx = btnCX - cursorX;
            var dy = btnCY - cursorY;
            var dist = Math.sqrt(dx * dx + dy * dy) || 1;
            var angle = Math.atan2(dy, dx);

            // Add slight randomness to the angle so it's not perfectly predictable
            angle += (Math.random() - 0.5) * 0.8;

            // Always jump farther than PROXIMITY so cursor is out of range
            var jumpDist = PROXIMITY + 50 + Math.random() * 50;
            var newX = btnCX + Math.cos(angle) * jumpDist - rect.width / 2;
            var newY = btnCY + Math.sin(angle) * jumpDist - rect.height / 2;

            // Clamp within BOUND px of origin
            newX = Math.max(originX - BOUND, Math.min(originX + BOUND, newX));
            newY = Math.max(originY - BOUND, Math.min(originY + BOUND, newY));

            // Keep on screen
            newX = Math.max(5, Math.min(window.innerWidth - rect.width - 5, newX));
            newY = Math.max(5, Math.min(window.innerHeight - rect.height - 5, newY));

            // Avoid overlapping the YES button
            var yR = yesBtn.getBoundingClientRect();
            var wouldOverlap = (
                newX < yR.right + 10 &&
                newX + rect.width > yR.left - 10 &&
                newY < yR.bottom + 10 &&
                newY + rect.height > yR.top - 10
            );
            if (wouldOverlap) {
                newY = yR.bottom + 20;
            }

            noBtn.style.left = newX + 'px';
            noBtn.style.top = newY + 'px';
        }

        // Dodge on mouse proximity
        document.addEventListener('mousemove', function(e) {
            cursorX = e.clientX;
            cursorY = e.clientY;
            var rect = noBtn.getBoundingClientRect();
            var dx = cursorX - (rect.left + rect.width / 2);
            var dy = cursorY - (rect.top + rect.height / 2);
            if (Math.sqrt(dx * dx + dy * dy) < PROXIMITY) {
                dodge();
            }
        });

        // Dodge on touch proximity
        document.addEventListener('touchmove', function(e) {
            var touch = e.touches[0];
            cursorX = touch.clientX;
            cursorY = touch.clientY;
            var rect = noBtn.getBoundingClientRect();
            var dx = cursorX - (rect.left + rect.width / 2);
            var dy = cursorY - (rect.top + rect.height / 2);
            if (Math.sqrt(dx * dx + dy * dy) < PROXIMITY) {
                dodge();
            }
        });

        // Dodge on click / tap
        noBtn.addEventListener('click', function(e) {
            e.preventDefault();
            dodge();
        });
        noBtn.addEventListener('touchstart', function(e) {
            e.preventDefault();
            dodge();
        });
    })();
""")


def build_floating_js(floating_config):
    """Generate JS that spawns floating symbols one at a time from the bottom."""
    cfg = dict(FLOATING_DEFAULTS)
    cfg.update(floating_config or {})
    symbols_json = json.dumps(cfg["symbols"])
    duration_range = cfg["max_duration"] - cfg["min_duration"]
    size_range = cfg["max_size"] - cfg["min_size"]
    # Spawn interval: spread spawns over the max_duration so the screen
    # fills up gradually over one full animation cycle.
    spawn_interval_ms = int(cfg["max_duration"] / cfg["count"] * 1000)
    return textwrap.dedent(f"""\
        (function() {{
            var container = document.querySelector('.hearts');
            var symbols = {symbols_json};
            var count = {cfg["count"]};
            var spawned = 0;

            function spawnHeart() {{
                if (spawned >= count) return;
                var el = document.createElement('div');
                el.className = 'heart';
                el.textContent = symbols[spawned % symbols.length];
                el.style.left = Math.random() * 100 + '%';
                var dur = {cfg["min_duration"]} + Math.random() * {duration_range};
                el.style.animationDuration = dur + 's';
                el.style.fontSize = ({cfg["min_size"]} + Math.random() * {size_range}) + 'rem';
                el.style.animationIterationCount = 'infinite';
                container.appendChild(el);
                spawned++;
            }}

            setInterval(spawnHeart, {spawn_interval_ms});
        }})();
    """)


def build_button_page(title, yes_text, no_text, yes_href, shared_css, floating_js, opacity):
    """Generate HTML for a page with YES/NO buttons."""
    html = textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            :root {{ --float-opacity: {opacity}; }}
    {textwrap.indent(shared_css, "        ")}
        </style>
    </head>
    <body>
        <div class="hearts"></div>
        <div class="content">
            <h1>{title}</h1>
            <a class="btn-yes" href="{yes_href}">{yes_text}</a>
            <button class="btn-no" id="no-btn">{no_text}</button>
        </div>
        <script>
    {textwrap.indent(floating_js, "        ")}
    {textwrap.indent(DODGING_JS, "        ")}
        </script>
    </body>
    </html>
    """)
    return html


def build_agenda_page(agenda_html, shared_css, floating_js, opacity):
    """Generate HTML for the agenda page with rendered markdown."""
    agenda_css = textwrap.dedent("""\
        body {
            overflow: auto;
            justify-content: flex-start;
            padding: 2rem 1rem;
        }
        .agenda {
            background: rgba(255, 255, 255, 0.85);
            border-radius: 20px;
            padding: 2.5rem;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 8px 30px rgba(194, 24, 91, 0.15);
            position: relative;
            z-index: 1;
        }
        .agenda h1 {
            font-size: 2.2rem;
            margin-bottom: 1rem;
        }
        .agenda h2 {
            color: #e91e63;
            font-size: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .agenda ul {
            list-style: none;
            padding-left: 0;
        }
        .agenda li {
            padding: 0.4rem 0;
            font-size: 1.1rem;
            color: #555;
        }
        .agenda li::before {
            content: '\\2764\\FE0F ';
        }
        .agenda p {
            color: #555;
            font-size: 1.1rem;
            line-height: 1.6;
        }
    """)

    html = textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Our Valentine's Day</title>
        <style>
            :root {{ --float-opacity: {opacity}; }}
    {textwrap.indent(shared_css, "        ")}
    {textwrap.indent(agenda_css, "        ")}
        </style>
    </head>
    <body>
        <div class="hearts"></div>
        <div class="agenda">
            {agenda_html}
        </div>
        <script>
    {textwrap.indent(floating_js, "        ")}
        </script>
    </body>
    </html>
    """)
    return html


def page_filename(index):
    """Return the filename for a button page by its index (0-based)."""
    if index == 0:
        return "index.html"
    return f"page-{index + 1}.html"


def main():
    parser = argparse.ArgumentParser(description="Build Valentine's Day static site")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    config_dir = os.path.dirname(os.path.abspath(args.config))
    agenda_path = os.path.join(config_dir, config["agenda_file"])

    with open(agenda_path, "r") as f:
        agenda_md = f.read()

    agenda_html = markdown.markdown(agenda_md)

    background = config.get("background", DEFAULT_BACKGROUND)
    shared_css = build_shared_css(background)

    floating_config = config.get("floating", {})
    floating_js = build_floating_js(floating_config)
    cfg = dict(FLOATING_DEFAULTS)
    cfg.update(floating_config or {})
    opacity = cfg["opacity"]

    out_dir = os.path.join(config_dir, "_site")
    os.makedirs(out_dir, exist_ok=True)

    pages = config["pages"]
    built_files = []

    for i, page in enumerate(pages):
        is_last = i == len(pages) - 1
        yes_href = "agenda.html" if is_last else page_filename(i + 1)
        filename = page_filename(i)

        html = build_button_page(
            title=page["title"],
            yes_text=page["yes_button"],
            no_text=page["no_button"],
            yes_href=yes_href,
            shared_css=shared_css,
            floating_js=floating_js,
            opacity=opacity,
        )
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w") as f:
            f.write(html)
        built_files.append(filename)

    agenda_page = build_agenda_page(agenda_html, shared_css, floating_js, opacity)
    filepath = os.path.join(out_dir, "agenda.html")
    with open(filepath, "w") as f:
        f.write(agenda_page)
    built_files.append("agenda.html")

    print(f"Built {len(built_files)} pages in {out_dir}/")
    for name in built_files:
        path = os.path.join(out_dir, name)
        print(f"  {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
