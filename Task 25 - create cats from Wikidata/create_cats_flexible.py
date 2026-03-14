#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import time
import traceback
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple, Set

import pywikibot


CONFIG_PAGE_PATTERN = "ميدياويكي:عطاشة25.2.خدمة{number}.json"

DEFAULT_SCAN_MEMBERS_LIMIT = 300
DEFAULT_ADD_TO_TARGET_PAGES_LIMIT = 0  # 0 = no limit
DEFAULT_SPARQL_LIMIT = 5000

DEFAULT_SAVE_SUMMARY_CREATE = "Create missing category from source wiki (bot)"
DEFAULT_SAVE_SUMMARY_ADD_CAT = "Add missing category (bot)"
DEFAULT_SAVE_SUMMARY_INTERLINK = "Setting sitelink (bot)"
DEFAULT_THROTTLE_SLEEP = 0.0

PLACEHOLDER_RE = re.compile(r"<([a-zA-Z0-9_]+)>")

# Fail fast: no exponential backoff sleeps on API errors/maxlag
pywikibot.config.max_retries = 0
pywikibot.config.retry_wait = 0

# Optional: if the sleeps are maxlag-related, disable sending maxlag altogether.
# (This removes the polite "defer edits when DB lagged" behavior.)
pywikibot.config.maxlag = None

# Optional: if the sleeps are between edits (write throttle), lower it.
# Use carefully on public wikis.
# pywikibot.config.put_throttle = 0



# ---------------------------
# Config types
# ---------------------------

@dataclass(frozen=True)
class RangeParam:
    start: int
    end: int
    step: int

@dataclass(frozen=True)
class ListParam:
    values: Dict[str, str]  # source_token -> target_token

@dataclass(frozen=True)
class QidParam:
    qid: str

ParamSpec = Any

@dataclass
class Rule:
    src_pat: str
    tgt_pat: str
    placeholders: List[str]

@dataclass
class Config:
    source_lang: str
    target_lang: str
    category_matchings: Dict[str, str]
    parameters: Dict[str, ParamSpec]

    target_stub_template: Optional[str]
    target_stub_template_param: Optional[str]

    scan_members_limit: int
    add_to_target_pages_limit: int
    sparql_limit: int

    save_summary_create: str
    save_summary_add_cat: str
    save_summary_interlink: str

    throttle_sleep: float


def _norm_qid(q: str) -> str:
    q = str(q).strip()
    if not q.upper().startswith("Q"):
        q = "Q" + q
    return q.upper()


def load_config_from_wiki(target_site: pywikibot.Site, number: int) -> Config:
    title = CONFIG_PAGE_PATTERN.format(number=number)
    page = pywikibot.Page(target_site, title)
    if not page.exists():
        raise ValueError(f"Config page does not exist: {title}")

    raw = json.loads(page.text)

    source_lang = raw["source_lang"].strip()
    target_lang = raw["target_lang"].strip()
    category_matchings = raw["category_matchings"]
    parameters_raw = raw.get("parameters", {})

    parameters: Dict[str, ParamSpec] = {}
    for pname, pspec in parameters_raw.items():
        print(pname)
        print(pspec)
        ptype = pspec.get("type")
        if ptype == "range":
            parameters[pname] = RangeParam(
                start=int(pspec["start"]),
                end=int(pspec["end"]),
                step=int(pspec["step"]),
            )
        elif ptype == "list":
            values = pspec.get("values", {})
            parameters[pname] = ListParam(values={str(k): str(v) for k, v in values.items()})
        elif ptype == "qid":
            parameters[pname] = QidParam(qid=_norm_qid(pspec["value"]))
        else:
            raise ValueError(f'Unsupported parameter type for "{pname}": {ptype}')

    return Config(
        source_lang=source_lang,
        target_lang=target_lang,
        category_matchings=category_matchings,
        parameters=parameters,

        target_stub_template=raw.get("target_category_stub_template"),
        target_stub_template_param=str(raw.get("target_category_stub_template_param", "1")),

        scan_members_limit=int(raw.get("scan_members_limit", DEFAULT_SCAN_MEMBERS_LIMIT)),
        add_to_target_pages_limit=int(raw.get("add_to_target_pages_limit", DEFAULT_ADD_TO_TARGET_PAGES_LIMIT)),
        sparql_limit=int(raw.get("sparql_limit", DEFAULT_SPARQL_LIMIT)),

        save_summary_create=str(raw.get("save_summary_create", DEFAULT_SAVE_SUMMARY_CREATE)),
        save_summary_add_cat=str(raw.get("save_summary_add_cat", DEFAULT_SAVE_SUMMARY_ADD_CAT)),
        save_summary_interlink=str(raw.get("save_summary_interlink", DEFAULT_SAVE_SUMMARY_INTERLINK)),

        throttle_sleep=float(raw.get("throttle_sleep", DEFAULT_THROTTLE_SLEEP)),
    )


