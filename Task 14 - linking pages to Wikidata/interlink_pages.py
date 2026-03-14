#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import itertools
import re
from pathlib import Path

import pywikibot
from pywikibot import pagegenerators
from pywikibot.exceptions import NoPageError, IsRedirectPageError

TASK_NUMBER = 14
BOOTSTRAP_TARGET_LANG = "ary"
LOG_FILE = Path("interlink_pages_log.txt")


def log(message: str) -> None:
    text = str(message)
    print(text)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(text + "\n")


def get_namespace_prefix(site: pywikibot.Site, ns_id: int) -> str:
    if ns_id == 0:
        return ""

    try:
        ns_name = site.namespace(ns_id)
        if ns_name:
            return ns_name
    except Exception:
        pass

    try:
        gen = pagegenerators.AllpagesPageGenerator(namespace=ns_id, site=site, total=1)
        first_page = next(gen, None)
        if first_page:
            title = first_page.title()
            if ":" in title:
                return title.split(":", 1)[0]
    except Exception:
        pass

    raise ValueError(f"Could not determine namespace name for namespace {ns_id} on {site.code}wiki")


def build_param_values(parameters: dict) -> dict:
    values = {}
    for name, spec in parameters.items():
        ptype = spec.get("type")

        if ptype == "range":
            start = spec["start"]
            end = spec["end"]
            step = spec.get("step", 1)

            if step == 0:
                raise ValueError(f'Parameter "{name}" has step=0')

            if step > 0:
                values[name] = list(range(start, end + 1, step))
            else:
                values[name] = list(range(start, end - 1, step))

        elif ptype == "list":
            values[name] = list(spec["values"])

        else:
            raise ValueError(f'Unsupported parameter type "{ptype}" for "{name}"')

    return values


def extract_used_parameters(*templates: str) -> list[str]:
    found = []
    seen = set()

    for template in templates:
        for name in re.findall(r"<([A-Za-z0-9_]+)>", template):
            if name not in seen:
                seen.add(name)
                found.append(name)

    return found


def build_combinations_for_templates(source_pattern: str, target_pattern: str, param_values: dict) -> list[dict]:
    used_params = extract_used_parameters(source_pattern, target_pattern)

    if not used_params:
        return [{}]

    missing = [p for p in used_params if p not in param_values]
    if missing:
        raise ValueError(f"Missing parameter definitions for: {', '.join(missing)}")

    return [
        dict(zip(used_params, combo))
        for combo in itertools.product(*(param_values[p] for p in used_params))
    ]


def expand_templates(template: str, params: dict) -> str:
    result = template
    for key, value in params.items():
        result = result.replace(f"<{key}>", str(value))
    return result


def make_title(site: pywikibot.Site, ns_id: int, base_title: str) -> str:
    base_title = base_title.strip()

    if ns_id == 0:
        return base_title

    prefix = get_namespace_prefix(site, ns_id)
    prefix_pattern = re.escape(prefix) + r"\s*:"

    if re.match(prefix_pattern, base_title, flags=re.IGNORECASE):
        return base_title

    return f"{prefix}:{base_title}"


def page_exists(page: pywikibot.Page) -> bool:
    try:
        return page.exists()
    except Exception:
        return False


def get_item_from_page(page: pywikibot.Page):
    try:
        item = pywikibot.ItemPage.fromPage(page)
        item.get(get_redirect=True)
        return item
    except (NoPageError, IsRedirectPageError):
        return None
    except Exception:
        return None


def interlink_pair(
    source_site: pywikibot.Site,
    target_site: pywikibot.Site,
    source_title: str,
    target_title: str,
    summary: str,
) -> None:
    source_page = pywikibot.Page(source_site, source_title)
    target_page = pywikibot.Page(target_site, target_title)

    if not page_exists(source_page):
        log(f"[SKIP] Source page does not exist: {source_page.title()}")
        return

    if not page_exists(target_page):
        log(f"[SKIP] Target page does not exist: {target_page.title()}")
        return

    source_item = get_item_from_page(source_page)
    if source_item is None:
        log(f"[SKIP] Source page has no Wikidata item: {source_page.title()}")
        return

    target_item = get_item_from_page(target_page)

    if target_item is not None:
        if source_item.id == target_item.id:
            log(f"[OK] Already linked: {source_page.title()} <-> {target_page.title()} ({source_item.id})")
        else:
            log(
                f"[CONFLICT] Different Wikidata items: "
                f"{source_page.title()} ({source_item.id}) / {target_page.title()} ({target_item.id})"
            )
        return

    try:
        source_item.setSitelink(target_page, summary=summary)
        log(f"[LINKED] {source_page.title()} <-> {target_page.title()} via {source_item.id}")
    except Exception as e:
        log(f"[ERROR] Failed to link {source_page.title()} <-> {target_page.title()}: {e}")


def load_job_json(target_site: pywikibot.Site, batch_number: str) -> dict:
    mediawiki_ns = get_namespace_prefix(target_site, 8)
    json_title = f"{mediawiki_ns}:عطاشة{TASK_NUMBER}.خدمة{batch_number}.json"
    json_page = pywikibot.Page(target_site, json_title)

    if not json_page.exists():
        raise NoPageError(f"JSON page does not exist: {json_title}")

    return json.loads(json_page.text.strip())


def main() -> None:
    batch_number = input("Batch number: ").strip()
    if not batch_number:
        raise ValueError("Batch number is required")

    bootstrap_site = pywikibot.Site(BOOTSTRAP_TARGET_LANG, "wikipedia")
    job = load_job_json(bootstrap_site, batch_number)

    source_lang = job["source_lang"]
    target_lang = job["target_lang"]
    namespace = int(job.get("namespace", 0))
    save_summary = job.get("save_summary_interlink", "Interlinking page")

    matchings = job.get("matchings") or job.get("category_matchings")
    if not matchings:
        raise ValueError('JSON must contain "matchings" or "category_matchings"')

    parameters = job.get("parameters", {})

    source_site = pywikibot.Site(source_lang, "wikipedia")
    target_site = pywikibot.Site(target_lang, "wikipedia")

    if target_lang != BOOTSTRAP_TARGET_LANG:
        job = load_job_json(target_site, batch_number)
        source_lang = job["source_lang"]
        target_lang = job["target_lang"]
        namespace = int(job.get("namespace", 0))
        save_summary = job.get("save_summary_interlink", "Interlinking page")
        matchings = job.get("matchings") or job.get("category_matchings")
        parameters = job.get("parameters", {})
        source_site = pywikibot.Site(source_lang, "wikipedia")
        target_site = pywikibot.Site(target_lang, "wikipedia")

    param_values = build_param_values(parameters)

    log(f"Loaded job for batch {batch_number}")
    log(f"Source wiki: {source_lang} | Target wiki: {target_lang} | Namespace: {namespace}")
    log("-" * 80)

    for source_pattern, target_pattern in matchings.items():
        combinations = build_combinations_for_templates(source_pattern, target_pattern, param_values)
        log(f"[MATCHING] {source_pattern} -> {target_pattern} | combinations: {len(combinations)}")

        for combo in combinations:
            source_base = expand_templates(source_pattern, combo)
            target_base = expand_templates(target_pattern, combo)

            source_title = make_title(source_site, namespace, source_base)
            target_title = make_title(target_site, namespace, target_base)

            interlink_pair(
                source_site=source_site,
                target_site=target_site,
                source_title=source_title,
                target_title=target_title,
                summary=save_summary,
            )

    log("-" * 80)
    log("Done.")


if __name__ == "__main__":
    main()