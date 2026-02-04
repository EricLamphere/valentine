#!/usr/bin/env python3
"""Build script that generates static Valentine's Day website from YAML config and Markdown."""

import argparse
import json
import os

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

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

    floating_config = config.get("floating", {})
    cfg = dict(FLOATING_DEFAULTS)
    cfg.update(floating_config or {})
    opacity = cfg["opacity"]
    duration_range = cfg["max_duration"] - cfg["min_duration"]
    size_range = cfg["max_size"] - cfg["min_size"]
    spawn_interval_ms = int(cfg["max_duration"] / cfg["count"] * 1000)

    # Jinja2 environment
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))

    # Shared template variables
    shared_vars = {
        "background": background,
        "opacity": opacity,
        "symbols_json": json.dumps(cfg["symbols"]),
        "count": cfg["count"],
        "min_duration": cfg["min_duration"],
        "duration_range": duration_range,
        "min_size": cfg["min_size"],
        "size_range": size_range,
        "spawn_interval_ms": spawn_interval_ms,
    }

    out_dir = os.path.join(config_dir, "_site")
    os.makedirs(out_dir, exist_ok=True)

    pages = config["pages"]
    built_files = []

    button_template = env.get_template("button_page.html")
    for i, page in enumerate(pages):
        is_last = i == len(pages) - 1
        yes_href = "fireworks.html" if is_last else page_filename(i + 1)
        filename = page_filename(i)

        html = button_template.render(
            **shared_vars,
            title=page["title"],
            yes_text=page["yes_button"],
            no_text=page["no_button"],
            yes_href=yes_href,
        )
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w") as f:
            f.write(html)
        built_files.append(filename)

    fireworks_config = config.get("fireworks", {})
    fireworks_title = fireworks_config.get("title", "Yay!")
    fireworks_duration = fireworks_config.get("duration_seconds", 5)
    fireworks_button_text = fireworks_config.get("button_text", "Here's the plan...")

    fireworks_template = env.get_template("fireworks_page.html")
    html = fireworks_template.render(
        **shared_vars,
        title=fireworks_title,
        next_href="agenda.html",
        delay_ms=int(fireworks_duration * 1000),
        button_text=fireworks_button_text,
    )
    filepath = os.path.join(out_dir, "fireworks.html")
    with open(filepath, "w") as f:
        f.write(html)
    built_files.append("fireworks.html")

    agenda_template = env.get_template("agenda_page.html")
    html = agenda_template.render(
        **shared_vars,
        title="Our Valentine's Day",
        agenda_html=agenda_html,
    )
    filepath = os.path.join(out_dir, "agenda.html")
    with open(filepath, "w") as f:
        f.write(html)
    built_files.append("agenda.html")

    print(f"Built {len(built_files)} pages in {out_dir}/")
    for name in built_files:
        path = os.path.join(out_dir, name)
        print(f"  {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