# ---------------------------
# Namespace/title sanitization (FIXED)
# ---------------------------

def strip_leading_colons(title: str) -> str:
    t = (title or "").strip()
    while t.startswith(":"):
        t = t[1:].lstrip()
    return t


def ns_aliases(site: pywikibot.Site, ns: int) -> List[str]:
    out: List[str] = []
    try:
        ns_obj = site.namespaces[ns]
        try:
            out.append(str(ns_obj))
        except Exception:
            pass
        try:
            for a in ns_obj:
                out.append(str(a))
        except Exception:
            pass
    except Exception:
        return []
    out = [x for x in out if x]
    seen = set()
    uniq: List[str] = []
    for x in out:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    return uniq


def collapse_double_colon_anywhere(title: str) -> str:
    # collapse only the first occurrence of '::' repeatedly until none
    t = (title or "").strip()
    while "::" in t:
        t = t.replace("::", ":", 1)
    return t


def collapse_double_colon_after_any_namespace(site: pywikibot.Site, title: str) -> str:
    """
    If title starts with '<ns>:' followed immediately by ':' -> collapse to single ':'.
    Works for ALL namespaces/aliases known by the site.
    """
    t = (title or "").strip()
    if not t:
        return t

    # Fast path: if no '::' at all, nothing to do
    if "::" not in t:
        return t

    # Try all namespace ids we care about first
    for ns in (14, 6, 10, 828):
        for a in ns_aliases(site, ns):
            if t.startswith(a + "::"):
                return a + ":" + t[len(a) + 2 :]

    # Generic: if it looks like 'Something::Title' collapse once
    m = re.match(r"^([^:]+)::(.*)$", t)
    if m:
        return m.group(1) + ":" + m.group(2)

    return t


def sanitize_title_for_site(site: pywikibot.Site, title: str) -> str:
    """
    Absolute last line of defense: make sure we never pass invalid 'ns::Title'
    or leading ':' into pywikibot.Page().
    """
    t = (title or "").strip()
    if not t:
        return t

    if t.startswith("[[") and t.endswith("]]"):
        t = t[2:-2].strip()

    t = strip_leading_colons(t)
    t = collapse_double_colon_after_any_namespace(site, t)
    t = strip_leading_colons(t)
    # if still contains '::' (rare weirdness), collapse generically
    t = collapse_double_colon_anywhere(t)
    t = strip_leading_colons(t)
    return t


def title_has_ns_prefix(site: pywikibot.Site, ns: int, title: str) -> bool:
    t = (title or "").strip()
    for a in ns_aliases(site, ns):
        if a and t.startswith(a + ":"):
            return True
    return False


def ns_primary_prefix(site: pywikibot.Site, ns: int) -> Optional[str]:
    try:
        ns_obj = site.namespaces[ns]
        name = str(ns_obj)
        if name:
            return name + ":"
    except Exception:
        pass
    return None


def force_namespace_on_title(target_site: pywikibot.Site, ns: int, title: str) -> str:
    """
    Ensure correct namespace prefix based on SOURCE page namespace.
    Then sanitize.
    """
    t = sanitize_title_for_site(target_site, title)
    if not t:
        return t

    if title_has_ns_prefix(target_site, ns, t):
        return sanitize_title_for_site(target_site, t)

    if ns in (6, 10, 14, 828):
        pref = ns_primary_prefix(target_site, ns)
        if pref:
            t = pref + t
    return sanitize_title_for_site(target_site, t)


def normalize_no_ns_title(site: pywikibot.Site, title: str) -> str:
    t = sanitize_title_for_site(site, title)
    if not t:
        return t

    cat_ns = site.namespaces.CATEGORY
    ns_names = set()
    try:
        ns_names.add(str(cat_ns))
    except Exception:
        pass
    try:
        for a in cat_ns:
            ns_names.add(str(a))
    except Exception:
        pass

    for ns in sorted(ns_names, key=len, reverse=True):
        ns_prefix = ns + ":"
        if t.startswith(ns_prefix):
            t = t[len(ns_prefix):].lstrip()
            break

    t = sanitize_title_for_site(site, t)
    return t


def cat_obj(site: pywikibot.Site, title_any: str) -> pywikibot.Category:
    return pywikibot.Category(site, normalize_no_ns_title(site, title_any))


def _clean_sitelink_title(sl) -> Optional[str]:
    if sl is None:
        return None

    t = None
    for attr in ("title", "canonical_title", "text"):
        try:
            v = getattr(sl, attr)
            if callable(v):
                v = v()
            if isinstance(v, str) and v.strip():
                t = v.strip()
                break
        except Exception:
            continue

    if t is None:
        t = str(sl).strip()

    return t if t else None


# ---------------------------
# Pattern engine
# ---------------------------

def extract_placeholders(s: str) -> List[str]:
    return [m.group(1) for m in PLACEHOLDER_RE.finditer(s)]


def build_rules(cfg: Config) -> List[Rule]:
    rules: List[Rule] = []
    for sp, tp in cfg.category_matchings.items():
        ph = sorted(set(extract_placeholders(sp) + extract_placeholders(tp)))
        rules.append(Rule(src_pat=sp, tgt_pat=tp, placeholders=ph))
    return rules


def render(pattern: str, values: Dict[str, str]) -> str:
    out = pattern
    for k, v in values.items():
        out = out.replace(f"<{k}>", v)
    return out


def iter_range(spec: RangeParam) -> Iterable[str]:
    if spec.step == 0:
        return
    x = spec.start
    if spec.step > 0:
        while x <= spec.end:
            yield str(x)
            x += spec.step
    else:
        while x >= spec.end:
            yield str(x)
            x += spec.step


def __product(*lists):
    if not lists:
        yield ()
        return
    res = [()]
    for lst in lists:
        res = [r + (x,) for r in res for x in lst]
    for r in res:
        yield r


def is_int_in_range(val: str, spec: RangeParam) -> bool:
    try:
        n = int(val)
    except Exception:
        return False
    if spec.step == 0:
        return False
    if spec.step > 0:
        if n < spec.start or n > spec.end:
            return False
    else:
        if n > spec.start or n < spec.end:
            return False
    if (n - spec.start) % spec.step != 0:
        return False
    return True


def validate_non_qid(values: Dict[str, str], cfg: Config) -> bool:
    for k, v in values.items():
        spec = cfg.parameters.get(k)
        if isinstance(spec, RangeParam):
            if not is_int_in_range(v, spec):
                return False
        elif isinstance(spec, ListParam):
            if v not in spec.values:
                return False
    return True


def map_values_to_target(values_src: Dict[str, str], cfg: Config) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in values_src.items():
        spec = cfg.parameters.get(k)
        if isinstance(spec, ListParam):
            out[k] = spec.values.get(v, v)
        else:
            out[k] = v
    return out


# ---------------------------
# Wikidata helpers
# ---------------------------

def item_of_page_safe(p: pywikibot.Page) -> Optional[pywikibot.ItemPage]:
    try:
        it = p.data_item()
        it.get()
        return it
    except Exception:
        return None


def get_target_page_from_source(
    source_page: pywikibot.Page,
    target_site: pywikibot.Site,
    target_lang: str,
    verbose: bool = False,
) -> Optional[pywikibot.Page]:
    it = item_of_page_safe(source_page)
    if not it:
        return None

    sl = it.sitelinks.get(f"{target_lang}wiki")
    raw = _clean_sitelink_title(sl)
    if not raw:
        return None

    raw = sanitize_title_for_site(target_site, raw)
    fixed = force_namespace_on_title(target_site, source_page.namespace(), raw)

    if verbose and ("::" in raw or "::" in fixed or raw.startswith(":") or fixed.startswith(":")):
        pywikibot.output(f"[DEBUG-SITELINK] src={source_page.title()} ns={source_page.namespace()} raw={repr(raw)} fixed={repr(fixed)}")

    try:
        return pywikibot.Page(target_site, fixed)
    except Exception:
        return None


def get_target_category_from_source_category(source_cat: pywikibot.Category, target_site: pywikibot.Site, target_lang: str) -> Optional[pywikibot.Category]:
    it = item_of_page_safe(source_cat)
    if not it:
        return None
    sl = it.sitelinks.get(f"{target_lang}wiki")
    raw = _clean_sitelink_title(sl)
    if not raw:
        return None
    raw = sanitize_title_for_site(target_site, raw)
    fixed = force_namespace_on_title(target_site, 14, raw)
    try:
        return cat_obj(target_site, fixed)
    except Exception:
        return None


def item_is_instance_of(it: pywikibot.ItemPage, qid: str) -> bool:
    qid = _norm_qid(qid)
    try:
        claims = it.claims.get("P31", [])
        for c in claims:
            t = c.getTarget()
            if hasattr(t, "title") and t.title() == qid:
                return True
    except Exception:
        return False
    return False


# ---------------------------
# Interlinking
# ---------------------------

import time
import traceback
import pywikibot


import traceback
import pywikibot


def interlink_categories(
    cfg,
    source_site: pywikibot.Site,
    target_site: pywikibot.Site,
    src_cat_no_ns: str,
    tgt_cat_no_ns: str,
    verbose: bool,
) -> bool:
    src_cat = cat_obj(source_site, src_cat_no_ns)
    tgt_cat = cat_obj(target_site, tgt_cat_no_ns)

    try:
        if not src_cat.exists() or not tgt_cat.exists():
            if verbose:
                pywikibot.output("[LINK] cannot link: missing src/tgt category page")
            return False
    except Exception:
        if verbose:
            pywikibot.output("[LINK-ERR]\n" + traceback.format_exc())
        return False

    src_code = f"{source_site.code}wiki"
    tgt_code = f"{target_site.code}wiki"

    # Category-only: we ALWAYS want sitelinks that include the category namespace.
    src_with_ns = src_cat.title(with_ns=True)
    src_no_ns = src_cat.title(with_ns=False)
    tgt_with_ns = tgt_cat.title(with_ns=True)
    tgt_no_ns = tgt_cat.title(with_ns=False)

    repo = source_site.data_repository()
    if repo is None:
        if verbose:
            pywikibot.output("[LINK] cannot link: no data_repository for source site")
        return False

    try:
        repo.login()
    except Exception:
        if verbose:
            pywikibot.output("[LINK-ERR] repo.login() failed\n" + traceback.format_exc())
        return False

    old_max_retries = getattr(pywikibot.config, "max_retries", 3)
    old_retry_wait = getattr(pywikibot.config, "retry_wait", 5)
    pywikibot.config.max_retries = 0
    pywikibot.config.retry_wait = 0

    def _restore_config():
        pywikibot.config.max_retries = old_max_retries
        pywikibot.config.retry_wait = old_retry_wait

    def _ensure_category_sitelink(
        item: pywikibot.ItemPage,
        sitecode: str,
        expected_with_ns: str,
        expected_no_ns: str,
    ) -> bool:
        item.get()

        if sitecode in item.sitelinks:
            existing = item.sitelinks[sitecode].title

            # Category-only rule:
            # If it matches the category title WITHOUT namespace, normalize to WITH namespace.
            if existing == expected_no_ns and expected_with_ns != expected_no_ns:
                item.setSitelink(
                    sitelink={"site": sitecode, "title": expected_with_ns},
                    summary=cfg.save_summary_interlink,
                )
                return True

            # If it already matches the correct category title WITH namespace, OK.
            if existing == expected_with_ns:
                return True

            # Anything else is a true conflict (wrong page linked).
            return False

        # Not present: add it (with namespace).
        item.setSitelink(
            sitelink={"site": sitecode, "title": expected_with_ns},
            summary=cfg.save_summary_interlink,
        )
        return True

    try:
        # Resolve item from the source category page
        try:
            item = pywikibot.ItemPage.fromPage(src_cat)
            item.get()
        except (pywikibot.exceptions.NoPageError, pywikibot.exceptions.InvalidTitleError):
            item = None

        if item is None or not item.exists():
            # Create a new item with BOTH category sitelinks (with namespace)
            new_item = pywikibot.ItemPage(repo)
            data = {
                "sitelinks": {
                    src_code: {"site": src_code, "title": src_with_ns},
                    tgt_code: {"site": tgt_code, "title": tgt_with_ns},
                }
            }
            new_item.editEntity(data, summary=cfg.save_summary_interlink)
            if verbose:
                pywikibot.output("[LINK] OK (created new item with both sitelinks)")
            return True

        # Ensure source sitelink is the category (normalize if missing ns)
        ok_src = _ensure_category_sitelink(item, src_code, src_with_ns, src_no_ns)
        if not ok_src:
            if verbose:
                existing_src = item.sitelinks[src_code].title if src_code in item.sitelinks else "<missing>"
                pywikibot.output(
                    f"[LINK] conflict: item already links {src_code} -> {existing_src} "
                    f"(expected {src_with_ns})"
                )
            return False

        # Ensure target sitelink is the category (normalize if missing ns)
        ok_tgt = _ensure_category_sitelink(item, tgt_code, tgt_with_ns, tgt_no_ns)
        if not ok_tgt:
            if verbose:
                existing_tgt = item.sitelinks[tgt_code].title if tgt_code in item.sitelinks else "<missing>"
                pywikibot.output(
                    f"[LINK] conflict: item already links {tgt_code} -> {existing_tgt} "
                    f"(expected {tgt_with_ns})"
                )
            return False

        if verbose:
            pywikibot.output("[LINK] OK (updated/normalized existing item)")
        return True

    except pywikibot.data.api.APIError as e:
        if verbose:
            pywikibot.output(f"[LINK] APIError (fail-fast): {e}")
        return False
    except (
        pywikibot.exceptions.MaxlagTimeoutError,
        pywikibot.exceptions.TimeoutError,
        pywikibot.exceptions.ServerError,
        pywikibot.exceptions.OtherPageSaveError,
        pywikibot.exceptions.PageSaveRelatedError,
    ) as e:
        if verbose:
            pywikibot.output(f"[LINK] save/timeout error (fail-fast): {e}")
        return False
    except Exception:
        if verbose:
            pywikibot.output("[LINK-ERR]\n" + traceback.format_exc())
        return False
    finally:
        _restore_config()

def resolve_redirect_target_page_safe(p: pywikibot.Page, max_hops: int = 5) -> pywikibot.Page:
    """
    Follow redirects (up to max_hops) and return the final target page.
    If anything fails, return the original page.
    """
    cur = p
    try:
        for _ in range(max_hops):
            try:
                if not cur.exists():
                    return cur
            except Exception:
                return cur

            try:
                if not cur.isRedirectPage():
                    return cur
            except Exception:
                return cur

            try:
                nxt = cur.getRedirectTarget()
            except Exception:
                return cur

            if not isinstance(nxt, pywikibot.Page):
                return cur

            cur = nxt
    except Exception:
        return p
    return cur

# ---------------------------
# Rule matching + candidate generation
# ---------------------------

def try_parse_rule_match_from_title(
    cfg: Config,
    rule: Rule,
    source_site: pywikibot.Site,
    target_site: pywikibot.Site,
    source_cat_title_no_ns: str,
) -> Optional[Tuple[Dict[str, str], Dict[str, str]]]:
    rx = re.escape(rule.src_pat)
    qid_placeholders: List[str] = []

    for ph in extract_placeholders(rule.src_pat):
        spec = cfg.parameters.get(ph)
        if isinstance(spec, RangeParam):
            rx = rx.replace(re.escape(f"<{ph}>"), rf"(?P<{ph}>\d+)")
        elif isinstance(spec, ListParam):
            alts = "|".join(re.escape(k) for k in spec.values.keys())
            rx = rx.replace(re.escape(f"<{ph}>"), rf"(?P<{ph}>{alts})")
        elif isinstance(spec, QidParam):
            qid_placeholders.append(ph)
            rx = rx.replace(re.escape(f"<{ph}>"), rf"(?P<{ph}>.+)")
        else:
            rx = rx.replace(re.escape(f"<{ph}>"), rf"(?P<{ph}>.+)")

    m = re.fullmatch(rx, source_cat_title_no_ns)
    if not m:
        return None

    src_vals = {k: v for k, v in m.groupdict().items()}

    if not validate_non_qid(src_vals, cfg):
        return None

    tgt_vals = map_values_to_target(src_vals, cfg)

    for qph in qid_placeholders:
        spec = cfg.parameters.get(qph)
        if not isinstance(spec, QidParam):
            return None

        src_topic_title = src_vals[qph]
        src_topic_title = sanitize_title_for_site(source_site, src_topic_title)
        src_topic_page = pywikibot.Page(source_site, src_topic_title)

        try:
            if not src_topic_page.exists():
                return None
        except Exception:
            return None

        # IMPORTANT FIX: follow redirects before checking Wikidata/Qid
        src_topic_page = resolve_redirect_target_page_safe(src_topic_page)

        try:
            if not src_topic_page.exists():
                return None
        except Exception:
            return None

        it = item_of_page_safe(src_topic_page)
        if not it:
            return None

        if not item_is_instance_of(it, spec.qid):
            return None

        sl = it.sitelinks.get(f"{cfg.target_lang}wiki")
        ttitle = _clean_sitelink_title(sl)
        if not ttitle:
            return None

        tgt_vals[qph] = sanitize_title_for_site(target_site, ttitle)

    return src_vals, tgt_vals


def split_pattern_on_qid(src_pat: str, placeholders: List[str], cfg: Config) -> Tuple[Optional[str], Optional[str]]:
    qid_ph = None
    for ph in placeholders:
        if isinstance(cfg.parameters.get(ph), QidParam):
            qid_ph = ph
            break
    if not qid_ph:
        return None, None
    token = f"<{qid_ph}>"
    if src_pat.count(token) != 1:
        return None, None
    before, _ = src_pat.split(token)
    return qid_ph, before


def iter_small_param_assignments_for_prefix(prefix_template: str, cfg: Config) -> Iterable[Dict[str, str]]:
    phs = extract_placeholders(prefix_template)
    domains: List[Tuple[str, List[str]]] = []
    for ph in phs:
        spec = cfg.parameters.get(ph)
        if isinstance(spec, RangeParam):
            domains.append((ph, list(iter_range(spec))))
        elif isinstance(spec, ListParam):
            domains.append((ph, list(spec.values.keys())))
        else:
            domains.append((ph, []))

    if any(len(vals) == 0 for _, vals in domains):
        return

    keys = [k for k, _ in domains]
    lists = [vals for _, vals in domains]
    for combo in __product(*lists):
        yield dict(zip(keys, combo))


def iter_source_categories_for_rule(cfg: Config, rule: Rule, source_site: pywikibot.Site, verbose: bool) -> Iterable[str]:
    qid_ph, prefix_template = split_pattern_on_qid(rule.src_pat, rule.placeholders, cfg)

    if qid_ph and prefix_template is not None:
        for pre_vals in iter_small_param_assignments_for_prefix(prefix_template, cfg):
            prefix = render(prefix_template, pre_vals)
            if verbose:
                pywikibot.output(f"[PREFIX] {source_site.code}wiki Category apprefix={prefix!r}")
            for p in source_site.allpages(prefix=prefix, namespace=14):
                yield p.title(with_ns=False)
        return

    phs = extract_placeholders(rule.src_pat)
    domains: List[Tuple[str, List[str]]] = []
    for ph in phs:
        spec = cfg.parameters.get(ph)
        if isinstance(spec, RangeParam):
            domains.append((ph, list(iter_range(spec))))
        elif isinstance(spec, ListParam):
            domains.append((ph, list(spec.values.keys())))
        else:
            domains.append((ph, []))

    if any(len(vals) == 0 for _, vals in domains):
        return

    keys = [k for k, _ in domains]
    lists = [vals for _, vals in domains]
    for combo in __product(*lists):
        vals = dict(zip(keys, combo))
        yield render(rule.src_pat, vals)


# ---------------------------
# Category creation / supercats / member tagging
# ---------------------------

def should_add_category_to_namespace(ns: int) -> bool:
    if ns < 0:
        return False
    if ns % 2 == 1:
        return False
    if ns == 8:
        return False
    return True


def build_target_category_text(cfg: Config, target_cat_no_ns: str, supercats: List[str]) -> str:
    parts: List[str] = []
    if cfg.target_stub_template:
        if cfg.target_stub_template_param:
            parts.append(f"{{{{{cfg.target_stub_template}|{cfg.target_stub_template_param}={target_cat_no_ns}}}}}")
        else:
            parts.append(f"{{{{{cfg.target_stub_template}|{target_cat_no_ns}}}}}")
    parts.extend(supercats)
    txt = "\n".join([p for p in parts if p.strip()])
    return txt.strip() + ("\n" if txt.strip() else "")


def add_missing_supercats_to_existing_catpage(
    target_cat: pywikibot.Category,
    supercat_links: List[str],
    summary: str,
    dry_run: bool,
    verbose: bool,
) -> bool:
    try:
        text = target_cat.get()
    except Exception:
        return False

    additions = [link for link in supercat_links if link not in text]
    if not additions:
        return False

    new_text = text.rstrip() + "\n" + "\n".join(additions) + "\n"

    if verbose:
        pywikibot.output(f"[SUPERCAT-UPDATE] {target_cat.title(with_ns=True)} +{len(additions)}")

    if not dry_run:
        target_cat.text = new_text
        target_cat.save(summary=summary)

    return True


def compute_target_supercats(
    cfg: Config,
    rules: List[Rule],
    source_site: pywikibot.Site,
    target_site: pywikibot.Site,
    source_cat: pywikibot.Category,
    verbose: bool,
) -> List[Tuple[pywikibot.Category, str]]:
    out: List[Tuple[pywikibot.Category, str]] = []
    seen: Set[str] = set()

    for sc in source_cat.categories():
        candidates: List[pywikibot.Category] = []

        src_sc_no_ns = normalize_no_ns_title(source_site, sc.title(with_ns=False))

        mapped_tgt_no_ns = None
        for r in rules:
            parsed = try_parse_rule_match_from_title(cfg, r, source_site, target_site, src_sc_no_ns)
            if not parsed:
                continue
            _, tgt_vals = parsed
            mapped_tgt_no_ns = normalize_no_ns_title(target_site, render(r.tgt_pat, tgt_vals))
            break
        if mapped_tgt_no_ns:
            candidates.append(cat_obj(target_site, mapped_tgt_no_ns))

        wd_mapped = get_target_category_from_source_category(sc, target_site, cfg.target_lang)
        if wd_mapped is not None:
            candidates.append(wd_mapped)

        for tgt_sc in candidates:
            t = tgt_sc.title(with_ns=True)
            if t in seen:
                continue
            seen.add(t)
            out.append((tgt_sc, f"[[{t}]]"))
            if verbose:
                pywikibot.output(f"[SUPERCAT-CAND] {sc.title(with_ns=True)} -> {t}")

    return out


def has_any_linked_member_quick(cfg: Config, source_cat: pywikibot.Category, target_site: pywikibot.Site, verbose: bool) -> bool:
    n = 0
    for sp in source_cat.members(recurse=False, total=cfg.scan_members_limit):
        n += 1
        if get_target_page_from_source(sp, target_site, cfg.target_lang, verbose=verbose) is not None:
            return True
        if n >= cfg.scan_members_limit:
            break
    return False


def ensure_target_category_recursive(
    cfg: Config,
    rules: List[Rule],
    source_site: pywikibot.Site,
    target_site: pywikibot.Site,
    src_cat_no_ns: str,
    tgt_cat_no_ns: str,
    dry_run: bool,
    verbose: bool,
    depth: int,
    visited: Set[str],
) -> bool:
    if depth <= 0:
        return False

    src_cat = cat_obj(source_site, src_cat_no_ns)
    try:
        if not src_cat.exists():
            return False
    except Exception:
        return False

    tgt_cat = cat_obj(target_site, tgt_cat_no_ns)

    supercat_pairs = compute_target_supercats(cfg, rules, source_site, target_site, src_cat, verbose)

    ensured_links: List[str] = []
    for tgt_sc, link in supercat_pairs:
        sc_key = tgt_sc.title(with_ns=True)
        if sc_key in visited:
            continue

        try:
            if tgt_sc.exists():
                ensured_links.append(link)
                continue
        except Exception:
            pass

        created_parent = False
        for src_parent in src_cat.categories():
            src_parent_no_ns = normalize_no_ns_title(source_site, src_parent.title(with_ns=False))

            mapped = None
            for r in rules:
                parsed = try_parse_rule_match_from_title(cfg, r, source_site, target_site, src_parent_no_ns)
                if not parsed:
                    continue
                _, tv = parsed
                mapped = cat_obj(target_site, render(r.tgt_pat, tv))
                break

            wd_map = get_target_category_from_source_category(src_parent, target_site, cfg.target_lang)

            match = False
            if mapped is not None and mapped.title(with_ns=True) == tgt_sc.title(with_ns=True):
                match = True
            if wd_map is not None and wd_map.title(with_ns=True) == tgt_sc.title(with_ns=True):
                match = True

            if not match:
                continue

            if not has_any_linked_member_quick(cfg, src_parent, target_site, verbose):
                continue

            visited.add(sc_key)
            created_parent = ensure_target_category_recursive(
                cfg, rules,
                source_site, target_site,
                src_parent_no_ns,
                tgt_sc.title(with_ns=False),
                dry_run, verbose,
                depth=depth - 1,
                visited=visited,
            )
            break

        try:
            if tgt_sc.exists():
                ensured_links.append(link)
        except Exception:
            pass

        if created_parent and verbose:
            pywikibot.output(f"[SUPERCAT-CREATED] {tgt_sc.title(with_ns=True)}")

    existed = False
    try:
        existed = tgt_cat.exists()
    except Exception:
        existed = False

    if not existed:
        text = build_target_category_text(cfg, normalize_no_ns_title(target_site, tgt_cat_no_ns), ensured_links)

        if verbose:
            pywikibot.output(f"[CREATE] {tgt_cat.title(with_ns=True)} supercats={len(ensured_links)}")

        if not dry_run:
            tgt_cat.text = text
            tgt_cat.save(summary=cfg.save_summary_create)
            try:
                _ = tgt_cat.get()
            except Exception:
                pass
    else:
        add_missing_supercats_to_existing_catpage(
            target_cat=tgt_cat,
            supercat_links=ensured_links,
            summary=cfg.save_summary_create,
            dry_run=dry_run,
            verbose=verbose,
        )

    return True


def add_category_simple(
    page: pywikibot.Page,
    category: pywikibot.Category,
    summary: str,
    dry_run: bool,
    verbose: bool
) -> bool:
    try:
        if not page.exists():
            return False

        text = page.get()

        cat_title = category.title(with_ns=True)
        cat_prefix = f"[[{cat_title}"
        cat_link = f"[[{cat_title}]]"

        # Exists already? Accept variants with sortkey / whitespace:
        #   [[Category:Foo]]
        #   [[Category:Foo|B]]
        #   [[Category:Foo | B]]
        if cat_prefix in text:
            return False

        new_text = text.rstrip() + "\n\n" + cat_link + "\n"

        if verbose:
            pywikibot.output(f"[ADD] {page.title()} += {cat_link}")

        if not dry_run:
            page.text = new_text
            page.save(summary=summary)

        return True

    except Exception as e:
        if verbose:
            pywikibot.output(f"[ADD-ERR] {page.title()} -> {type(e).__name__}: {e}")
        return False



def add_category_to_all_linked_members(
    cfg: Config,
    source_site: pywikibot.Site,
    target_site: pywikibot.Site,
    src_cat_no_ns: str,
    tgt_cat_no_ns: str,
    dry_run: bool,
    verbose: bool,
) -> int:
    src_cat = cat_obj(source_site, src_cat_no_ns)
    tgt_cat = cat_obj(target_site, tgt_cat_no_ns)

    try:
        if not src_cat.exists() or not tgt_cat.exists():
            return 0
    except Exception:
        return 0

    limit = None if cfg.add_to_target_pages_limit == 0 else cfg.add_to_target_pages_limit

    added = 0
    for sp in src_cat.members(recurse=False, total=limit):
        if not should_add_category_to_namespace(sp.namespace()):
            continue

        tp = get_target_page_from_source(sp, target_site, cfg.target_lang, verbose=verbose)
        if tp is None:
            continue

        if add_category_simple(tp, tgt_cat, cfg.save_summary_add_cat, dry_run, verbose):
            added += 1

    if verbose:
        pywikibot.output(f"[ADD-DONE] added={added} for {tgt_cat.title(with_ns=True)}")

    return added


# ---------------------------
# Main (same CLI)
# ---------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("number", type=int, help="Config number (MediaWiki JSON page on target wiki)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--max-create", type=int, default=0)
    ap.add_argument("--max-scan", type=int, default=0)
    args, _ = ap.parse_known_args()
    print("loading default site")
    boot_site = pywikibot.Site()
    print("loaded default site")
    #exit(0)
    print("load json configs")
    cfg = load_config_from_wiki(boot_site, args.number)

    source_site = pywikibot.Site(cfg.source_lang, "wikipedia")
    target_site = pywikibot.Site(cfg.target_lang, "wikipedia")
    wikidata_site = pywikibot.Site("wikidata", "wikidata")

    source_site.login()
    target_site.login()
    wikidata_site.login()

    source_site.throttle.maxdelay = 1
    target_site.throttle.maxdelay = 1
    wikidata_site.throttle.maxdelay = 1

    rules = build_rules(cfg)

    scanned = 0
    created = 0

    for rule in rules:
        if args.verbose:
            pywikibot.output(f"\n[RULE] {rule.src_pat} ==> {rule.tgt_pat}")

        for src_cat_title_no_ns in iter_source_categories_for_rule(cfg, rule, source_site, args.verbose):
            scanned += 1
            if args.max_scan and scanned > args.max_scan:
                return 0

            src_cat_title_no_ns = normalize_no_ns_title(source_site, src_cat_title_no_ns)
            src_cat = cat_obj(source_site, src_cat_title_no_ns)

            try:
                if not src_cat.exists():
                    continue
            except Exception:
                continue

            parsed = try_parse_rule_match_from_title(cfg, rule, source_site, target_site, src_cat_title_no_ns)
            if not parsed:
                continue

            _, tgt_vals = parsed
            tgt_raw = sanitize_title_for_site(target_site, render(rule.tgt_pat, tgt_vals))
            tgt_cat_no_ns = normalize_no_ns_title(target_site, tgt_raw)
            tgt_cat = cat_obj(target_site, tgt_cat_no_ns)

            existed_before = False
            try:
                existed_before = tgt_cat.exists()
            except Exception:
                existed_before = False

            if not has_any_linked_member_quick(cfg, src_cat, target_site, args.verbose):
                if args.verbose:
                    pywikibot.output(f"[SKIP] no linked members in first {cfg.scan_members_limit} for {src_cat.title(with_ns=True)} (total members: {len(list(src_cat.members()))})")
                continue

            visited: Set[str] = set()
            visited.add(tgt_cat.title(with_ns=True))

            ok = ensure_target_category_recursive(
                cfg=cfg,
                rules=rules,
                source_site=source_site,
                target_site=target_site,
                src_cat_no_ns=src_cat_title_no_ns,
                tgt_cat_no_ns=tgt_cat_no_ns,
                dry_run=args.dry_run,
                verbose=args.verbose,
                depth=2,
                visited=visited,
            )
            if not ok:
                continue

            if not args.dry_run:
                interlink_categories(cfg, source_site, target_site, src_cat_title_no_ns, tgt_cat_no_ns, args.verbose)

            add_category_to_all_linked_members(
                cfg=cfg,
                source_site=source_site,
                target_site=target_site,
                src_cat_no_ns=src_cat_title_no_ns,
                tgt_cat_no_ns=tgt_cat_no_ns,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )

            if not existed_before:
                created += 1
                if args.verbose:
                    pywikibot.output(f"[CREATED] {tgt_cat.title(with_ns=True)} (count={created})")
                if args.max_create and created >= args.max_create:
                    return 0

            if cfg.throttle_sleep:
                time.sleep(cfg.throttle_sleep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
